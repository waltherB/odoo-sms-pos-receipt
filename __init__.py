# -*- coding: utf-8 -*-
from . import models

def post_init_hook(env):
    """Create default SMS receipt templates after module installation."""
    # Delete any problematic existing templates
    problematic = env['sms.receipt.template'].search([('name', '=', 'Default SMS Receipt')])
    if problematic:
        problematic.unlink()
    
    # Create multi-language templates using the model method
    # This ensures all language-specific templates are created properly
    try:
        env['sms.receipt.template'].create_default_templates()
    except Exception as e:
        # If multi-language creation fails, create basic templates
        env.cr.rollback()
        existing_templates = env['sms.receipt.template'].search([])
        if not existing_templates:
            env['sms.receipt.template'].create([
                {
                    'name': 'Complete SMS Receipt Template',
                    'language': 'da_DK',
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
                    'footer_template': 'Tak for dit køb!\n\n{website_line}\n\nUnik kode: {unique_code}\nOrdre: {order_name}\n{order_datetime}'
                }
            ])
from . import controllers