// Manual SMS injection for POS receipt screen
// Copy and paste this code into the browser console when on the POS receipt screen

console.log('🚀 Manual SMS injection starting...');

function addSmsToReceipt() {
    // Look for email input field
    const emailInput = document.querySelector('input[type="email"]');
    if (!emailInput) {
        console.log('❌ Email input not found');
        return false;
    }
    
    // Check if SMS section already exists
    if (document.querySelector('#pos-sms-section')) {
        console.log('⚠️ SMS section already exists');
        return true;
    }
    
    console.log('✅ Found email input, adding SMS section');
    
    // Find the container that holds email input and button
    let emailContainer = emailInput.closest('div');
    while (emailContainer && !emailContainer.querySelector('button')) {
        emailContainer = emailContainer.parentElement;
    }
    
    if (emailContainer) {
        // Create SMS section
        const smsSection = document.createElement('div');
        smsSection.id = 'pos-sms-section';
        smsSection.style.cssText = 'margin-top: 10px; display: flex; align-items: center; gap: 10px;';
        
        // Phone input
        const phoneInput = document.createElement('input');
        phoneInput.type = 'tel';
        phoneInput.placeholder = 'Phone number for SMS receipt';
        phoneInput.style.cssText = 'flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;';
        
        // SMS button (matching email button style)
        const smsButton = document.createElement('button');
        smsButton.innerHTML = '📱';
        smsButton.title = 'Send SMS Receipt';
        smsButton.style.cssText = 'background: #875A7B; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 16px; min-width: 40px; height: 36px;';
        
        // SMS send functionality
        smsButton.onclick = function() {
            const phone = phoneInput.value.trim();
            if (!phone) {
                alert('Please enter a phone number');
                return;
            }
            
            // Show loading
            smsButton.innerHTML = '⏳';
            smsButton.disabled = true;
            
            // Send SMS (using test mode for now)
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
                        order_id: null // Will use test mode
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
                smsButton.innerHTML = '📱';
                smsButton.disabled = false;
            });
        };
        
        // Add hover effect
        smsButton.onmouseover = function() {
            this.style.background = '#6d4c63';
        };
        smsButton.onmouseout = function() {
            this.style.background = '#875A7B';
        };
        
        smsSection.appendChild(phoneInput);
        smsSection.appendChild(smsButton);
        
        // Insert after email container
        emailContainer.parentNode.insertBefore(smsSection, emailContainer.nextSibling);
        
        console.log('✅ SMS section added to POS receipt');
        return true;
    }
    
    console.log('❌ Could not find email container');
    return false;
}

// Try to add SMS section
addSmsToReceipt();

console.log('📱 Manual SMS injection complete - check the receipt screen!');