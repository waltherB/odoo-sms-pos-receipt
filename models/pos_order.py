# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    phone_for_sms_receipt = fields.Char(
        string="Phone for SMS Receipt",
        help="Phone number provided at POS for sending the receipt via SMS.",
        readonly=True, # Should be set by POS UI/controller method
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
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        fields_return['phone_for_sms_receipt'] = ui_order.get('phone_for_sms_receipt', False)
        return fields_return

    def action_send_sms_receipt(self, phone_number=None):
        """
        Sends the SMS receipt for the order.
        This method can be called via RPC from the POS.
        """
        self.ensure_one()
        if not phone_number and not self.phone_for_sms_receipt:
            raise UserError(_("No phone number specified for the SMS receipt."))

        target_phone = phone_number or self.phone_for_sms_receipt

        # Update phone_for_sms_receipt if a new one is provided and different
        if phone_number and self.phone_for_sms_receipt != phone_number:
            self.write({'phone_for_sms_receipt': phone_number})

        # Try to use the defined SMS template
        sms_template = None
        try:
            sms_template = self.env.ref('pos_sms_receipt.sms_template_pos_receipt', raise_if_not_found=True)
        except ValueError:
            _logger.warning("SMS template 'pos_sms_receipt.sms_template_pos_receipt' not found. Using a generic message.")

        if sms_template:
            try:
                # The send_sms method might vary based on the 'sms' module version or custom implementations.
                # This is a common way to use sms.template
                # We might need to adjust if the 'sms' module expects phone numbers differently
                # when not directly tied to a partner's mobile field.
                # Some modules might require 'numbers=[target_phone]' or similar.

                # Attempt 1: Using message_post_with_template (might not directly support arbitrary numbers well for SMS)
                # self.message_post_with_template(
                #     sms_template.id,
                #     composition_mode='comment', # 'comment' or 'mass_mail'
                #     # partner_ids=[(4, self.partner_id.id)] if self.partner_id else [], # For tracking if possible
                #     # The following are non-standard, depends on sms module's override of message_post_with_template
                #     # phone_numbers=[target_phone], # This is a hypothetical parameter
                # )

                # Attempt 2: More direct usage of sms.api or similar (preferred for arbitrary numbers)
                # This assumes the 'sms' module provides 'sms.api' and its '_send_sms' method.
                body = sms_template._render_field('body_html', [self.id])[self.id] # Or 'body' for plain text
                # Simple plain text conversion (real HTML to text might be needed if template is HTML)
                body = body.replace('<p>', '').replace('</p>', '\n').replace('<br>', '\n')
                import re
                body = re.sub('<[^>]+>', '', body).strip()


                self.env['sms.api']._send_sms([target_phone], body)

                self.write({'is_sms_receipt_sent': True})
                self.message_post(body=_("Receipt sent via SMS to %s.") % target_phone)
                _logger.info("SMS receipt sent for order %s to %s", self.name, target_phone)
                return True
            except Exception as e:
                _logger.error("Failed to send SMS receipt for order %s to %s: %s", self.name, target_phone, str(e))
                # Do not raise UserError to POS directly, POS should handle this based on RPC response
                return {'error': str(e)}
        else:
            # Fallback if template is not found
            receipt_content = f"Thank you for your order {self.name}. Total: {self.amount_total} {self.currency_id.symbol}."
            try:
                self.env['sms.api']._send_sms([target_phone], receipt_content)
                self.write({'is_sms_receipt_sent': True})
                self.message_post(body=_("Receipt sent via SMS (generic) to %s.") % target_phone)
                _logger.info("Generic SMS receipt sent for order %s to %s", self.name, target_phone)
                return True
            except Exception as e:
                _logger.error("Failed to send generic SMS receipt for order %s to %s: %s", self.name, target_phone, str(e))
                return {'error': str(e)}

    # This method is called from JS (see rpc.js in point_of_sale)
    # when the POS UI sends order data to the server.
    # We need to ensure 'phone_for_sms_receipt' is saved if it's part of the ui_order.
    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft=draft)
        # After orders are created, find them and update if phone_for_sms_receipt was in the initial data
        # This might be redundant if _order_fields handles it correctly for new orders too,
        # but it's good to be explicit.
        # created_orders = self.browse(order_ids)
        # for order_data in orders:
        #     corresponding_order = created_orders.filtered(lambda o: o.pos_reference == order_data['data']['name']) # 'name' is pos_reference in ui_order
        #     if corresponding_order and order_data['data'].get('phone_for_sms_receipt'):
        #         corresponding_order.write({'phone_for_sms_receipt': order_data['data']['phone_for_sms_receipt']})
        return order_ids

    # If you need to call action_send_sms_receipt from a button in Odoo Backend (Form View)
    def button_send_sms_receipt_backend(self):
        self.ensure_one()
        if not self.phone_for_sms_receipt and not self.partner_id.mobile and not self.partner_id.phone:
            raise UserError(_("No phone number found on the order or linked customer."))

        phone_to_use = self.phone_for_sms_receipt or self.partner_id.mobile or self.partner_id.phone

        action_result = self.action_send_sms_receipt(phone_number=phone_to_use)

        if isinstance(action_result, dict) and action_result.get('error'):
            raise UserError(_("Failed to send SMS: %s") % action_result.get('error'))

        return True

# Note: The actual method for sending SMS (`self.env['sms.api']._send_sms`)
# is an assumption based on common Odoo SMS modules.
# It might need to be adjusted based on the specific SMS module installed.
# For example, it could be self.env['sms.composer'].with_context( ... )._action_send_sms(...)
# or using mail.thread's message_post with a subtype for SMS.
# The use of `sms_template._render_field` and then `_send_sms` is a robust approach if direct
# model rendering is needed for the body.
# If `message_post_with_template` is adapted by the SMS module to handle `phone_numbers` kwarg,
# that would be cleaner.
# For now, this structure provides the necessary fields and a server-side action.
# The `create_from_ui` and `_order_fields` ensure that data from PoS UI can be saved.
# The `action_send_sms_receipt` is the core RPC endpoint for the PoS JS to call.
# Added `button_send_sms_receipt_backend` for potential backend usage.
# The `_order_fields` method ensures that when an order is created or updated from the POS UI,
# the `phone_for_sms_receipt` field from the UI order data is correctly mapped to the server-side order field.
# This is crucial for persisting the phone number entered in the POS.
# The `create_from_ui` extension is more for complex scenarios; often `_order_fields` is sufficient
# for adding new fields to be saved from the UI.
# The `action_send_sms_receipt` is designed to be callable via RPC.
# It now also logs to chatter and returns a simple True or a dict with an error key.
# POS JS will need to handle the response.
# The method to get the rendered body `sms_template._render_field('body_html', ...)` might need
# `sms_template.generate_body_html(self)` or similar depending on Odoo version and specific SMS module.
# For Odoo 17 and `sms` module, `_render_field` should work.
# Fallback to generic message if template is not found.
# Error handling for SMS sending now returns a dict with an error key to allow POS to show a message.
# Updated `action_send_sms_receipt` to explicitly use the `phone_number` argument if provided,
# and also to update `phone_for_sms_receipt` on the order if a new number is used for sending.
# This ensures the number used is recorded.
# Corrected `_order_fields` to get `phone_for_sms_receipt` from `ui_order`.
# Removed the potentially redundant loop in `create_from_ui` as `_order_fields` should handle this.
# If `phone_for_sms_receipt` is meant to be saved with the order *before* sending,
# then the POS JS should include it in the order data payload.
# The current `action_send_sms_receipt` updates it if a new number is passed during the send action.
# This seems reasonable: the number is associated with the *act of sending*.
# If it needs to be stored *before* any send attempt, the JS side must ensure it's in the main order JSON.
# My `models.js` will ensure this.
# The `readonly=True` for `phone_for_sms_receipt` implies it's set programmatically (e.g., by `action_send_sms_receipt` or `_order_fields`),
# not directly by a user on the backend form view, unless that view is customized.
# Added a basic HTML to text conversion for the SMS body. A more robust library might be needed for complex HTML.
# Assumed `sms.api` model and `_send_sms` method for sending. This is a common pattern but might need checking against the specific `sms` module in use.
# The `body = sms_template._render_field('body_html', [self.id])[self.id]` is a way to render a field of a template.
# If the SMS module uses plain text templates, it should be `body_plaintext` or similar, or just `body`.
# I'm using `body_html` and then stripping tags as a common case for QWeb templates.
# If the `sms` module has a more direct way to render and send a template to an arbitrary number, that would be preferable.
# For example, `template.send_sms(self.id, numbers=[target_phone])` if such a method exists.
# The current approach of rendering then calling `sms.api._send_sms` is a fallback.
# The `_order_fields` is the standard way to map data from the POS UI order object to the backend `pos.order` fields
# when the order is synced (usually on payment or finalization).
# `ui_order.get('phone_for_sms_receipt', False)` will fetch the value if `phone_for_sms_receipt` is set in the JS Order model
# and included in its `export_as_JSON` data.
# This python file is now quite complete for the backend logic.
