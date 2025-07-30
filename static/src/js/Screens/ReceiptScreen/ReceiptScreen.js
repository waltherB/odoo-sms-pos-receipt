/* @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";



patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        
        // Always initialize services (we'll check config later)
        this.notification = useService("notification");
        this.popup = useService("popup");
        this.orm = useService("orm");
        
        // Initialize SMS phone number safely
        this.initializeSmsPhone();
    },

    initializeSmsPhone() {
        // Initialize SMS phone number if not already set
        if (!this.orderUiState.inputSmsPhone) {
            const partner = this.currentOrder?.get_partner();
            this.orderUiState.inputSmsPhone = (partner && (partner.mobile || partner.phone)) || "";
        }
        
        // Initialize SMS states
        if (this.orderUiState.smsSuccessful === undefined) {
            this.orderUiState.isSmsSending = false;
            this.orderUiState.smsSuccessful = null;
            this.orderUiState.smsNotice = "";
        }
    },

    get isSmsEnabled() {
        return this.pos && this.pos.config && this.pos.config.enable_sms_receipt;
    },

    get smsPhoneFromPartner() {
        if (!this.currentOrder) return "";
        const partner = this.currentOrder.get_partner();
        return (partner && (partner.mobile || partner.phone)) || "";
    },



    async sendSmsReceipt() {
        // Safety checks
        if (!this.isSmsEnabled) {
            return;
        }

        // Ensure SMS phone is initialized
        this.initializeSmsPhone();

        const order = this.currentOrder;
        const phone = this.orderUiState.inputSmsPhone;

        // Reset previous states
        this.orderUiState.smsSuccessful = null;
        this.orderUiState.smsNotice = "";

        if (!order) {
            this.orderUiState.smsSuccessful = false;
            this.orderUiState.smsNotice = _t("Cannot send SMS receipt, current order not available.");
            return;
        }

        if (!phone || !phone.trim()) {
            this.orderUiState.smsSuccessful = false;
            this.orderUiState.smsNotice = _t("Please enter a valid phone number to send the SMS receipt.");
            return;
        }

        // Basic phone validation
        const phoneRegex = /^[+]?[\d\s\-\(\)]{7,}$/;
        if (!phoneRegex.test(phone)) {
            this.orderUiState.smsSuccessful = false;
            this.orderUiState.smsNotice = _t("The entered phone number format is not valid.");
            return;
        }

        // Set loading state
        this.orderUiState.isSmsSending = true;

        try {
            let orderId = order.backendId || order.server_id || order.id;
            
            // If order doesn't exist in backend yet (offline mode), create it first
            if (!orderId) {
                // Check if we're online before attempting to create order
                if (!navigator.onLine) {
                    this.orderUiState.smsSuccessful = false;
                    this.orderUiState.smsNotice = _t("Cannot send SMS while offline. Please connect to internet and try again.");
                    return;
                }
                
                // Save the order to backend first
                try {
                    const orderData = order.export_as_JSON();
                    orderData.phone_for_sms_receipt = phone; // Add phone number to order data
                    
                    const createdOrder = await this.orm.call(
                        'pos.order',
                        'create_from_ui_with_sms',
                        [[orderData], phone]
                    );
                    
                    if (createdOrder && createdOrder.length > 0) {
                        orderId = createdOrder[0].id;
                        order.backendId = orderId; // Store for future reference
                    } else {
                        throw new Error("Failed to create order in backend");
                    }
                } catch (createError) {
                    this.orderUiState.smsSuccessful = false;
                    
                    // Check if it's a connection error
                    if (createError.message && createError.message.includes('network')) {
                        this.orderUiState.smsNotice = _t("Network error. Please check your connection and try again.");
                    } else {
                        this.orderUiState.smsNotice = _t("Failed to save order to backend for SMS sending.");
                    }
                    return;
                }
            }
            const result = await this.orm.call(
                'pos.order',
                'action_send_sms_receipt_rpc',
                [orderId, phone]
            );

            if (result === true) {
                this.orderUiState.smsSuccessful = true;
                this.orderUiState.smsNotice = _t("SMS receipt sent successfully to %s.", phone);
                order.is_sms_receipt_sent = true;
                // Store phone number in order for future reference
                order.phone_for_sms_receipt = phone;
            } else if (result && result.error) {
                this.orderUiState.smsSuccessful = false;
                this.orderUiState.smsNotice = _t("SMS Sending Failed: %s", result.error);
            } else {
                this.orderUiState.smsSuccessful = false;
                this.orderUiState.smsNotice = _t("An unknown error occurred while sending the SMS.");
            }

        } catch (error) {
            let errorMessage = _t("Could not connect to the server or an unexpected error occurred.");
            
            if (error.data && error.data.message) {
                errorMessage = error.data.message;
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            this.orderUiState.smsSuccessful = false;
            this.orderUiState.smsNotice = errorMessage;
        } finally {
            // Clear loading state
            this.orderUiState.isSmsSending = false;
        }
    },


});
