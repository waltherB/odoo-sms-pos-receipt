# POS SMS Receipt Module

This module extends Odoo 17's Point of Sale to allow sending receipts via SMS.

## Features

- **SMS Receipt Option**: Add SMS sending capability to the POS receipt screen
- **Phone Number Input**: Automatic prefill from customer data with manual override
- **SMS Gateway Selection**: Choose specific SMS gateway per POS configuration
- **Customizable Templates**: Design text-only receipt templates in the backend
- **Status Tracking**: Track SMS sending status and errors
- **Backend Management**: Resend SMS receipts from backend order forms

## Configuration

### 1. Enable SMS Receipts
1. Go to **Point of Sale > Configuration > Point of Sale**
2. Select your POS configuration
3. Enable **SMS Receipts** option
4. Optionally select a specific **SMS Gateway** (if multiple IAP SMS accounts exist)

### 2. Customize SMS Template
1. Go to **Point of Sale > Configuration > SMS Receipt Template**
2. Modify the template using Odoo's template syntax
3. Available variables:
   - `${object.name}` - Order reference
   - `${object.date_order}` - Order date
   - `${object.partner_id.name}` - Customer name
   - `${object.amount_total}` - Total amount
   - `${object.currency_id.symbol}` - Currency symbol
   - Loop through order lines with `% for line in object.lines:`

## Usage

### In POS Interface
1. Complete a sale and proceed to the receipt screen
2. Enter customer's phone number (auto-filled if customer is selected)
3. Click **Send SMS Receipt**
4. SMS will be sent using the configured gateway

### In Backend
1. Go to **Point of Sale > Orders > Orders**
2. Open any completed order
3. Click **Send SMS Receipt** to send or resend the SMS

## Technical Details

### Dependencies
- `point_of_sale`
- `sms`
- `iap`

### Models Extended
- `pos.config`: Added SMS configuration fields
- `pos.order`: Added SMS tracking fields and methods

### Frontend Components
- Extended `ReceiptScreen` with SMS functionality
- Added phone number input and send button
- Integrated with existing POS workflow

## Installation

1. Copy this module to your Odoo addons directory
2. Update the app list
3. Install the "POS SMS Receipt" module
4. Configure your SMS gateway in Settings > Technical > IAP Account
5. Enable SMS receipts in your POS configuration

## Support

For issues or feature requests, please contact your system administrator.