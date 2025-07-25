// Fallback SMS injection - load this via script tag
console.log("🚀 Fallback SMS injection loading...");

// Wait for DOM and try multiple times
function injectSmsSection() {
    const emailInput = document.querySelector('input[type="email"]');
    if (!emailInput || document.querySelector('#pos-sms-section')) {
        return false;
    }
    
    console.log("✅ Injecting SMS section");
    
    // Find email container
    let emailContainer = emailInput.closest('div');
    while (emailContainer && !emailContainer.querySelector('button')) {
        emailContainer = emailContainer.parentElement;
    }
    
    if (emailContainer) {
        // Create SMS section
        const smsSection = document.createElement('div');
        smsSection.id = 'pos-sms-section';
        smsSection.className = 'sms-receipt-section d-flex align-items-center gap-2 mt-2 p-2 bg-warning border rounded';
        
        // Try to get customer phone from POS data
        let customerPhone = '';
        try {
            // Try to access POS data if available
            if (window.odoo && window.odoo.define) {
                // This would need to be adapted based on actual POS structure
                customerPhone = ''; // Will be filled by server-side if possible
            }
        } catch (e) {
            console.log('Could not access POS customer data');
        }
        
        smsSection.innerHTML = `
            <strong class="text-dark">SMS:</strong>
            <input type="tel" 
                   class="form-control" 
                   placeholder="Phone number for SMS receipt"
                   value="${customerPhone}"
                   style="flex: 1;"
                   id="sms-phone-input">
            <button class="btn" 
                    style="background: #875A7B; color: white; min-width: 40px; height: 36px;"
                    onclick="sendSmsFromPos()"
                    title="Send SMS Receipt">
                📱
            </button>
        `;
        
        emailContainer.parentNode.insertBefore(smsSection, emailContainer.nextSibling);
        console.log("✅ SMS section injected successfully");
        return true;
    }
    
    return false;
}

// SMS sending function
window.sendSmsFromPos = function() {
    const phoneInput = document.getElementById('sms-phone-input');
    const phone = phoneInput.value.trim();
    
    if (!phone) {
        alert('Please enter a phone number');
        return;
    }
    
    const button = phoneInput.nextElementSibling;
    button.innerHTML = '⏳';
    button.disabled = true;
    
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
            alert('✅ SMS sent to ' + phone);
            phoneInput.value = '';
        } else {
            alert('❌ Failed: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        alert('❌ Error: ' + error.message);
    })
    .finally(() => {
        button.innerHTML = '📱';
        button.disabled = false;
    });
};

// Try injection multiple times
setTimeout(injectSmsSection, 1000);
setTimeout(injectSmsSection, 2000);
setTimeout(injectSmsSection, 3000);
setTimeout(injectSmsSection, 5000);

// Monitor for changes
const observer = new MutationObserver(() => {
    setTimeout(injectSmsSection, 500);
});
observer.observe(document.body, {childList: true, subtree: true});

console.log("📱 Fallback SMS injection initialized");