# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class PosSmsReceiptController(http.Controller):

    @http.route('/pos_sms_receipt/send_sms', type='json', auth='user')
    def send_sms_receipt(self, order_id, phone_number):
        """
        Controller method to send SMS receipt from POS
        """
        try:
            order = request.env['pos.order'].browse(order_id)
            if not order.exists():
                return {'error': 'Order not found'}
            
            result = order.action_send_sms_receipt(phone_number)
            return {'success': True, 'result': result}
            
        except Exception as e:
            _logger.error("Error in SMS controller: %s", str(e))
            return {'error': str(e)}

    @http.route('/pos_sms_receipt/test', type='http', auth='public')
    def test_controller(self):
        """
        Test controller to verify module is working
        """
        return """
        <html>
        <head><title>POS SMS Receipt Test</title></head>
        <body>
            <h1>🚀 POS SMS Receipt Module is Working!</h1>
            <p>If you see this page, the module is properly installed.</p>
            <script>
                console.log('🎯 POS SMS Receipt controller loaded successfully!');
                alert('POS SMS Receipt Module Test - Controller Working!');
            </script>
        </body>
        </html>
        """