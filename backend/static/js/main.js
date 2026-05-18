// =============================================
//  MediCare Hospital — Shared JS
//  Final Year College Project
// =============================================

// Flash message
function flash(msg, type = 'success') {
  let wrap = document.getElementById('flash-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.id = 'flash-wrap';
    wrap.className = 'flash-wrap';
    document.body.appendChild(wrap);
  }
  const div = document.createElement('div');
  div.className = 'flash' + (type === 'error' ? ' error' : '');
  div.textContent = (type === 'success' ? '✅ ' : '❌ ') + msg;
  wrap.appendChild(div);
  setTimeout(() => div.remove(), 3500);
}

// Set today's min date on date inputs
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="date"]').forEach(el => {
    el.min = new Date().toISOString().split('T')[0];
  });
});
