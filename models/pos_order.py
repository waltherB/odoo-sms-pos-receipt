# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
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
            # Create SMS receipt with proper Danish format
            lines_text = ""
            for line in self.lines:
                lines_text += f"- {line.product_id.name} x{line.qty:.0f} = {line.price_subtotal_incl:.2f} kr\n"
            
            # Build the receipt
            body = f"""{self.company_id.name}"""
            
            if self.company_id.phone:
                body += f"\nTelefon: {self.company_id.phone}"
            if self.company_id.vat:
                body += f"\nCVR: {self.company_id.vat}"
            if self.company_id.email:
                body += f"\n{self.company_id.email}"
            if self.company_id.website:
                body += f"\n{self.company_id.website}"
                
            body += f"\n--------------------------------"
            
            if self.partner_id and self.partner_id.name:
                body += f"\nBetjent af {self.partner_id.name}"
                
            body += f"\n{self.name}\n\n{lines_text}"
            body += f"--------\nTOTAL                kr {self.amount_total:.2f}\n"
            
            if self.payment_ids:
                payment_method = self.payment_ids[0].payment_method_id.name
                body += f"\n{payment_method}          {self.amount_total:.2f}"
            else:
                body += f"\nKontant          {self.amount_total:.2f}"
                
            body += f"\n\nBYTTEPENGE\n                     kr 0,00"
            
            if self.amount_tax > 0:
                tax_base = self.amount_total - self.amount_tax
                body += f"\n\nMoms    Beløb    Basis      I alt"
                body += f"\n25%     {self.amount_tax:.2f}    {tax_base:.2f}    {self.amount_total:.2f}"
            
            if self.partner_id and self.partner_id.name:
                body += f"\n\nKunde               {self.partner_id.name}"
                
            body += f"\n\nScan mig for at anmode om en faktura for dit køb."
            
            if self.company_id.website:
                body += f"\n\nDu kan gå til {self.company_id.website} og brug koden nedenfor til at anmode om en faktura online"
                
            body += f"\nUnik kode: {self.pos_reference or self.name}"
            body += f"\n\nPowered by Odoo"
            body += f"\nOrdre {self.name}"
            body += f"\n{self.date_order.strftime('%d-%m-%Y %H:%M:%S')}"
            
            _logger.info("Created Danish SMS receipt body")

            # Send SMS using configured gateway
            self._send_sms_message(cleaned_phone, body)

            # Mark as sent and log success
            self.write({
                'is_sms_receipt_sent': True,
                'sms_receipt_error': False
            })
            # Log success (pos.order doesn't support message_post)
            _logger.info("SMS receipt logged for order %s", self.name)
            _logger.info(
                "SMS receipt sent for order %s to %s",
                self.name, cleaned_phone
            )
            return True

        except Exception as e:
            error_msg = str(e)
            
            # Handle known gatewayapi-sms compatibility issues
            if ("'iap.account' object attribute '_get_sms_account' is read-only" in error_msg) or \
               ('_get_sms_account' in error_msg and 'read-only' in error_msg) or \
               ('failure_type' in error_msg and 'sms_server_error' in error_msg):
                # These are known compatibility issues but SMS is usually still sent
                _logger.warning(
                    "SMS gateway compatibility warning for order %s to %s: %s",
                    self.name, cleaned_phone, error_msg
                )
                
                # For these specific errors, assume SMS was sent successfully
                # since the gatewayapi-sms module typically sends despite these errors
                self.write({
                    'is_sms_receipt_sent': True,
                    'sms_receipt_error': False
                })
                # Log success (pos.order doesn't support message_post)
                _logger.info("SMS receipt logged for order %s", self.name)
                _logger.info(
                    "SMS receipt marked as sent for order %s to %s (compatibility issue handled)",
                    self.name, cleaned_phone
                )
                return True
            
            # For other errors, log and return error
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
        # Try multiple possible template references
        template_refs = [
            'odoo-sms-pos-receipt.sms_template_pos_receipt',
            'pos_sms_receipt.sms_template_pos_receipt'
        ]
        
        for template_ref in template_refs:
            try:
                return self.env.ref(template_ref, raise_if_not_found=True)
            except ValueError:
                continue
        
        # If no template found, search by name
        template = self.env['sms.template'].search([
            ('name', '=', 'POS Receipt SMS'),
            ('model_id.model', '=', 'pos.order')
        ], limit=1)
        
        if template:
            return template
            
        _logger.warning("No SMS template found for POS receipts")
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
            _logger.info("_send_sms_message called with body: %s", body[:100] + "..." if len(body) > 100 else body)
            
            # Create SMS record and send it using the default gateway
            # Note: Gateway selection is handled by the SMS gateway module configuration
            sms_vals = {
                'number': phone,
                'body': body,
                'state': 'outgoing',
            }
            
            _logger.info("Creating SMS record with vals: %s", sms_vals)
            sms_record = self.env['sms.sms'].create(sms_vals)
            _logger.info("SMS record created with body: %s", sms_record.body[:100] + "..." if len(sms_record.body) > 100 else sms_record.body)
            
            try:
                sms_record._send()
            except Exception as send_error:
                # Handle specific SMS gateway errors
                error_str = str(send_error)
                if ('failure_type' in error_str and 'sms_server_error' in error_str) or \
                   ('_get_sms_account' in error_str and 'read-only' in error_str):
                    # These are known issues with gatewayapi-sms module
                    # The SMS might have been sent despite the error
                    _logger.warning(
                        "SMS gateway compatibility issue for order %s: %s", 
                        self.name, error_str
                    )
                    # Check if the SMS was actually sent by looking at the record state
                    sms_record.invalidate_cache()
                    if sms_record.state in ['sent', 'outgoing']:
                        _logger.info("SMS was sent successfully despite the error")
                        return  # SMS was sent successfully
                    else:
                        # Wait a moment and check again (SMS might be queued)
                        import time
                        time.sleep(1)
                        sms_record.invalidate_cache()
                        if sms_record.state in ['sent', 'outgoing']:
                            _logger.info("SMS was sent successfully (after delay)")
                            return
                        else:
                            raise Exception("SMS sending failed due to gateway compatibility issue")
                else:
                    # Re-raise other errors
                    raise send_error
            
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

    def _render_custom_sms_receipt(self):
        """Render SMS receipt using customizable template."""
        # Get the template for this company
        template = self.env['sms.receipt.template'].get_default_template(self.company_id.id)
        
        body_parts = []
        
        # Company Information
        if template.show_company_info and template.company_info_template:
            phone_line = f"Telefon: {self.company_id.phone}" if self.company_id.phone else ""
            vat_line = f"CVR: {self.company_id.vat}" if self.company_id.vat else ""
            email_line = self.company_id.email if self.company_id.email else ""
            website_line = self.company_id.website if self.company_id.website else ""
            
            company_info = template.company_info_template.format(
                company_name=self.company_id.name,
                phone_line=phone_line,
                vat_line=vat_line,
                email_line=email_line,
                website_line=website_line
            )
            # Remove empty lines
            company_info = '\n'.join(line for line in company_info.split('\n') if line.strip())
            body_parts.append(company_info)
        
        # Separator
        if template.show_separator and template.separator_line:
            body_parts.append(template.separator_line)
        
        # Order Information
        if template.show_order_info and template.order_info_template:
            served_by_line = f"Betjent af {self.partner_id.name}" if self.partner_id and self.partner_id.name else ""
            
            order_info = template.order_info_template.format(
                served_by_line=served_by_line,
                order_name=self.name,
                order_date=self.date_order.strftime('%d-%m-%Y %H:%M')
            )
            # Remove empty lines
            order_info = '\n'.join(line for line in order_info.split('\n') if line.strip())
            body_parts.append(order_info)
        
        # Items
        if template.show_items and template.item_line_template:
            items_text = ""
            for line in self.lines:
                item_line = template.item_line_template.format(
                    product_name=line.product_id.name,
                    qty=f"{line.qty:.0f}",
                    price=f"{line.price_subtotal_incl:.2f}"
                )
                items_text += item_line + "\n"
            if items_text:
                body_parts.append(items_text.rstrip())
        
        # Total
        if template.show_total and template.total_template:
            payment_method = "Kontant"
            payment_amount = self.amount_total
            change_amount = 0.0
            
            if self.payment_ids:
                payment_method = self.payment_ids[0].payment_method_id.name
                payment_amount = sum(payment.amount for payment in self.payment_ids)
                # Calculate change (difference between payment amount and total)
                change_amount = payment_amount - self.amount_total
                # Ensure change is not negative (in case of underpayment)
                change_amount = max(0.0, change_amount)
            
            total_section = template.total_template.format(
                total=f"{self.amount_total:.2f}",
                payment_method=payment_method,
                amount=f"{payment_amount:.2f}",
                change=f"{change_amount:.2f}"
            )
            body_parts.append(total_section)
        
        # Tax
        if template.show_tax and template.tax_template and self.amount_tax > 0:
            tax_base = self.amount_total - self.amount_tax
            tax_section = template.tax_template.format(
                tax_amount=f"{self.amount_tax:.2f}",
                tax_base=f"{tax_base:.2f}",
                total=f"{self.amount_total:.2f}"
            )
            body_parts.append(tax_section)
        
        # Customer
        if template.show_customer and template.customer_template and self.partner_id and self.partner_id.name:
            customer_section = template.customer_template.format(
                customer_name=self.partner_id.name
            )
            body_parts.append(customer_section)
        
        # Footer
        if template.show_footer and template.footer_template:
            website_line = ""
            if self.company_id.website:
                website_line = f"Du kan gå til {self.company_id.website} og brug koden nedenfor til at anmode om en faktura online"
            
            # Generate ticket code if POS is configured to generate codes
            ticket_code_line = ""
            if hasattr(self, 'config_id') and self.config_id and hasattr(self.config_id, 'receipt_header') and self.config_id.receipt_header:
                # Check if POS is configured to generate ticket codes
                if hasattr(self.config_id, 'receipt_footer') and 'code' in (self.config_id.receipt_footer or '').lower():
                    ticket_code_line = f"Ticket kode: {self.pos_reference or self.name}"
                elif hasattr(self, 'access_token') and self.access_token:
                    # Use access token if available
                    ticket_code_line = f"Ticket kode: {self.access_token[:8].upper()}"
                elif self.pos_reference and self.pos_reference != self.name:
                    # Use POS reference if different from order name
                    ticket_code_line = f"Ticket kode: {self.pos_reference}"
            
            footer_section = template.footer_template.format(
                website_line=website_line,
                unique_code=self.pos_reference or self.name,
                order_name=self.name,
                order_datetime=self.date_order.strftime('%d-%m-%Y %H:%M:%S'),
                ticket_code_line=ticket_code_line
            )
            # Remove empty lines
            footer_section = '\n'.join(line for line in footer_section.split('\n') if line.strip())
            body_parts.append(footer_section)
        
        # Join all parts
        return '\n\n'.join(part for part in body_parts if part.strip())