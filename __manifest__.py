# -*- coding: utf-8 -*-
{
    'name': 'POS SMS Receipt',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    "license": "AGPL-3",
    'summary': 'Send POS receipts via SMS with customizable templates.',
    'description': """
POS SMS Receipt Module

This module extends the Point of Sale interface to allow cashiers
to send receipts to customers via SMS, providing a modern alternative
to email or printing receipts.

Key Features:
- SMS receipt option on POS receipt screen
- Phone number input with customer auto-fill
- Configurable SMS gateway selection per POS
- Customizable multi-language SMS templates
- Template management with live preview
- Multi-language support (English, Danish, German)
- Dynamic change calculation for cash payments
- SMS sending status tracking and error handling
- Backend resend functionality
- Offline POS support
- Professional receipt formatting
- Template variable system for dynamic content
- Permission-based access control
    """,
    'author': 'Walther Barnett',
    'website': 'https://github.com/waltherB/odoo-sms-pos-receipt',
    'depends': [
        'point_of_sale',
        'sms',
        'iap',
    ],
    'external_dependencies': {
        'python': [],
    },
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'security/sms_receipt_template_access.xml',
        'data/sms_template_data.xml',
        'data/sms_receipt_template_data.xml',
        'data/setup_sms_accounts.xml',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
        'views/sms_template_views.xml',
        'views/sms_receipt_template_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'odoo-sms-pos-receipt/static/src/js/Screens/ReceiptScreen/ReceiptScreen.js',
            'odoo-sms-pos-receipt/static/src/xml/Screens/ReceiptScreen/ReceiptScreen.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
