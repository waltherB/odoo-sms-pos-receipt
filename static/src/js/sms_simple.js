// Simple SMS Receipt for POS
console.log("📱 SMS Receipt Module Loading...");

(function() {
    'use strict';
    
    console.log("📱 SMS Module: Starting initialization");
    
    // Add indicator immediately
    const indicator = document.createElement('div');
    indicator.innerHTML = '🟢 SMS ACTIVE';
    indicator.style.cssText = 'position:fixed;top:10px;left:10px;background:lime;color:black;padding:5px;z-index:99999;font-size:12px;';
    document.body.appendChild(indicator);
    
    function addSmsButton() {
        if (document.querySelector('#sms-btn')) return;
        
        const btn = document.createElement('button');
        btn.id = 'sms-btn';
        btn.innerHTML = '📱 SMS';
        btn.style.cssText = 'position:fixed;top:50px;right:20px;background:#875A7B;color:white;border:none;padding:10px;border-radius:4px;cursor:pointer;z-index:99999;';
        
        btn.onclick = function() {
            const phone = prompt('Phone number:');
            if (phone) {
                alert('SMS would be sent to: ' + phone);
            }
        };
        
        document.body.appendChild(btn);
        console.log("✅ SMS button added");
    }
    
    // Add button with multiple attempts
    addSmsButton();
    setTimeout(addSmsButton, 1000);
    setTimeout(addSmsButton, 3000);
    
    console.log("📱 SMS Module: Initialization complete");
})();