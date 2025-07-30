# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SmsReceiptTemplate(models.Model):
    _name = 'sms.receipt.template'
    _description = 'SMS Receipt Template'
    _rec_name = 'name'

    name = fields.Char(
        string="Template Name",
        required=True,
        default="Default SMS Receipt",
        translate=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company,
        required=True
    )
    
    language = fields.Selection(
        selection=[
            ('da_DK', 'Danish'),
            ('en_US', 'English'),
            ('de_DE', 'German'),
            ('fr_FR', 'French'),
            ('es_ES', 'Spanish'),
            ('nl_NL', 'Dutch'),
            ('sv_SE', 'Swedish'),
            ('no_NO', 'Norwegian'),
        ],
        string="Language",
        default='da_DK',
        required=True,
        help="Language for this SMS template"
    )
    
    active = fields.Boolean(
        string="Active",
        default=True
    )
    
    # Template sections - each can be enabled/disabled and customized
    show_company_info = fields.Boolean(
        string="Show Company Information",
        default=True
    )
    
    company_info_template = fields.Text(
        string="Company Info Template",
        default="""{company_name}
{phone_line}
{vat_line}
{email_line}
{website_line}""",
        help="Available variables: {company_name}, {phone_line}, {vat_line}, {email_line}, {website_line}",
        translate=True
    )
    
    show_separator = fields.Boolean(
        string="Show Separator Line",
        default=True
    )
    
    separator_line = fields.Char(
        string="Separator Line",
        default="--------------------------------"
    )
    
    show_order_info = fields.Boolean(
        string="Show Order Information",
        default=True
    )
    
    order_info_template = fields.Text(
        string="Order Info Template",
        default="""{served_by_line}
{order_name}""",
        help="Available variables: {served_by_line}, {order_name}, {order_date}",
        translate=True
    )
    
    show_items = fields.Boolean(
        string="Show Order Items",
        default=True
    )
    
    item_line_template = fields.Char(
        string="Item Line Template",
        default="- {product_name} x{qty} = {price} kr",
        help="Available variables: {product_name}, {qty}, {price}",
        translate=True
    )
    
    show_total = fields.Boolean(
        string="Show Total",
        default=True
    )
    
    total_template = fields.Text(
        string="Total Section Template",
        default="""--------
TOTAL                kr {total}

{payment_method}          {amount}

BYTTEPENGE
                     kr {change}""",
        help="Available variables: {total}, {payment_method}, {amount}, {change}",
        translate=True
    )
    
    show_tax = fields.Boolean(
        string="Show Tax Information",
        default=True
    )
    
    tax_template = fields.Text(
        string="Tax Section Template",
        default="""Moms    Beløb    Basis      I alt
25%     {tax_amount}    {tax_base}    {total}""",
        help="Available variables: {tax_amount}, {tax_base}, {total}",
        translate=True
    )
    
    show_customer = fields.Boolean(
        string="Show Customer Information",
        default=True
    )
    
    customer_template = fields.Char(
        string="Customer Template",
        default="Kunde               {customer_name}",
        help="Available variables: {customer_name}",
        translate=True
    )
    
    show_footer = fields.Boolean(
        string="Show Footer",
        default=True
    )
    
    footer_template = fields.Text(
        string="Footer Template",
        default="""Scan mig for at anmode om en faktura for dit køb.

{website_line}
Unik kode: {unique_code}

Powered by Odoo
Ordre {order_name}
{order_datetime}""",
        help="Available variables: {website_line}, {unique_code}, {order_name}, {order_datetime}",
        translate=True
    )
    
    # Preview functionality
    preview_text = fields.Text(
        string="Preview",
        compute="_compute_preview",
        help="Preview of how the SMS receipt will look"
    )
    
    @api.depends('company_info_template', 'order_info_template', 'item_line_template', 
                 'total_template', 'tax_template', 'customer_template', 'footer_template',
                 'show_company_info', 'show_order_info', 'show_items', 'show_total', 
                 'show_tax', 'show_customer', 'show_footer', 'separator_line')
    def _compute_preview(self):
        """Generate a preview of the SMS receipt template."""
        for record in self:
            preview = ""
            
            if record.show_company_info and record.company_info_template:
                preview += record.company_info_template.format(
                    company_name="Your Company Name",
                    phone_line="Telefon: +45 12 34 56 78",
                    vat_line="CVR: 12345678",
                    email_line="info@company.dk",
                    website_line="https://company.dk"
                ) + "\n"
            
            if record.show_separator and record.separator_line:
                preview += record.separator_line + "\n"
            
            if record.show_order_info and record.order_info_template:
                preview += record.order_info_template.format(
                    served_by_line="Betjent af John Doe",
                    order_name="Shop/001",
                    order_date="29-07-2025 08:30"
                ) + "\n\n"
            
            if record.show_items and record.item_line_template:
                preview += record.item_line_template.format(
                    product_name="Product 1",
                    qty="2",
                    price="50.00"
                ) + "\n"
                preview += record.item_line_template.format(
                    product_name="Product 2",
                    qty="1",
                    price="25.00"
                ) + "\n"
            
            if record.show_total and record.total_template:
                # Create a safe template formatting function
                template_vars = {
                    'total': "75.00",
                    'payment_method': "Kontant",
                    'amount': "80.00",
                    'change': "5.00"
                }
                
                try:
                    # Try to format with all variables
                    total_preview = record.total_template
                    for var, value in template_vars.items():
                        total_preview = total_preview.replace('{' + var + '}', str(value))
                    preview += total_preview + "\n"
                except Exception:
                    # Ultimate fallback - just show the template as-is
                    preview += record.total_template + "\n"
            
            if record.show_tax and record.tax_template:
                preview += record.tax_template.format(
                    tax_amount="15.00",
                    tax_base="60.00",
                    total="75.00"
                ) + "\n"
            
            if record.show_customer and record.customer_template:
                preview += record.customer_template.format(
                    customer_name="Jane Smith"
                ) + "\n"
            
            if record.show_footer and record.footer_template:
                preview += "\n" + record.footer_template.format(
                    website_line="Du kan gå til https://company.dk og brug koden nedenfor",
                    unique_code="Shop/001",
                    order_name="Shop/001",
                    order_datetime="29-07-2025 08:30:15"
                )
            
            record.preview_text = preview
    
    def action_preview(self):
        """Force recompute of preview."""
        self._compute_preview()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Preview Updated'),
                'message': _('The SMS preview has been refreshed with current template settings.'),
                'type': 'success',
            }
        }
    
    def fix_change_variable(self):
        """Fix templates that have hardcoded change amounts."""
        for record in self:
            if record.total_template and 'kr 0,00' in record.total_template:
                # Replace hardcoded change with variable
                record.total_template = record.total_template.replace('kr 0,00', 'kr {change}')
        return True
    
    @api.model
    def create_default_templates(self):
        """Create default SMS receipt templates for different languages."""
        templates = self.env['sms.receipt.template']
        
        # Define templates for different languages
        language_templates = {
            'da_DK': {
                'complete_name': 'Komplet SMS Kvittering',
                'minimal_name': 'Minimal SMS Kvittering',
                'order_prefix': 'Ordre:',
                'date_prefix': 'Dato:',
                'customer_prefix': 'Kunde:',
                'total_label': 'TOTAL',
                'change_label': 'BYTTEPENGE',
                'tax_header': 'Moms    Beløb    Basis      I alt',
                'thank_you': 'Tak for dit køb!',
                'unique_code': 'Unik kode:',
                'currency': 'kr'
            },
            'en_US': {
                'complete_name': 'Complete SMS Receipt',
                'minimal_name': 'Minimal SMS Receipt',
                'order_prefix': 'Order:',
                'date_prefix': 'Date:',
                'customer_prefix': 'Customer:',
                'total_label': 'TOTAL',
                'change_label': 'CHANGE',
                'tax_header': 'Tax     Amount   Base       Total',
                'thank_you': 'Thank you for your purchase!',
                'unique_code': 'Unique code:',
                'currency': '$'
            },
            'de_DE': {
                'complete_name': 'Vollständige SMS-Quittung',
                'minimal_name': 'Minimale SMS-Quittung',
                'order_prefix': 'Bestellung:',
                'date_prefix': 'Datum:',
                'customer_prefix': 'Kunde:',
                'total_label': 'GESAMT',
                'change_label': 'WECHSELGELD',
                'tax_header': 'MwSt    Betrag   Basis      Gesamt',
                'thank_you': 'Vielen Dank für Ihren Einkauf!',
                'unique_code': 'Eindeutiger Code:',
                'currency': '€'
            }
        }
        
        # Create templates for each language
        for lang_code, lang_data in language_templates.items():
            # Check if templates already exist for this language
            existing = self.search([
                ('language', '=', lang_code),
                ('name', 'in', [lang_data['complete_name'], lang_data['minimal_name']])
            ])
            if existing:
                templates += existing
                continue
                
            # Create complete template
            complete_template = self.create({
                'name': lang_data['complete_name'],
                'language': lang_code,
                'active': True,
                'show_company_info': True,
                'company_info_template': '{company_name}\n{phone_line}\n{vat_line}\n{email_line}\n{website_line}',
                'show_separator': True,
                'separator_line': '--------------------------------',
                'show_order_info': True,
                'order_info_template': f'{{served_by_line}}\n{lang_data["order_prefix"]} {{order_name}}\n{lang_data["date_prefix"]} {{order_date}}',
                'show_items': True,
                'item_line_template': f'{{qty}}x {{product_name}} = {{price}} {lang_data["currency"]}',
                'show_total': True,
                'total_template': f'--------\n{lang_data["total_label"]}                {lang_data["currency"]} {{total}}\n\n{{payment_method}}          {{amount}}\n\n{lang_data["change_label"]}\n                     {lang_data["currency"]} {{change}}',
                'show_tax': True,
                'tax_template': f'{lang_data["tax_header"]}\n25%     {{tax_amount}} {lang_data["currency"]}  {{tax_base}} {lang_data["currency"]}  {{total}} {lang_data["currency"]}',
                'show_customer': True,
                'customer_template': f'{lang_data["customer_prefix"]} {{customer_name}}',
                'show_footer': True,
                'footer_template': f'{lang_data["thank_you"]}\n\n{{website_line}}\n\n{lang_data["unique_code"]} {{unique_code}}\n{lang_data["order_prefix"]} {{order_name}}\n{{order_datetime}}'
            })
            templates += complete_template
            
            # Create minimal template
            minimal_template = self.create({
                'name': lang_data['minimal_name'],
                'language': lang_code,
                'active': True,
                'show_company_info': True,
                'company_info_template': '{company_name}',
                'show_separator': False,
                'show_order_info': True,
                'order_info_template': f'{lang_data["order_prefix"]} {{order_name}} - {{order_date}}',
                'show_items': True,
                'item_line_template': f'{{qty}}x {{product_name}} {{price}}{lang_data["currency"]}',
                'show_total': True,
                'total_template': f'Total: {{total}} {lang_data["currency"]} ({{payment_method}})\n{lang_data["change_label"]}: {{change}} {lang_data["currency"]}',
                'show_tax': False,
                'show_customer': True,
                'customer_template': f'{lang_data["customer_prefix"]} {{customer_name}}',
                'show_footer': True,
                'footer_template': f'{lang_data["thank_you"]} {{website_line}}\nRef: {{unique_code}}'
            })
            templates += minimal_template
        
        return templates

    @api.model
    def get_default_template(self, company_id=None, language=None):
        """Get the default SMS receipt template for a company and language."""
        if not company_id:
            company_id = self.env.company.id
        
        if not language:
            language = self.env.context.get('lang', 'da_DK')
            
        # First try to find template for specific company and language
        template = self.search([
            ('company_id', '=', company_id),
            ('language', '=', language),
            ('active', '=', True)
        ], limit=1)
        
        if not template:
            # Try to find template for company with any language
            template = self.search([
                ('company_id', '=', company_id),
                ('active', '=', True)
            ], limit=1)
            
        if not template:
            # Try to find template for specific language with any company
            template = self.search([
                ('language', '=', language),
                ('active', '=', True)
            ], limit=1)
            
        if not template:
            # Try to find any active template
            template = self.search([('active', '=', True)], limit=1)
            
        if not template:
            # Create default templates if none exist
            templates = self.create_default_templates()
            template = templates[0] if templates else None
            
        if not template:
            # Last resort: create a simple template
            template = self.create({
                'name': _('Default SMS Receipt'),
                'company_id': company_id,
                'language': language
            })
        
        return template