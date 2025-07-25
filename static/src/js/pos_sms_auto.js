// Auto SMS injection for POS - Simple approach
console.log("🚀 POS SMS Auto injection loading...");

// Simple function to add SMS section
function addSmsToPos() {
    // Don't add if already exists
    if (document.querySelector('#pos-sms-section')) {
        return;
    }
    
    // Look for email input
    const emailInput = document.querySelector('input[type="email"]');
    if (!emailInput) {
        return;
    }
    
    console.log("✅ Adding SMS section to POS");
    
    // Find email container
    let emailContainer = emailInput.closest('div');
    while (emailContainer && !emailContainer.querySelector('button')) {
        emailContainer = emailContainer.parentElement;
    }
    
    if (emailContainer) {
        // Create SMS section
        const smsSection = document.createElement('div');
        smsSection.id = 'pos-sms-section';
        smsSection.style.cssText = 'margin-top: 10px; display: flex; align-items: center; gap: 10px; padding: 8px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;';
        
        // SMS label
        const label = document.createElement('strong');
        label.textContent = 'SMS:';
        label.style.cssText = 'color: #856404; min-width: 35px;';
        
        // Phone input
        const phoneInput = document.createElement('input');
        phoneInput.type = 'tel';
        phoneInput.placeholder = 'Phone number for SMS receipt';
        phoneInput.style.cssText = 'flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;';
        
        // SMS button
        const smsButton = document.createElement('button');
        smsButton.innerHTML = '📱';
        smsButton.title = 'Send SMS Receipt';
        smsButton.style.cssText = 'background: #875A7B; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 16px; min-width: 40px; height: 36px;';
        
        // SMS functionality
        smsButton.onclick = function() {
            const phone = phoneInput.value.trim();
            if (!phone) {
                alert('Please enter a phone number');
                return;
            }
            
            smsButton.innerHTML = '⏳';
            smsButton.disabled = true;
            
            fetch('/pos_sms_receipt/send_sms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: { phone: phone, order_id: null },
                    id: Math.floor(Math.random() * 1000000)
                })
            })
            .then(response => response.json())
            .then(data => {
                const result = data.result || data;
                if (result.success) {
                    alert('✅ SMS sent to ' + phone);
                } else {
                    alert('❌ Failed: ' + (result.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('❌ Error: ' + error.message);
            })
            .finally(() => {
                smsButton.innerHTML = '📱';
                smsButton.disabled = false;
            });
        };
        
        // Assemble
        smsSection.appendChild(label);
        smsSection.appendChild(phoneInput);
        smsSection.appendChild(smsButton);
        
        // Insert
        emailContainer.parentNode.insertBefore(smsSection, emailContainer.nextSibling);
        
        console.log("✅ SMS section added to POS successfully");
    }
}

// Try multiple times
setTimeout(addSmsToPos, 1000);
setTimeout(addSmsToPos, 2000);
setTimeout(addSmsToPos, 3000);
setTimeout(addSmsToPos, 5000);
setTimeout(addSmsToPos, 10000);

// Also try on page changes
setInterval(addSmsToPos, 5000);

console.log("📱 POS SMS Auto injection initialized");