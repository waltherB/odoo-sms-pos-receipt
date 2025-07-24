/* @odoo-module */

console.log("🚀 Simple SMS Module Loading...");

// Add SMS button directly to the page when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("📱 Adding SMS button to page");
    
    // Function to add SMS button
    function addSmsButton() {
        // Check if we're on the receipt screen
        if (window.location.href.includes('/pos/ui') || document.querySelector('.pos-content')) {
            console.log("🎯 On POS page, adding SMS button");
            
            // Create SMS button
            const smsButton = document.createElement('button');
            smsButton.innerHTML = '📱 Send SMS Receipt';
            smsButton.style.cssText = `
                position: fixed;
                top: 100px;
                right: 20px;
                background: #007bff;
                color: white;
                border: none;
                padding: 15px 20px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                z-index: 9999;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            `;
            
            smsButton.onclick = function() {
                const phone = prompt('Enter phone number for SMS receipt:');
                if (phone) {
                    sendSmsReceipt(phone);
                }
            };
            
            document.body.appendChild(smsButton);
            console.log("✅ SMS button added successfully");
        }
    }
    
    // Function to send SMS
    function sendSmsReceipt(phone) {
        console.log("📤 Sending SMS to:", phone);
        
        // Try to get current order ID (this is a simplified approach)
        const orderId = 1; // We'll need to get this dynamically
        
        fetch('/pos_sms_receipt/send_sms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    order_id: orderId,
                    phone_number: phone
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("📨 SMS Response:", data);
            if (data.result && data.result.success) {
                alert('✅ SMS sent successfully!');
            } else {
                alert('❌ Failed to send SMS: ' + (data.result?.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('❌ SMS Error:', error);
            alert('❌ Error sending SMS: ' + error.message);
        });
    }
    
    // Add button immediately and also after a delay
    addSmsButton();
    setTimeout(addSmsButton, 2000);
    setTimeout(addSmsButton, 5000);
});

console.log("✅ Simple SMS Module Loaded");