// Test if module JS is loading
alert('🚀 POS SMS MODULE JAVASCRIPT IS LOADING! 🚀');
console.log('🚀 POS SMS MODULE JAVASCRIPT IS LOADING! 🚀');

// Add visible element immediately
document.body.style.border = '5px solid red';

// Add a big visible indicator
setTimeout(function() {
    const div = document.createElement('div');
    div.innerHTML = 'SMS MODULE LOADED!';
    div.style.cssText = 'position:fixed;top:0;left:0;width:100%;background:red;color:white;text-align:center;font-size:20px;z-index:999999;padding:10px;';
    document.body.appendChild(div);
}, 100);