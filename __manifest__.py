# -*- coding: utf-8 -*-
{
    'name': 'POS SMS Receipt',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Allows sending POS receipts via SMS from the Point of Sale receipt screen.',
    'description': """
This module extends the Point of Sale interface to allow cashiers
to send receipts to customers via SMS, in addition to email or printing.

Key Features:
- Option on POS receipt screen to send receipt via SMS.
- Input field for phone number, pre-filled from customer record if available.
- Configurable per POS to enable/disable SMS receipt functionality (via POS settings).
- Uses a customizable SMS template (found under Technical > SMS Templates) for the receipt content.
- Tracks if an SMS receipt has been sent for an order and displays this information on the order backend form.
- Allows resending SMS receipt from the order backend form.
    """,
    'author': 'Jules AI Agent',
    'website': '', # Consider adding a link to where this code might be hosted or discussed
    'depends': [
        'point_of_sale',
        'sms',  # Standard Odoo SMS module, provides sms.template and sms.api
    ],
    'data': [
        'data/sms_template_data.xml',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
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
