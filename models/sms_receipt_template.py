# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SmsReceiptTemplate(models.Model):
    _name = 'sms.receipt.template'
    _description = 'SMS Receipt Template'
    _rec_name = 'name'

    name = fields.Char(
        string="Template Name",
        required=True,
        default="Default SMS Receipt"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company,
        required=True
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
        help="Available variables: {company_name}, {phone_line}, {vat_line}, {email_line}, {website_line}"
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
        help="Available variables: {served_by_line}, {order_name}, {order_date}"
    )
    
    show_items = fields.Boolean(
        string="Show Order Items",
        default=True
    )
    
    item_line_template = fields.Char(
        string="Item Line Template",
        default="- {product_name} x{qty} = {price} kr",
        help="Available variables: {product_name}, {qty}, {price}"
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
        help="Available variables: {total}, {payment_method}, {amount}, {change}"
    )
    
    show_tax = fields.Boolean(
        string="Show Tax Information",
        default=True
    )
    
    tax_template = fields.Text(
        string="Tax Section Template",
        default="""Moms    Beløb    Basis      I alt
25%     {tax_amount}    {tax_base}    {total}""",
        help="Available variables: {tax_amount}, {tax_base}, {total}"
    )
    
    show_customer = fields.Boolean(
        string="Show Customer Information",
        default=True
    )
    
    customer_template = fields.Char(
        string="Customer Template",
        default="Kunde               {customer_name}",
        help="Available variables: {customer_name}"
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
        help="Available variables: {website_line}, {unique_code}, {order_name}, {order_datetime}, {ticket_code_line}"
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
                    order_datetime="29-07-2025 08:30:15",
                    ticket_code_line="Ticket kode: ABC123 (hvis aktiveret i POS)"
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
        """Create default SMS receipt templates."""
        # Check if templates already exist
        existing = self.search([('name', 'in', ['Complete SMS Receipt Template', 'Minimal SMS Receipt'])])
        if existing:
            return existing
        
        # Create complete template
        complete_template = self.create({
            'name': 'Complete SMS Receipt Template',
            'active': True,
            'show_company_info': True,
            'company_info_template': '{company_name}\n{phone_line}\n{vat_line}\n{email_line}\n{website_line}',
            'show_separator': True,
            'separator_line': '--------------------------------',
            'show_order_info': True,
            'order_info_template': '{served_by_line}\nOrdre: {order_name}\nDato: {order_date}',
            'show_items': True,
            'item_line_template': '{qty}x {product_name} = {price} kr',
            'show_total': True,
            'total_template': '--------\nTOTAL                kr {total}\n\n{payment_method}          {amount}\n\nBYTTEPENGE\n                     kr {change}',
            'show_tax': True,
            'tax_template': 'Moms    Beløb    Basis      I alt\n25%     {tax_amount} kr  {tax_base} kr  {total} kr',
            'show_customer': True,
            'customer_template': 'Kunde: {customer_name}',
            'show_footer': True,
            'footer_template': 'Tak for dit køb!\n\n{website_line}\n\n{ticket_code_line}\n\nUnik kode: {unique_code}\nOrdre: {order_name}\n{order_datetime}'
        })
        
        # Create minimal template
        minimal_template = self.create({
            'name': 'Minimal SMS Receipt',
            'active': True,
            'show_company_info': True,
            'company_info_template': '{company_name}',
            'show_separator': False,
            'show_order_info': True,
            'order_info_template': 'Ordre: {order_name} - {order_date}',
            'show_items': True,
            'item_line_template': '{qty}x {product_name} {price}kr',
            'show_total': True,
            'total_template': 'Total: {total} kr ({payment_method})',
            'show_tax': False,
            'show_customer': True,
            'customer_template': 'Kunde: {customer_name}',
            'show_footer': True,
            'footer_template': 'Tak for dit køb! {website_line}\n{ticket_code_line}\nRef: {unique_code}'
        })
        
        return complete_template + minimal_template

    @api.model
    def get_default_template(self, company_id=None):
        """Get the default SMS receipt template for a company."""
        if not company_id:
            company_id = self.env.company.id
            
        template = self.search([
            ('company_id', '=', company_id),
            ('active', '=', True)
        ], limit=1)
        
        if not template:
            # Try to find any active template for any company
            template = self.search([('active', '=', True)], limit=1)
            
        if not template:
            # Create default templates if none exist
            templates = self.create_default_templates()
            template = templates[0] if templates else None
            
        if not template:
            # Last resort: create a simple template
            template = self.create({
                'name': 'Default SMS Receipt',
                'company_id': company_id
            })
        
        return template