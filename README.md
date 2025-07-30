# POS SMS Receipt Module for Odoo 17

Send POS receipts via SMS with customizable Danish-formatted templates and dynamic change calculation.

## 📱 Features

### Core Functionality
- **SMS Receipt Sending** - Send receipts directly from POS interface
- **Customizable Templates** - Create and manage SMS receipt templates
- **Danish Formatting** - Professional Danish receipt formatting with proper currency and tax display
- **Dynamic Change Calculation** - Automatic calculation of change amount for cash payments
- **Multi-Gateway Support** - Compatible with various SMS gateways (GatewayAPI, etc.)
- **POS Integration** - Seamless integration with Odoo 17 Point of Sale

### Template Features
- **Variable System** - Use `{variable_name}` format for dynamic content
- **Modular Sections** - Enable/disable company info, items, totals, tax, customer info, footer
- **Live Preview** - See exactly how your SMS will look before sending
- **Multi-Company Support** - Different templates per company
- **Active/Inactive Management** - Easy template activation/deactivation with visual indicators

### Advanced Features
- **Ticket Code Integration** - Supports POS "Generate a code on ticket" feature
- **Error Handling** - Robust error handling for production environments
- **Offline Support** - Works with offline POS systems
- **Permission Management** - Proper access control for different user groups

## 🚀 Installation

### Prerequisites
- Odoo 17
- SMS gateway module (e.g., `gatewayapi-sms`)
- Point of Sale module

### Installation Steps
1. **Download** the module to your Odoo addons directory
2. **Update Apps List** in Odoo
3. **Install** the "POS SMS Receipt" module
4. **Configure** SMS gateway settings
5. **Set up** POS configurations

## ⚙️ Configuration

### 1. SMS Gateway Setup
Configure your SMS gateway in **Settings → Technical → SMS**:
- Set up SMS gateway credentials
- Test SMS sending functionality
- Configure default SMS gateway

### 2. POS Configuration
Navigate to **Point of Sale → Configuration → Point of Sale**:
- Enable SMS receipts for desired POS configurations
- Select SMS gateway for each POS
- Configure receipt settings

### 3. SMS Receipt Templates
Access **Point of Sale → SMS Receipt Templates**:

#### Creating Templates
1. **Click "Create"** to add new template
2. **Configure sections** using the tabbed interface:
   - **Company Information** - Business details, contact info
   - **Order Information** - Order details, cashier info
   - **Items & Total** - Product lines and payment totals
   - **Tax & Customer** - Tax breakdown and customer details
   - **Footer** - Thank you message, website, codes
   - **Preview** - Live preview of SMS format

#### Available Variables
Use these variables in your templates:

**Company Variables:**
- `{company_name}` - Your company name
- `{phone_line}` - Phone number (if set)
- `{vat_line}` - VAT/CVR number (if set)
- `{email_line}` - Company email (if set)
- `{website_line}` - Company website (if set)

**Order Variables:**
- `{served_by_line}` - Cashier/user who served
- `{order_name}` - Order reference number
- `{order_date}` - Order date and time
- `{order_datetime}` - Full order date and time

**Item Variables:**
- `{product_name}` - Product name
- `{qty}` - Quantity purchased
- `{price}` - Line total price

**Payment Variables:**
- `{total}` - Order total amount
- `{payment_method}` - Payment method used
- `{amount}` - Payment amount received
- `{change}` - Change amount (amount - total)

**Tax Variables:**
- `{tax_amount}` - Total tax amount
- `{tax_base}` - Tax base amount (subtotal)

**Customer Variables:**
- `{customer_name}` - Customer name (if available)

**Footer Variables:**
- `{unique_code}` - Unique order identifier
- `{ticket_code_line}` - POS ticket code (if enabled)

#### Template Examples

**Complete Template:**
```
{company_name}
{phone_line}
{vat_line}
--------------------------------
{served_by_line}
Ordre: {order_name}
Dato: {order_date}

{qty}x {product_name} = {price} kr

--------
TOTAL                kr {total}

{payment_method}          {amount}

BYTTEPENGE
                     kr {change}

Moms    Beløb    Basis      I alt
25%     {tax_amount} kr  {tax_base} kr  {total} kr

Kunde: {customer_name}

Tak for dit køb!
{website_line}
{ticket_code_line}
Unik kode: {unique_code}
```

**Minimal Template:**
```
{company_name}
Ordre: {order_name} - {order_date}
{qty}x {product_name} {price}kr
Total: {total} kr ({payment_method})
Change: {change} kr
Kunde: {customer_name}
Tak for dit køb! {website_line}
{ticket_code_line}
Ref: {unique_code}
```

## 📱 Usage

### Sending SMS Receipts from POS
1. **Complete a sale** in the POS interface
2. **Click "SMS Receipt"** button on receipt screen
3. **Enter customer phone number** (or use existing customer data)
4. **Click "Send SMS"** to deliver receipt

### Managing Templates
1. **Navigate** to Point of Sale → SMS Receipt Templates
2. **Use filters** to view Active, Inactive, or All templates
3. **Create/Edit** templates using the form interface
4. **Preview** templates before saving
5. **Activate/Deactivate** templates as needed

### Backend SMS Sending
From **Point of Sale → Orders**:
1. **Open an order** record
2. **Click "Send SMS Receipt"** button
3. **SMS sent** using configured template

## 🔧 Technical Details

### File Structure
```
odoo-sms-pos-receipt/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── pos_order.py          # POS order SMS functionality
│   ├── pos_config.py         # POS configuration
│   ├── sms_receipt_template.py # Template model
│   └── iap_account.py        # Gateway account display
├── views/
│   ├── pos_config_views.xml  # POS configuration views
│   ├── pos_order_views.xml   # Order management views
│   └── sms_receipt_template_views.xml # Template management
├── static/src/
│   ├── js/Screens/ReceiptScreen/
│   │   └── ReceiptScreen.js  # Frontend SMS functionality
│   └── xml/Screens/ReceiptScreen/
│       └── ReceiptScreen.xml # UI integration
├── security/
│   ├── ir.model.access.csv   # Basic access rights
│   └── sms_receipt_template_access.xml # Template permissions
└── data/
    ├── sms_template_data.xml # Legacy SMS templates
    ├── sms_receipt_template_data.xml # Default templates
    └── setup_sms_accounts.xml # Gateway setup
```

### Dependencies
- `point_of_sale` - Core POS functionality
- `sms` - SMS sending capabilities
- `iap` - Gateway integration

### Permissions
- **POS Managers** - Full access to templates and configuration
- **POS Users** - Can use SMS receipts and view templates
- **System Administrators** - Full system access

## 🐛 Troubleshooting

### Common Issues

**SMS Not Sending:**
- Check SMS gateway configuration
- Verify phone number format
- Check SMS gateway credits/balance
- Review error logs in Settings → Technical → Logging

**Template Not Appearing:**
- Ensure template is active
- Check company assignment
- Verify user permissions
- Use "All" filter to see inactive templates

**Variables Not Working:**
- Check variable spelling and format `{variable_name}`
- Ensure variables are supported in template section
- Review template preview for errors

**Menu Not Visible:**
- Check user group permissions
- Verify module installation
- Update module if needed

### Error Handling
The module includes robust error handling for:
- Gateway compatibility issues
- Network connectivity problems
- Invalid phone numbers
- Template rendering errors

## 📄 License

This module is licensed under LGPL-2.

## 🤝 Support

For support and bug reports, please contact the module maintainer or create an issue in the project repository.

## 🔄 Changelog

### Version 17.0.1.0.0
- Initial release for Odoo 17
- Complete SMS receipt functionality
- Danish formatting support
- Dynamic change calculation
- Customizable template system
- POS integration
- Multi-gateway support
- Production-ready error handling