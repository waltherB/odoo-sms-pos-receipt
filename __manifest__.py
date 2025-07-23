# -*- coding: utf-8 -*-
{
    'name': 'POS SMS Receipt',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Send POS receipts via SMS with customizable templates.',
    'description': """
POS SMS Receipt Module

This module extends the Point of Sale interface to allow cashiers
to send receipts to customers via SMS, in addition to email or printing.

Key Features:
- SMS receipt option on POS receipt screen
- Phone number input with customer auto-fill
- Configurable SMS gateway selection per POS
- Customizable SMS templates
- SMS sending status tracking
- Backend resend functionality
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'point_of_sale',
        'sms',
        'iap',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sms_template_data.xml',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
        'views/sms_template_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_sms_receipt/static/src/js/models.js',
            'pos_sms_receipt/static/src/js/Screens/ReceiptScreen/ReceiptScreen.js',
            'pos_sms_receipt/static/src/xml/Screens/ReceiptScreen/ReceiptScreen.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
