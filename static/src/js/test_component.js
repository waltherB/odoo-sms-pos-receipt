/* @odoo-module */

console.log("🚀 POS SMS Receipt module assets are loading!");

// Add a visible element to the page to confirm loading
document.addEventListener('DOMContentLoaded', function() {
    console.log("🎯 DOM loaded, adding test element");
    const testDiv = document.createElement('div');
    testDiv.innerHTML = '🟡 SMS MODULE LOADED - CHECK CONSOLE';
    testDiv.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: yellow;
        padding: 10px;
        border: 2px solid red;
        z-index: 9999;
        font-weight: bold;
    `;
    document.body.appendChild(testDiv);
    
    // Remove after 5 seconds
    setTimeout(() => testDiv.remove(), 5000);
});