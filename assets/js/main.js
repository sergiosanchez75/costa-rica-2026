// Costa Rica 2026 — comportamiento compartido: menú móvil + cortina de gastos.

function toggleNav() {
  var links = document.getElementById('nav-links');
  if (links) links.classList.toggle('open');
}

async function sha256Hex(text) {
  var enc = new TextEncoder().encode(text);
  var buf = await crypto.subtle.digest('SHA-256', enc);
  return Array.from(new Uint8Array(buf)).map(function (b) {
    return b.toString(16).padStart(2, '0');
  }).join('');
}

function unlockGastos() {
  var lock = document.getElementById('gastos-lock');
  var content = document.getElementById('gastos-content');
  if (lock) lock.classList.add('hide');
  if (content) content.classList.add('show');
}

function initGastos(expectedHash) {
  if (sessionStorage.getItem('cr26-gastos-unlocked') === '1') {
    unlockGastos();
  }
  var form = document.getElementById('pass-form');
  if (!form) return;
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    var input = document.getElementById('gastos-pass');
    var error = document.getElementById('pass-error');
    var hash = await sha256Hex(input.value);
    if (hash === expectedHash) {
      sessionStorage.setItem('cr26-gastos-unlocked', '1');
      error.classList.remove('show');
      unlockGastos();
    } else {
      error.classList.add('show');
      input.select();
    }
  });
}
