/* @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup"; // For confirmation if needed

const { useState, onMounted } = owl; // Import Owl hooks if needed for local component state

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.notification = useService("pos_notification"); // For user feedback
        this.popup = useService("popup"); // For error popups
        this.orm = useService("orm"); // For RPC calls

        // Local state for the phone number input, if not directly bound to order model
        // However, it's better to bind directly to the order's phone_for_sms_receipt
        // this.state = useState({ smsPhoneNumber: this.currentOrder.get_phone_for_sms_receipt() || '' });
        // No, direct binding is better. The model.js already handles fetching from partner.

        onMounted(() => {
            // Initialize phone number for SMS when the component mounts
            // This ensures the input field has the correct starting value.
            // The value in currentOrder.phone_for_sms_receipt should be pre-filled by model.js
            // (from partner or existing order data).
            // If the input element is directly bound using t-model or similar, this might be automatic.
        });
    },

    get currentOrder() {
        // In Odoo 17, this.pos.selectedOrder is the way to get current order
        return this.pos.get_order();
    },

    get smsPhoneNumber() {
        return this.currentOrder.get_phone_for_sms_receipt() || "";
    },

    set smsPhoneNumber(value) {
        this.currentOrder.set_phone_for_sms_receipt(value);
    },

    // This method will be called when the "Send by SMS" button is clicked.
    // The actual button definition will be in the XML template.
    async sendSmsReceipt() {
        const order = this.currentOrder;
        const phone = this.smsPhoneNumber; // Get phone from component's state or bound model

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

        // Basic phone validation (you might want a more robust one)
        // This is a very simple regex for digits, possibly with + and spaces.
        const phoneRegex = /^[+]?[\d\s-]{7,}$/;
        if (!phoneRegex.test(phone)) {
            this.popup.add(ErrorPopup, {
                title: this.env._t("Invalid Phone Number"),
                body: this.env._t("The entered phone number format is not valid."),
            });
            return;
        }

        try {
            // Show some loading indicator if possible / desired
            // this.showLoadingIndicator = true; // Needs corresponding template change

            const result = await this.orm.call(
                'pos.order', // Model
                'action_send_sms_receipt_rpc', // Method
                [order.backendId || order.uid, phone] // Args: order_id (use backendId if synced, else uid for unsynced orders if backend handles it)
                                                      // The python method expects order_id (integer)
                                                      // For newly created orders not yet synced, backendId might be null.
                                                      // The Python method needs the actual server ID.
                                                      // This implies SMS can only be sent for orders that are ALREADY synced/finalized.
                                                      // Or, the order data needs to be passed fully.
                                                      // The current python method `action_send_sms_receipt_rpc` takes `order_id`.
                                                      // So, this assumes `order.backendId` is populated.
                                                      // POS usually finalizes order (sends to backend) then goes to receipt screen.
            );

            // this.showLoadingIndicator = false;

            if (result === true) {
                this.notification.add(this.env._t("SMS receipt sent successfully to %s.", phone), 3000);
                order.is_sms_receipt_sent = true; // Mark it on client side too, if needed
                                                  // The python side sets its own field.
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
            // this.showLoadingIndicator = false;
            console.error("Error sending SMS receipt:", error);
            let errorMessage = this.env._t("Could not connect to the server or an unexpected error occurred.");
            if (error.message && error.message.data && error.message.data.message) {
                errorMessage = error.message.data.message;
            } else if (error.legacy && error.legacy.message) { // Odoo 16 error structure
                errorMessage = error.legacy.message;
            } else if (error.message) {
                errorMessage = error.message;
            }
            this.popup.add(ErrorPopup, {
                title: this.env._t("SMS Sending Error"),
                body: errorMessage,
            });
        }
    },

    // To ensure the input field for phone number is correctly bound,
    // you might need to ensure the component re-renders when currentOrder.phone_for_sms_receipt changes.
    // In OWL, if `smsPhoneNumber` getter/setter are used by the template, it should be reactive.

    // Example of how to get the phone number if not using a getter/setter directly bound to template:
    // _onPhoneNumberChange(event) {
    //    this.currentOrder.set_phone_for_sms_receipt(event.target.value);
    //    // If using local state for the input:
    //    // this.state.smsPhoneNumber = event.target.value;
    // }

    get shouldShowSmsFeature() {
        // Ensure this.pos and this.pos.config are available
        return this.pos && this.pos.config && this.pos.config.enable_sms_receipt;
    }
});

// Notes:
// - `setup()`: Initializes services. `onMounted` can be used for actions when the DOM is ready.
// - `currentOrder`: Getter for the current order. In Odoo 17, `this.pos.get_order()` is standard.
// - `smsPhoneNumber` (getter/setter): These allow the XML template to use `t-model="smsPhoneNumber"`
//   for two-way data binding with the order's `phone_for_sms_receipt` property.
// - `sendSmsReceipt()`:
//   - Retrieves the current order and phone number.
//   - Performs basic validation.
//   - Makes an RPC call to `pos.order`'s `action_send_sms_receipt_rpc` method.
//     - **Important**: It passes `order.backendId`. This means the order must have been saved to the
//       backend and have an ID. This is typically true by the time the ReceiptScreen is shown.
//       If SMS needs to be sent for orders not yet on the server, the backend method would need
//       to accept full order data instead of just an ID.
//   - Uses `pos_notification` service for success messages and `popup` service for error messages.
//   - Includes basic error handling for the RPC call.
// - The phone number input field in the XML template should use `t-on-input` or `t-model`
//   to update `this.smsPhoneNumber`.
// - A more robust phone number validation library could be used if needed.
// - The patch structure is standard for extending OWL components in Odoo.
// - Ensure this JS file is correctly listed in `__manifest__.py` assets.
// - Error handling tries to extract messages from Odoo's typical error structures.
// - `ConfirmPopup` is imported but not used; it's there if a confirmation step ("Are you sure?") was desired.
// - Assumes `order.backendId` is the correct server-side ID. In some contexts or for sub-records,
//   it might be just `order.id`. For `pos.order` synced from POS, `backendId` is common for the server ID.
//   The Python method `action_send_sms_receipt_rpc` takes `order_id` as its first arg (after self).
//   So `[order.backendId, phone]` is the correct way to pass arguments.
// - The regex for phone validation is very basic; for production, consider a more comprehensive one or a library.
// - If `this.pos.selectedOrder` is used in older versions, ensure to use the correct way for Odoo 17,
//   which is `this.pos.get_order()`. The provided code uses `this.pos.get_order()`.
// - The use of `this.env._t` is for translations.
// - `useState` from Owl is available if more complex local component state is needed beyond direct model binding.
//   For this case, binding to `currentOrder.phone_for_sms_receipt` via the getter/setter is cleaner.
// - `onMounted` is used to potentially initialize things; here, the model should already handle initialization.
//   It's left as a placeholder for other on-mount logic if needed.
// - The `pos_notification` service is suitable for non-blocking feedback.
// - The `ErrorPopup` service is suitable for blocking error messages that require user attention.
// - The `orm` service is the standard way to make RPC calls in Odoo 17's JS framework.
// - The commented out `showLoadingIndicator` is a suggestion for UX improvement during the RPC call.
//   This would require adding an element in the XML template controlled by this boolean.
// - `order.is_sms_receipt_sent = true;` on the client side is an optimistic update. The backend
//   is the source of truth for this field (`is_sms_receipt_sent` on `pos.order`).
//   This client-side flag might be useful for UI changes (e.g., disabling the button after sending)
//   without needing to re-fetch the order. However, it's not strictly necessary if the backend handles it.
//   The Python code already sets this field on the server.
// - The `patch` target `ReceiptScreen.prototype` is correct for extending component methods and properties.
// - `owl` is imported for `useState` and `onMounted`, though `useState` isn't used directly here in favor of model binding.
//   `onMounted` is used as an example. If no specific on-mount logic is needed beyond what OWL/models provide, it can be removed.
//   However, services like `orm`, `popup`, `notification` are typically initialized in `setup`.
// - `this.pos` is assumed to be available in `ReceiptScreen` and provides access to global POS state and services.
// - The services (`notification`, `popup`, `orm`) are correctly obtained using `useService`.
// - The arguments to `action_send_sms_receipt_rpc` are `[order.backendId, phone]`. This matches the Python method's
//   parameters `(self, order_id, phone_number=None)`. The `self` is implicit. `order_id` is the first explicit arg.
// - Final check on `order.backendId`: In Odoo 16/17, after an order is successfully synced (which happens before or upon entering the receipt screen for a paid order), `order.backendId` should hold the database ID of the `pos.order` record. If the order is not yet synced (e.g., offline mode, draft order), `backendId` might be `null` or undefined. The current logic assumes synced orders.
//   If an order can be in a state where it has a `uid` (client-side unique ID) but no `backendId` when `sendSmsReceipt` is called,
//   and SMS is desired for such orders, the backend `action_send_sms_receipt_rpc` would need to be adapted to find the order by `uid` or accept the full order data for processing, which is more complex.
//   The typical flow is: Pay -> Order Finalized (Sync to Backend) -> Receipt Screen. So `backendId` should be available.
//   If `order.id` is used instead of `order.backendId`, it usually refers to a client-side temporary ID if the order is not yet saved.
//   The `backendId` is the correct property for the server database ID.
// - Added `this.env._t` for all user-facing strings to enable translation.
// - The error handling for the catch block has been improved to try and get more specific messages.
