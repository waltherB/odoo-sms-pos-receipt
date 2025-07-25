# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class IapAccount(models.Model):
    _inherit = 'iap.account'



    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Override name_search to show proper account names for SMS accounts."""
        # Get the default result first
        result = super(IapAccount, self).name_search(name, args, operator, limit)
        
        # If we're searching for SMS accounts, override the display names
        if args:
            domain_has_sms = any('service_name' in str(arg) and 'sms' in str(arg) for arg in args if isinstance(arg, (list, tuple)))
            if domain_has_sms:
                new_result = []
                for record_id, display_name in result:
                    record = self.browse(record_id)
                    if record.service_name == 'sms' and record.name and record.name.strip():
                        # Use the account name instead of generic 'sms'
                        new_result.append((record_id, record.name))
                    else:
                        new_result.append((record_id, display_name))
                return new_result
        
        return result

    @api.model
    def setup_default_sms_account_names(self):
        """Helper method to set up proper names for SMS accounts."""
        sms_accounts = self.search([('service_name', '=', 'sms')])
        
        for account in sms_accounts:
            if not account.name or account.name == 'sms':
                new_name = None
                
                if hasattr(account, 'gatewayapi_base_url') and account.gatewayapi_base_url:
                    base_url = account.gatewayapi_base_url.replace('https://', '').replace('http://', '')
                    if hasattr(account, 'gatewayapi_sender') and account.gatewayapi_sender:
                        new_name = f"{account.gatewayapi_sender} - GatewayAPI"
                    else:
                        new_name = f"GatewayAPI ({base_url})"
                elif hasattr(account, 'provider') and account.provider:
                    provider_name = account.provider.replace('sms_api_', '').replace('_', ' ').title()
                    new_name = f"SMS Gateway - {provider_name}"
                else:
                    new_name = f"SMS Gateway {account.id}"
                
                if new_name:
                    account.write({'name': new_name})
                    _logger.info(f"Updated SMS account {account.id} name to: {new_name}")
        
        return True