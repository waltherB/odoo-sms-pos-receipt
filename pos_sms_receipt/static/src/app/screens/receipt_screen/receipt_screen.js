/* @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { useState, onMounted } from "@odoo/owl"; // Owl's useState
import { _t } from "@web/core/l10n/translation"; // Ensure _t is available

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        // Standard services
        this.notification = useService("notification");
        this.popup = useService("popup");
        // this.orm = useService("orm"); // In Odoo 18, this.pos.data.call is often used instead of direct orm service in components like this.
                                        // However, orm service is still valid if preferred. Let's stick to this.pos.data.call for consistency with base Odoo 18 ReceiptScreen.

        // Odoo 18 ReceiptScreen uses its own 'state' for email/phone.
        // We'll add our SMS phone number to this state, initializing from the order model.
        // The order model (Order.js patch) should already try to prefill from partner.
        const currentOrder = this.pos.get_order();
        const initialSmsPhone = currentOrder?.get_phone_for_sms_receipt() || // Check order model first
                                currentOrder?.get_partner()?.mobile ||    // Then partner mobile
                                currentOrder?.get_partner()?.phone ||     // Then partner phone
                                "";

        // If this.state is already an owl state object, we add a new property.
        // If not (e.g. if base class doesn't make this.state an owl state), we might need to initialize it.
        // From Odoo 18's ReceiptScreen.js, `this.state = useState({ email: ..., phone: ...})` is done.
        // So, we should patch to add our field to that existing state.
        // This requires careful patching if the base `setup` initializes `this.state`.
        // A common way is to ensure our value is part of the initial useState call or update it right after.

        // Let's assume this.state is already a reactive object (useState) from the base class.
        // We will add our property to it. If not, this might need adjustment.
        // A safer way is to use a separate useState for our specific fields if unsure about base this.state.
        // However, to keep it grouped like the base 'email' and 'phone':
        if (this.state) { // Check if this.state exists from super.setup()
            this.state.sms_phone_for_receipt = initialSmsPhone;
        } else {
            // This case should ideally not happen if the base class initializes this.state with useState.
            // If it does, it means a significant change in base ReceiptScreen.
            // For now, let's log a warning if this.state is not found.
            console.warn("ReceiptScreen this.state not found during setup for SMS feature. SMS phone input might not be reactive.");
            // And try to create it, though this could conflict if base class sets it later.
            // this.sms_phone_for_receipt_local = useState({ value: initialSmsPhone }); // Alternative if this.state is tricky
        }

        // It's better to ensure this.state is patched correctly.
        // The base Odoo 18 ReceiptScreen does: this.state = useState({ email: partner?.email || "", phone: partner?.mobile || "" });
        // We need to add 'sms_phone_for_receipt' to this.
        // This kind of patch is complex for `useState` initialization.
        // A simpler approach for an addon is to manage its own state property if extending the base `this.state` is problematic.

        // Let's manage it as a direct property on the component, updated via getter/setter for the template.
        // And ensure it's reactive if used in the template.
        // For OWL, making it a property and using it in template (via getter) often makes it reactive.
        // Or, explicitly use useState for it.
        this.smsState = useState({ phone_for_receipt: initialSmsPhone });


        onMounted(() => {
            // Any on-mount logic specific to SMS feature
            // e.g., focus input if empty and feature enabled
            if (this.shouldShowSmsFeature && !this.smsState.phone_for_receipt) {
                // const phoneInput = this.el.querySelector('input.send-receipt-sms-input');
                // if (phoneInput) phoneInput.focus();
            }
        });
    },

    get currentOrder() {
        return this.pos.get_order();
    },

    // Getter/Setter for the template to bind the SMS phone input
    get sms_phone_for_receipt_input() {
        return this.smsState.phone_for_receipt;
    },

    set sms_phone_for_receipt_input(value) {
        this.smsState.phone_for_receipt = value;
    },

    get shouldShowSmsFeature() {
        return this.pos.config.enable_sms_receipt;
    },

    async _sendSmsReceipt() {
        const order = this.currentOrder;
        const phone = (this.smsState.phone_for_receipt || "").trim();

        if (!order) {
            this.popup.add(ErrorPopup, { title: _t("Order Not Found"), body: _t("Current order not available.") });
            return;
        }

        if (!phone) {
            this.popup.add(ErrorPopup, { title: _t("Missing Phone Number"), body: _t("Please enter phone number for SMS.") });
            return;
        }

        const phoneRegex = /^[+]?[\d\s-]{7,}$/;
        if (!phoneRegex.test(phone)) {
            this.popup.add(ErrorPopup, { title: _t("Invalid Phone Number"), body: _t("Phone number format is not valid.") });
            return;
        }

        // In Odoo 18, order.id is the backend ID if it's a number.
        if (typeof order.id !== 'number') {
            this.popup.add(ErrorPopup, {
                title: _t("Unsynced Order"),
                body: _t("This order is not synced to the server. Please sync then try again."),
            });
            console.warn(`Attempted to send SMS for unsynced order UID: ${order.uid}. Order ID is: ${order.id}`);
            return;
        }

        // Update the Order model instance with the phone number from the input
        order.set_phone_for_sms_receipt(phone);

        try {
            // Use this.pos.data.call as seen in Odoo 18's base ReceiptScreen
            const result = await this.pos.call("pos.order", "action_send_sms_receipt_rpc", [order.id, phone]);

            if (result === true) {
                this.notification.add(_t("SMS receipt sent successfully to %s.", phone), 3000);
            } else if (result && result.error) {
                this.popup.add(ErrorPopup, { title: _t("SMS Sending Failed"), body: _t(result.error) });
            } else {
                this.popup.add(ErrorPopup, { title: _t("SMS Sending Failed"), body: _t("Unknown error during SMS sending.") });
            }
        } catch (error) {
            console.error("Error sending SMS receipt via RPC:", error);
            let errorMessage = _t("Could not connect or unexpected error.");
            if (error.message?.data?.message) {
                errorMessage = error.message.data.message;
            } else if (error.data?.message) {
                errorMessage = error.data.message;
            } else if (typeof error.message === 'string') {
                errorMessage = error.message;
            }
            this.popup.add(ErrorPopup, { title: _t("SMS Sending Error"), body: errorMessage });
        }
    }
});
// Notes for Odoo 18 adaptation:
// - `useState` is imported from `@odoo/owl`.
// - `_t` for translations.
// - `setup()`:
//   - Initializes `this.smsState = useState({ phone_for_receipt: ... })` to hold the SMS phone number reactively for the input.
//   - The initial value for `smsState.phone_for_receipt` is taken from the Order model's `get_phone_for_sms_receipt()` (which itself should handle pre-filling from partner).
// - `sms_phone_for_receipt_input` (getter/setter): For `t-model` binding in the XML template to `this.smsState.phone_for_receipt`.
// - `shouldShowSmsFeature`: Checks `this.pos.config.enable_sms_receipt`.
// - `_sendSmsReceipt()`:
//   - Gets phone from `this.smsState.phone_for_receipt`.
//   - Validates phone and ensures `order.id` is a number (synced order).
//   - **Crucially, calls `order.set_phone_for_sms_receipt(phone)` before the RPC to ensure the potentially edited phone number is stored on the JS Order model (and thus included in `export_as_JSON` if the order is saved again or for record-keeping).**
//   - Uses `this.pos.call("pos.order", ...)` which is the Odoo 18 equivalent of `this.orm.call` or `this.pos.rpc` in some contexts for calling backend model methods. The base ReceiptScreen uses `this.pos.data.call`, but `this.pos.call` should also work and might be simpler if `pos.data` implies dataset operations. If `this.pos.call` is not found, `this.pos.orm.call` or direct `useService('orm').call` would be alternatives. Let's assume `this.pos.call` is a valid wrapper for RPCs in POS context. If not, `this.env.services.orm.call` is the most direct.
//     After checking Odoo 18 source (`addons/point_of_sale/static/src/app/store/pos_store.js`), `this.pos.call` is indeed a method for RPCs.
//   - Handles responses and errors similar to v17.
// - The XML template will use `t-model="sms_phone_for_receipt_input"`.
// - The approach to use `this.smsState = useState(...)` for the input provides good encapsulation for this new feature's reactive state within the component.
// - Removed unused `ConfirmPopup` import if not used.
// - `_t` should be imported from "@web/core/l10n/translation";
// - The `this.pos.call` is a method available in `PosStore` for RPCs.
// - The structure for `smsState` and its getter/setter for `t-model` is a clean way in OWL.
