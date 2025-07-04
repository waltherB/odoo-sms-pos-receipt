# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import re # For basic HTML stripping

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    phone_for_sms_receipt = fields.Char(
        string="Phone for SMS Receipt",
        help="Phone number provided at POS for sending the receipt via SMS for this specific order.",
        readonly=True,
        copy=False
    )
    is_sms_receipt_sent = fields.Boolean(
        string="SMS Receipt Sent",
        default=False,
        readonly=True,
        copy=False,
        help="Indicates if an SMS receipt has been attempted for this order."
    )

    @api.model
    def _order_fields(self, ui_order):
        """
        Map fields from the POS UI order data to backend pos.order fields.
        """
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        if 'phone_for_sms_receipt' in ui_order:
            fields_return['phone_for_sms_receipt'] = ui_order.get('phone_for_sms_receipt')
        return fields_return

    @api.model
    def action_send_sms_receipt_rpc(self, order_id, phone_number=None):
        """
        RPC endpoint for the POS JS to call to send an SMS receipt.
        :param order_id: The ID of the pos.order. (integer)
        :param phone_number: Optional. The phone number to send to.
        :return: True on success, or a dictionary {'error': message} on failure.
        """
        order = self.browse(order_id) # order_id is expected to be an integer
        if not order.exists():
            _logger.error(f"action_send_sms_receipt_rpc: Order ID {order_id} not found.")
            return {'error': _('Order not found.')}

        _logger.info(f"action_send_sms_receipt_rpc called for order {order.name} (ID: {order_id}) with phone {phone_number}")

        target_phone = phone_number
        if not target_phone:
            target_phone = order.phone_for_sms_receipt
        if not target_phone and order.partner_id:
            target_phone = order.partner_id.mobile or order.partner_id.phone

        if not target_phone:
            _logger.warning(f"action_send_sms_receipt_rpc: No phone number for order {order.name}.")
            return {'error': _('No phone number provided or found on the order/customer.')}

        if phone_number and order.phone_for_sms_receipt != phone_number:
            order.write({'phone_for_sms_receipt': phone_number})
        elif not order.phone_for_sms_receipt and phone_number:
             order.write({'phone_for_sms_receipt': phone_number})

        sms_template = None
        try:
            sms_template = self.env.ref('pos_sms_receipt.sms_template_pos_receipt', raise_if_not_found=True)
        except ValueError:
            _logger.warning("SMS template 'pos_sms_receipt.sms_template_pos_receipt' not found.")

        message_body = ""
        if sms_template:
            try:
                rendered_vals = sms_template._render_template(sms_template.body, sms_template.model, [order.id])
                message_body = rendered_vals.get(order.id, "")
                if not message_body and sms_template.body:
                     message_body = self.env['mail.render.mixin']._render_template_qweb(sms_template.body, sms_template.model, [order.id])[order.id]
                if not message_body:
                    _logger.warning(f"SMS template '{sms_template.name}' produced no content for order {order.name}. Using generic message.")
                    message_body = f"Your order {order.pos_reference or order.name}: Total {order.amount_total} {order.currency_id.symbol}. Thank you."
            except Exception as render_err:
                _logger.error(f"Error rendering SMS template for order {order.name}: {str(render_err)}")
                message_body = f"Your order {order.pos_reference or order.name}: Total {order.amount_total} {order.currency_id.symbol}. Thank you. (Template render error)"
        else:
            message_body = f"Your order {order.pos_reference or order.name}: Total {order.amount_total} {order.currency_id.symbol}. Thank you. (SMS Template missing)"

        message_body = re.sub(r'<br\s*/?>', '\n', message_body, flags=re.IGNORECASE)
        message_body = re.sub(r'<[^>]+>', '', message_body)
        message_body = re.sub(r'(\s*\n\s*)+', '\n', message_body).strip()

        if not message_body:
            _logger.error(f"Empty SMS body for order {order.name} after all processing.")
            return {'error': _('Failed to generate SMS content.')}

        try:
            sms_api_model = self.env.get('sms.api')
            if sms_api_model is None or not hasattr(sms_api_model, '_send_sms'):
                _logger.error("SMS sending mechanism (e.g., model 'sms.api' with method '_send_sms') not found for order %s.", order.name)
                return {'error': _('SMS sending service not available or misconfigured.')}

            # Pass record_id and model_name if your sms.api._send_sms supports it for tracking
            sms_api_model._send_sms([target_phone], message_body, model_name=self._name, record_id=order.id)

            order.write({'is_sms_receipt_sent': True})
            order.message_post(body=_("Receipt sent via SMS to %s.") % target_phone, subtype_xmlid='mail.mt_note')
            _logger.info("SMS receipt sent for order %s to %s", order.name, target_phone)
            return True
        except UserError as ue:
            _logger.error("UserError sending SMS for order %s to %s: %s", order.name, target_phone, str(ue))
            return {'error': str(ue)}
        except Exception as e:
            _logger.error("Generic error sending SMS for order %s to %s: %s", order.name, target_phone, str(e))
            return {'error': _('An unexpected error occurred while sending the SMS.')}

    def button_send_sms_receipt_backend(self):
        self.ensure_one()
        phone_to_use = self.phone_for_sms_receipt
        if not phone_to_use and self.partner_id:
            phone_to_use = self.partner_id.mobile or self.partner_id.phone

        if not phone_to_use:
            raise UserError(_("No phone number found on the order (dedicated SMS field) or on the linked customer (Mobile/Phone fields)."))

        action_result = self.action_send_sms_receipt_rpc(order_id=self.id, phone_number=phone_to_use)

        if isinstance(action_result, dict) and action_result.get('error'):
            raise UserError(_("Failed to send SMS: %s") % action_result.get('error'))
        return True
