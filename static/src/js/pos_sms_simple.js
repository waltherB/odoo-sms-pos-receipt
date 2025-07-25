// Simple POS SMS Receipt - No Odoo module system
console.log("🚀 POS SMS Simple - Loading...");

// Wait for the page to load
document.addEventListener('DOMContentLoaded', function() {
    console.log("📱 POS SMS Simple - DOM loaded");
    
    // Function to add SMS section
    function addSmsSection() {
        // Don't add if already exists
        if (document.querySelector('#pos-sms-section')) {
            return;
        }
        
        // Look for the buttons section in receipt screen
        const buttonsDiv = document.querySelector('.receipt-screen .buttons, .buttons');
        if (!buttonsDiv) {
            console.log("❌ Buttons section not found");
            return;
        }
        
        console.log("✅ Found buttons section, adding SMS section");
        
        // Create SMS section
        const smsSection = document.createElement('div');
        smsSection.id = 'pos-sms-section';
        smsSection.className = 'sms-receipt-section my-3';
        smsSection.innerHTML = `
            <div class="d-flex align-items-center gap-2 p-3 bg-warning bg-opacity-25 border border-warning rounded">
                <strong class="text-warning-emphasis" style="min-width: 40px;">SMS:</strong>
                <input type="tel"
                       id="sms-phone-input"
                       class="form-control"
                       placeholder="Phone number for SMS receipt"
                       style="flex: 1;"/>
                
                <button class="btn btn-warning" 
                        onclick="sendSmsFromPos()"
                        title="Send SMS Receipt">
                    📱 SMS
                </button>
            </div>
            <div id="sms-status" class="notice mt-2" style="display: none;"></div>
        `;
        
        // Insert after the buttons section
        buttonsDiv.parentNode.insertBefore(smsSection, buttonsDiv.nextSibling);
        
        console.log("✅ SMS section added successfully");
    }
    
    // Global function for sending SMS
    window.sendSmsFromPos = function() {
        const phoneInput = document.getElementById('sms-phone-input');
        const statusDiv = document.getElementById('sms-status');
        const button = event.target;
        
        const phone = phoneInput.value.trim();
        if (!phone) {
            alert('Please enter a phone number');
            phoneInput.focus();
            return;
        }
        
        // Show loading
        button.innerHTML = '⏳ Sending...';
        button.disabled = true;
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = '<div class="text-info">Sending SMS...</div>';
        
        // Send SMS
        fetch('/pos_sms_receipt/send_sms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    phone: phone,
                    order_id: null
                },
                id: Math.floor(Math.random() * 1000000)
            })
        })
        .then(response => response.json())
        .then(data => {
            const result = data.result || data;
            if (result.success) {
                statusDiv.innerHTML = '<div class="text-success"><i class="fa fa-check-circle me-1"></i>SMS sent successfully to ' + phone + '</div>';
                // Keep phone number for reuse
            } else {
                statusDiv.innerHTML = '<div class="text-danger"><i class="fa fa-exclamation-triangle me-1"></i>Failed: ' + (result.error || 'Unknown error') + '</div>';
            }
        })
        .catch(error => {
            statusDiv.innerHTML = '<div class="text-danger"><i class="fa fa-exclamation-triangle me-1"></i>Error: ' + error.message + '</div>';
        })
        .finally(() => {
            button.innerHTML = '📱 SMS';
            button.disabled = false;
        });
    };
    
    // Try to add SMS section multiple times
    setTimeout(addSmsSection, 1000);
    setTimeout(addSmsSection, 2000);
    setTimeout(addSmsSection, 3000);
    setTimeout(addSmsSection, 5000);
    
    // Monitor for page changes
    const observer = new MutationObserver(() => {
        setTimeout(addSmsSection, 500);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    console.log("📱 POS SMS Simple - Initialized");
});

// Also try immediately in case DOM is already loaded
setTimeout(() => {
    if (document.readyState === 'complete') {
        console.log("📱 POS SMS Simple - DOM already complete, trying now");
        // Trigger the same logic
        document.dispatchEvent(new Event('DOMContentLoaded'));
    }
}, 500);

console.log("📱 POS SMS Simple - Script loaded");