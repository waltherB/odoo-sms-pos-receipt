# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_sms_receipt = fields.Boolean(
        string="Enable SMS Receipts",
        default=False,
        help="If checked, cashiers will see an option to send receipts "
             "via SMS in this Point of Sale."
    )

    sms_gateway_id = fields.Many2one(
        'iap.account',
        string="SMS Gateway Account",
        domain=[('service_name', '=', 'sms')],
        help="Select the SMS gateway account to use for sending receipts. "
             "Choose from configured SMS gateway accounts by name. "
             "If not set, the default SMS gateway will be used."
    )

    def _get_fields_for_pos_config(self):
        """
        Returns the list of fields of pos.config that needs to be loaded
        by the POS UI.
        """
        fields = super()._get_fields_for_pos_config()
        fields.extend(['enable_sms_receipt', 'sms_gateway_id'])
        return fields

    @api.model
    def setup_sms_account_names(self):
        """Set up proper names for SMS accounts to show in dropdown."""
        return self.env['iap.account'].setup_default_sms_account_names()
