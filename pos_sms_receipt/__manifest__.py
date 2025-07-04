# -*- coding: utf-8 -*-
{
    'name': 'POS SMS Receipt (Odoo 18)',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale', # Updated category for Odoo 18+
    'summary': 'Allows sending POS receipts via SMS from the Point of Sale receipt screen.',
    'description': """
This module extends the Point of Sale interface for Odoo 18 to allow cashiers
to send receipts to customers via SMS, in addition to email or printing.

Key Features:
- Option on POS receipt screen to send receipt via SMS.
- Input field for phone number, pre-filled from customer record if available.
- Configurable per POS to enable/disable SMS receipt functionality (via POS settings).
- Uses a customizable SMS template (found under Technical > SMS Templates) for the receipt content.
- Tracks if an SMS receipt has been sent for an order and displays this information on the order backend form.
- Allows resending SMS receipt from the order backend form.
    """,
    'author': 'Jules AI Agent (for Odoo 18)',
    'website': '',
    'depends': [
        'point_of_sale',
        'sms',
    ],
    'data': [
        'data/sms_template_data.xml',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            # Assuming Odoo 18 POS JS files are typically within an 'app' subdirectory
            'pos_sms_receipt/static/src/app/store/models.js',
            'pos_sms_receipt/static/src/app/screens/receipt_screen/receipt_screen.js',
            # XML templates often mirror JS structure or are in a flatter 'xml' dir
            'pos_sms_receipt/static/src/xml/screens/receipt_screen/receipt_screen.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
