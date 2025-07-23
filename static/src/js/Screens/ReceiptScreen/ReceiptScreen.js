/* @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
        this.popup = useService("popup");
        this.orm = useService("orm");
    },

    get currentOrder() {
        return this.pos.get_order();
    },

    get smsPhoneNumber() {
        return this.currentOrder?.get_phone_for_sms_receipt() || "";
    },

    set smsPhoneNumber(value) {
        this.currentOrder?.set_phone_for_sms_receipt(value);
    },

    async sendSmsReceipt() {
        const order = this.currentOrder;
        const phone = this.smsPhoneNumber;

        if (!order) {
            this.popup.add(ErrorPopup, {
                title: this.env._t("Order Not Found"),
                body: this.env._t("Cannot send SMS receipt, current order not available."),
            });
            return;
        }

        if (!phone || !phone.trim()) {
            this.popup.add(ErrorPopup, {
                title: this.env._t("Missing Phone Number"),
                body: this.env._t("Please enter a valid phone number to send the SMS receipt."),
            });
            return;
        }

        // Basic phone validation
        const phoneRegex = /^[+]?[\d\s\-\(\)]{7,}$/;
        if (!phoneRegex.test(phone)) {
            this.popup.add(ErrorPopup, {
                title: this.env._t("Invalid Phone Number"),
                body: this.env._t("The entered phone number format is not valid."),
            });
            return;
        }

        try {
            const result = await this.orm.call(
                'pos.order',
                'action_send_sms_receipt_rpc',
                [order.backendId, phone]
            );

            if (result === true) {
                this.notification.add(
                    this.env._t("SMS receipt sent successfully to %s.", phone),
                    { type: 'success' }
                );
                order.is_sms_receipt_sent = true;
            } else if (result && result.error) {
                this.popup.add(ErrorPopup, {
                    title: this.env._t("SMS Sending Failed"),
                    body: this.env._t(result.error),
                });
            } else {
                this.popup.add(ErrorPopup, {
                    title: this.env._t("SMS Sending Failed"),
                    body: this.env._t("An unknown error occurred while sending the SMS."),
                });
            }

        } catch (error) {
            console.error("Error sending SMS receipt:", error);
            let errorMessage = this.env._t("Could not connect to the server or an unexpected error occurred.");
            
            if (error.data && error.data.message) {
                errorMessage = error.data.message;
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            this.popup.add(ErrorPopup, {
                title: this.env._t("SMS Sending Error"),
                body: errorMessage,
            });
        }
    },

    get shouldShowSmsFeature() {
        // Always show for testing - remove this later
        console.log('SMS Feature Check:', {
            pos: !!this.pos,
            config: !!this.pos?.config,
            enable_sms_receipt: this.pos?.config?.enable_sms_receipt
        });
        return true; // Force show for debugging
        // return this.pos?.config?.enable_sms_receipt;
    }
});
