/* @odoo-module */

import { Order } from "@point_of_sale/app/store/models"; // Standard import path
import { patch } from "@web/core/utils/patch";

// Patch Order to add the phone number field for SMS receipts
patch(Order.prototype, {
    setup(options) {
        super.setup(...arguments);
        this.phone_for_sms_receipt = this.phone_for_sms_receipt || null;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.phone_for_sms_receipt = this.get_phone_for_sms_receipt() || null;
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.phone_for_sms_receipt = json.phone_for_sms_receipt || null;
        // Pre-fill from partner if not already set on the order
        if (!this.phone_for_sms_receipt && this.get_partner()) {
            this.phone_for_sms_receipt = this.get_partner().mobile || this.get_partner().phone || null;
        }
    },

    set_phone_for_sms_receipt(phone) {
        this.phone_for_sms_receipt = phone ? String(phone).trim() : null;
    },

    get_phone_for_sms_receipt() {
        return this.phone_for_sms_receipt;
    },

    // Override set_partner to prefill phone_for_sms_receipt
    set_partner(partner) {
        const oldPartner = this.get_partner();
        super.set_partner(...arguments); // Call original set_partner
        const newPartner = this.get_partner();

        if (newPartner && (oldPartner?.id !== newPartner.id || !this.get_phone_for_sms_receipt())) {
            const currentSmsPhone = this.get_phone_for_sms_receipt();
            const oldPartnerPhone = oldPartner ? (oldPartner.mobile || oldPartner.phone) : null;

            if (!currentSmsPhone || (oldPartnerPhone && currentSmsPhone === oldPartnerPhone)) {
                 this.set_phone_for_sms_receipt(newPartner.mobile || newPartner.phone || null);
            }
        } else if (!newPartner && oldPartner) {
            // If partner is removed, clear the phone_for_sms_receipt if it matched the old partner's phone.
            const currentSmsPhone = this.get_phone_for_sms_receipt();
            const oldPartnerPhone = oldPartner.mobile || oldPartner.phone;
            if (currentSmsPhone && currentSmsPhone === oldPartnerPhone) {
                this.set_phone_for_sms_receipt(null);
            }
        }
    }
});
// Notes:
// - Assumes `Order` class is imported from "@point_of_sale/app/store/models".
// - Standard patching mechanism.
// - `phone_for_sms_receipt` is initialized, exported in JSON for backend, and initialized from JSON.
// - Pre-filling logic from partner's mobile/phone on `init_from_JSON` and `set_partner` is included.
// - Getter and Setter for `phone_for_sms_receipt`.
// - This structure is very similar to the Odoo 17 version, as these parts of the Order model are fundamental.
// - Ensure this file is correctly listed in `__manifest__.py` under `point_of_sale.assets`.
//   The path used in manifest: 'pos_sms_receipt/static/src/app/store/models.js' matches this file's location.
