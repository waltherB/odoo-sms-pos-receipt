# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_sms_receipt = fields.Boolean(
        string="Enable SMS Receipts",
        default=True,
        help="If checked, cashiers will see an option to send receipts "
             "via SMS in this Point of Sale."
    )

    sms_gateway_id = fields.Many2one(
        'iap.account',
        string="SMS Gateway",
        domain=[('service_name', '=', 'sms')],
        help="Select the SMS gateway to use for sending receipts. "
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
