// ==UserScript==
// @name         POS SMS Receipt
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Add SMS receipt functionality to Odoo POS
// @author       You
// @match        http://localhost:8080/*
// @match        https://your-odoo-domain.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    
    console.log('🚀 POS SMS Receipt UserScript Loading...');
    
    // Function to add SMS section
    function addSmsSection() {
        // Don't add if already exists
        if (document.querySelector('#pos-sms-section')) {
            return true;
        }
        
        // Look for email input
        const emailInput = document.querySelector('input[type="email"]');
        if (!emailInput) {
            return false;
        }
        
        console.log('✅ Adding SMS section to POS');
        
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
            
            // Phone input - try to auto-fill from customer data
            const phoneInput = document.createElement('input');
            phoneInput.type = 'tel';
            phoneInput.placeholder = 'Phone number for SMS receipt';
            phoneInput.style.cssText = 'flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;';
            
            // Try to get customer phone from page content
            try {
                const customerInfo = document.querySelector('[class*="customer"], [class*="partner"], .o_pos_customer_name');
                if (customerInfo) {
                    const text = customerInfo.textContent || '';
                    const phoneMatch = text.match(/\+?[\d\s\-\(\)]{7,}/);
                    if (phoneMatch) {
                        phoneInput.value = phoneMatch[0].trim();
                    }
                }
            } catch (e) {
                console.log('Could not auto-fill customer phone');
            }
            
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
                    phoneInput.focus();
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
                        // Keep the phone number for reuse
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
            
            // Assemble
            smsSection.appendChild(label);
            smsSection.appendChild(phoneInput);
            smsSection.appendChild(smsButton);
            
            // Insert after email container
            emailContainer.parentNode.insertBefore(smsSection, emailContainer.nextSibling);
            
            console.log('✅ SMS section added to POS successfully');
            return true;
        }
        
        return false;
    }
    
    // Try to add SMS section multiple times
    setTimeout(addSmsSection, 1000);
    setTimeout(addSmsSection, 2000);
    setTimeout(addSmsSection, 3000);
    setTimeout(addSmsSection, 5000);
    setTimeout(addSmsSection, 10000);
    
    // Monitor for page changes (POS is SPA)
    const observer = new MutationObserver(() => {
        setTimeout(addSmsSection, 500);
    });
    
    // Start observing when DOM is ready
    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
    } else {
        document.addEventListener('DOMContentLoaded', () => {
            observer.observe(document.body, { childList: true, subtree: true });
        });
    }
    
    // Also try periodically
    setInterval(addSmsSection, 10000);
    
    console.log('📱 POS SMS Receipt UserScript initialized');
})();