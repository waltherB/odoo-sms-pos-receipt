# -*- coding: utf-8 -*-
from . import models

def post_init_hook(env):
    """Create default SMS receipt templates after module installation."""
    # Delete any problematic existing templates
    problematic = env['sms.receipt.template'].search([('name', '=', 'Default SMS Receipt')])
    if problematic:
        problematic.unlink()
    
    # Check if good templates already exist
    existing_templates = env['sms.receipt.template'].search([
        ('name', 'in', ['Complete SMS Receipt Template', 'Minimal SMS Receipt'])
    ])
    
    if not existing_templates:
        # Create default templates with proper change variable
        env['sms.receipt.template'].create([
            {
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
            },
            {
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
                'total_template': 'Total: {total} kr ({payment_method})\nChange: {change} kr',
                'show_tax': False,
                'show_customer': True,
                'customer_template': 'Kunde: {customer_name}',
                'show_footer': True,
                'footer_template': 'Tak for dit køb! {website_line}\n{ticket_code_line}\nRef: {unique_code}'
            }
        ])
from . import controllers