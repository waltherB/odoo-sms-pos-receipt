/* @odoo-module */

import { Order, Orderline, PosGlobalState } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

// Patch PosGlobalState if needed for global settings, not for this specific field.
// export class PosSmsPosGlobalState extends PosGlobalState {
//    async _processData(loadedData) {
//        await super._processData(...arguments);
//        // Load any global config related to SMS here if necessary
//    }
// }
// patch(PosGlobalState.prototype, PosSmsPosGlobalState);


// Patch Order to add the phone number field
patch(Order.prototype, {
    setup(_options) {
        super.setup(...arguments);
        this.phone_for_sms_receipt = this.phone_for_sms_receipt || null;
        // If loading from backend, this field should be populated by init_from_JSON
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.phone_for_sms_receipt = this.phone_for_sms_receipt || null;
        return json;
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.phone_for_sms_receipt = json.phone_for_sms_receipt || null;
        // Initialize with customer's mobile/phone if available and no specific SMS phone is set
        if (!this.phone_for_sms_receipt && this.get_partner()) {
            this.phone_for_sms_receipt = this.get_partner().mobile || this.get_partner().phone || null;
        }
    },
    set_phone_for_sms_receipt(phone) {
        this.phone_for_sms_receipt = phone;
        // Odoo 16+ POS uses a different way to trigger changes, often automatic with tracked:
        // this.trigger('change', this); // For older versions or if not automatically reactive
    },
    get_phone_for_sms_receipt() {
        return this.phone_for_sms_receipt;
    },
    // Optionally, prefill from customer data when a customer is set
    set_partner(partner) {
        super.set_partner(...arguments);
        if (partner && !this.get_phone_for_sms_receipt()) { // Only if not already set for SMS specifically
            this.set_phone_for_sms_receipt(partner.mobile || partner.phone || null);
        } else if (!partner) {
            // Clear the phone if customer is removed, unless you want to keep it
            // this.set_phone_for_sms_receipt(null);
        }
    }
});

// No changes needed for Orderline for this feature.
// patch(Orderline.prototype, { ... });

// Notes:
// 1. `setup`: Initializes the field when a new Order object is created.
// 2. `export_as_JSON`: Ensures the phone number is included in the data sent to the server
//    when the order is finalized. This is critical for `_order_fields` on the Python side.
// 3. `init_from_JSON`: Populates the field when an order is loaded from the backend
//    (e.g., when loading existing orders or after an online sync).
//    It also tries to prefill from the customer's main mobile/phone number if available.
// 4. `set_phone_for_sms_receipt` / `get_phone_for_sms_receipt`: Standard setter/getter.
// 5. `set_partner`: Extended to auto-fill the SMS phone number from the selected customer's
//    details if no specific SMS phone has been entered yet. This provides a good default.
//
// This setup ensures that `phone_for_sms_receipt` is managed within the POS Order object,
// saved to the backend, and loaded from the backend.
// The ReceiptScreen JS will use `set_phone_for_sms_receipt` and `get_phone_for_sms_receipt`.
// The `patch` utility is standard for modifying existing Odoo JS classes.
// Make sure this file is correctly listed in `__manifest__.py` under `point_of_sale.assets`.
// This is for Odoo 16/17 using the OWL component system and ES6 modules.
// The `PosGlobalState` patch is commented out as it's not strictly needed for this field,
// but shown as an example if global configurations were required.
// The reactivity in Odoo 17's OWL components usually means direct assignment to `this.phone_for_sms_receipt`
// in a component would trigger re-renders if that property is used in its template.
// The `set_phone_for_sms_receipt` method is good practice for encapsulation and if extra logic is needed.
// The pre-filling logic in `init_from_JSON` and `set_partner` improves UX by providing a default phone number.
