/* @odoo-module */

console.log("🚀🚀🚀 POS SMS RECEIPT MODULE ASSETS ARE LOADING! 🚀🚀🚀");

// Immediately add visible element
const testDiv = document.createElement('div');
testDiv.innerHTML = '🟡 SMS MODULE LOADED - ASSETS WORKING!';
testDiv.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    background: yellow;
    padding: 15px;
    border: 3px solid red;
    z-index: 99999;
    font-weight: bold;
    font-size: 14px;
`;
document.body.appendChild(testDiv);

// Also try DOM ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("🎯 DOM loaded, SMS module confirmed working");
    alert("SMS Module Assets Loaded Successfully!");
});

// And try immediate execution
setTimeout(() => {
    console.log("⏰ Timeout executed - SMS module still working");
    if (!document.querySelector('[data-sms-test]')) {
        const div2 = document.createElement('div');
        div2.setAttribute('data-sms-test', 'true');
        div2.innerHTML = '🔥 SMS ASSETS CONFIRMED WORKING';
        div2.style.cssText = `
            position: fixed;
            top: 60px;
            right: 10px;
            background: lime;
            padding: 10px;
            border: 2px solid green;
            z-index: 99999;
            font-weight: bold;
        `;
        document.body.appendChild(div2);
    }
}, 100);