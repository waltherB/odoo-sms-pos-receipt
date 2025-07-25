/* @odoo-module */

console.log("🚀🚀🚀 POS TEST MODULE LOADING 🚀🚀🚀");

// Add a very visible indicator
setTimeout(() => {
    const div = document.createElement('div');
    div.innerHTML = 'POS TEST MODULE ACTIVE!';
    div.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:red;color:white;padding:20px;font-size:24px;z-index:999999;border:5px solid yellow;';
    document.body.appendChild(div);
}, 1000);

// Also try to modify the receipt screen directly
setTimeout(() => {
    const receiptScreen = document.querySelector('.receipt-screen, .pos-receipt, [class*="receipt"]');
    if (receiptScreen) {
        console.log("✅ Found receipt screen element");
        const smsDiv = document.createElement('div');
        smsDiv.innerHTML = `
            <div style="background:yellow;padding:10px;margin:10px;border:2px solid red;">
                <h3>SMS RECEIPT TEST</h3>
                <input type="tel" placeholder="Phone number" style="width:200px;padding:5px;margin:5px;">
                <button style="padding:5px 10px;background:green;color:white;border:none;">📱 Send SMS</button>
            </div>
        `;
        receiptScreen.appendChild(smsDiv);
        console.log("✅ Added SMS section to receipt screen");
    } else {
        console.log("❌ Receipt screen not found");
    }
}, 2000);