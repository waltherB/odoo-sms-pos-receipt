# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import re

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    phone_for_sms_receipt = fields.Char(
        string="Phone for SMS Receipt",
        help="Phone number provided at POS for sending the receipt via SMS.",
        readonly=True,
        copy=False
    )
    is_sms_receipt_sent = fields.Boolean(
        string="SMS Receipt Sent",
        default=False,
        readonly=True,
        copy=False,
        help="Indicates if an SMS receipt has been sent for this order."
    )
    sms_receipt_error = fields.Text(
        string="SMS Receipt Error",
        readonly=True,
        copy=False,
        help="Error message if SMS sending failed."
    )

    @api.model
    def _order_fields(self, ui_order):
        """Map UI order fields to backend order fields."""
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        fields_return['phone_for_sms_receipt'] = ui_order.get(
            'phone_for_sms_receipt', False
        )
        return fields_return

    def action_send_sms_receipt_rpc(self, phone_number=None):
        """RPC method called from POS frontend to send SMS receipt."""
        return self.action_send_sms_receipt(phone_number)

    @api.model
    def create_from_ui_with_sms(self, orders, phone_number=None):
        """Create order from UI data and prepare for SMS sending."""
        # Ensure phone number is included in order data
        if phone_number and orders:
            for order_data in orders:
                if isinstance(order_data, dict):
                    order_data['phone_for_sms_receipt'] = phone_number
        
        # Use the standard create_from_ui method
        result = self.create_from_ui(orders)
        return result

    def action_send_sms_receipt(self, phone_number=None):
        """Send SMS receipt for the order."""
        self.ensure_one()

        if not phone_number and not self.phone_for_sms_receipt:
            raise UserError(_(
                "No phone number specified for the SMS receipt."
            ))

        target_phone = phone_number or self.phone_for_sms_receipt

        # Clean and validate phone number
        cleaned_phone = self._clean_phone_number(target_phone)
        if not cleaned_phone:
            error_msg = _("Invalid phone number format: %s") % target_phone
            self.write({'sms_receipt_error': error_msg})
            return {'error': error_msg}

        # Update phone number if different
        if phone_number and self.phone_for_sms_receipt != phone_number:
            self.write({'phone_for_sms_receipt': phone_number})

        try:
            # Get SMS template
            sms_template = self._get_sms_template()

            if sms_template:
                # Render template body
                body = self._render_sms_body(sms_template)
            else:
                # Fallback message
                body = self._get_fallback_sms_body()

            # Send SMS using configured gateway
            self._send_sms_message(cleaned_phone, body)

            # Mark as sent and log success
            self.write({
                'is_sms_receipt_sent': True,
                'sms_receipt_error': False
            })
            self.message_post(
                body=_("Receipt sent via SMS to %s.") % cleaned_phone
            )
            _logger.info(
                "SMS receipt sent for order %s to %s",
                self.name, cleaned_phone
            )
            return True

        except Exception as e:
            error_msg = str(e)
            self.write({'sms_receipt_error': error_msg})
            _logger.error(
                "Failed to send SMS receipt for order %s to %s: %s",
                self.name, cleaned_phone, error_msg
            )
            return {'error': error_msg}

    def _clean_phone_number(self, phone):
        """Clean and validate phone number."""
        if not phone:
            return False

        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)

        # Basic validation: should contain only digits and optional + at start
        if not re.match(r'^\+?[\d]{7,15}$', cleaned):
            return False

        return cleaned

    def _get_sms_template(self):
        """Get SMS template for POS receipt."""
        try:
            return self.env.ref(
                'pos_sms_receipt.sms_template_pos_receipt',
                raise_if_not_found=True
            )
        except ValueError:
            _logger.warning(
                "SMS template 'pos_sms_receipt.sms_template_pos_receipt' "
                "not found."
            )
            return False

    def _render_sms_body(self, template):
        """Render SMS template body."""
        # Render template
        body = template._render_field('body', [self.id])[self.id]

        # Convert HTML to plain text if needed
        body = self._html_to_text(body)

        return body.strip()

    def _html_to_text(self, html_content):
        """Convert HTML content to plain text."""
        if not html_content:
            return ''

        # Simple HTML to text conversion
        text = html_content
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p[^>]*>', '', text)
        text = re.sub(r'</p>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)

        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    def _get_fallback_sms_body(self):
        """Get fallback SMS body when template is not available."""
        return _(
            "Receipt for Order: %(order_name)s\n"
            "Total: %(total)s %(currency)s\n"
            "Thank you for your purchase!"
        ) % {
            'order_name': self.name,
            'total': self.amount_total,
            'currency': self.currency_id.symbol
        }

    def _send_sms_message(self, phone, body):
        """Send SMS message using configured gateway."""
        try:
            # Create SMS record and send it using the default gateway
            # Note: Gateway selection is handled by the SMS gateway module configuration
            sms_vals = {
                'number': phone,
                'body': body,
                'state': 'outgoing',
            }
            
            sms_record = self.env['sms.sms'].create(sms_vals)
            sms_record._send()
            
            # Check if sending was successful
            if sms_record.state == 'error':
                error_msg = sms_record.sms_api_error or sms_record.failure_type or 'Unknown SMS error'
                raise Exception(f"SMS sending failed: {error_msg}")
            elif sms_record.state not in ['sent', 'outgoing']:
                # Sometimes the state might be something else, log it for debugging
                _logger.warning(
                    "SMS state after sending: %s for order %s", 
                    sms_record.state, self.name
                )
                
        except Exception as e:
            _logger.error("Failed to send SMS for order %s: %s", self.name, str(e))
            raise

    def button_send_sms_receipt_backend(self):
        """Backend button to send/resend SMS receipt."""
        self.ensure_one()

        phone_to_use = (
            self.phone_for_sms_receipt or
            (self.partner_id.mobile if self.partner_id else None) or
            (self.partner_id.phone if self.partner_id else None)
        )

        if not phone_to_use:
            raise UserError(_(
                "No phone number found on the order or linked customer."
            ))

        result = self.action_send_sms_receipt(phone_number=phone_to_use)

        if isinstance(result, dict) and result.get('error'):
            raise UserError(_("Failed to send SMS: %s") % result['error'])

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SMS Sent'),
                'message': _('SMS receipt sent successfully to %s') % phone_to_use,
                'type': 'success',
            }
        }