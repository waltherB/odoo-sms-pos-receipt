/* @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

console.log("🚀 POS SMS Receipt - models.js loaded!");

// Patch Order to add the phone number field
patch(Order.prototype, {
    setup(_options) {
        super.setup(...arguments);
        this.phone_for_sms_receipt = this.phone_for_sms_receipt || null;
    },
    
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.phone_for_sms_receipt = this.phone_for_sms_receipt || null;
        return json;
    },
    
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.phone_for_sms_receipt = json.phone_for_sms_receipt || null;
        // Initialize with customer's mobile/phone if available
        if (!this.phone_for_sms_receipt && this.get_partner()) {
            this.phone_for_sms_receipt = this.get_partner().mobile || this.get_partner().phone || null;
        }
    },
    
    set_phone_for_sms_receipt(phone) {
        this.phone_for_sms_receipt = phone;
    },
    
    get_phone_for_sms_receipt() {
        return this.phone_for_sms_receipt;
    },
    
    // Prefill from customer data when a customer is set
    set_partner(partner) {
        super.set_partner(...arguments);
        if (partner && !this.get_phone_for_sms_receipt()) {
            this.set_phone_for_sms_receipt(partner.mobile || partner.phone || null);
        }
    }
});