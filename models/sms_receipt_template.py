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
                     kr 0,00""",
        help="Available variables: {total}, {payment_method}, {amount}"
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
        help="Available variables: {website_line}, {unique_code}, {order_name}, {order_datetime}"
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
                preview += record.total_template.format(
                    total="75.00",
                    payment_method="Bank/MobilePay",
                    amount="75.00"
                ) + "\n"
            
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
            # Create default template if none exists
            template = self.create({
                'name': 'Default SMS Receipt',
                'company_id': company_id
            })
        
        return template