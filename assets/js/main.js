// Costa Rica 2026 — comportamiento compartido: menú móvil, cortina de gastos
// y el lector/editor de la Google Sheet de gastos (via Apps Script).

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

function unlockGastos(expenseConfig) {
  var lock = document.getElementById('gastos-lock');
  var content = document.getElementById('gastos-content');
  if (lock) lock.classList.add('hide');
  if (content) content.classList.add('show');

  var fab = document.getElementById('exp-add-btn');
  if (expenseConfig && expenseConfig.apiUrl) {
    if (fab) fab.classList.add('show');
    initExpenseForm(expenseConfig);
    loadExpenses(expenseConfig);
  } else if (fab) {
    fab.classList.remove('show');
  }
}

function initGastos(expectedHash, expenseConfig) {
  if (sessionStorage.getItem('cr26-gastos-unlocked') === '1') {
    unlockGastos(expenseConfig);
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
      unlockGastos(expenseConfig);
    } else {
      error.classList.add('show');
      input.select();
    }
  });
}

/* ---------------- Gastos: lectura/escritura via Apps Script ---------------- */

var currentExpenseConfig = null;
var currentExpenseItems = [];
var expenseFormReady = false;

function normalizeLabel(s) {
  return (s || '').toString().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
}

function fmtEUR(n) {
  return n.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
}

function matchByLabel(list, label) {
  var n = normalizeLabel(label);
  return list.find(function (x) { return normalizeLabel(x.label) === n; });
}

function isoToSpanishDate(iso) {
  if (!iso) return '';
  var p = iso.split('-');
  if (p.length !== 3) return iso;
  return p[2] + '/' + p[1] + '/' + p[0];
}

function spanishDateToIso(s) {
  if (!s) return '';
  var p = s.split('/');
  if (p.length !== 3) return '';
  var dd = p[0].padStart(2, '0');
  var mm = p[1].padStart(2, '0');
  var yyyy = p[2].length === 2 ? '20' + p[2] : p[2];
  return yyyy + '-' + mm + '-' + dd;
}

function toExpenseItem(raw, cfg) {
  var cat = matchByLabel(cfg.categories, raw.tipo);
  var place = matchByLabel(cfg.places, raw.lugar);
  return {
    id: raw.id,
    date: raw.fecha || '',
    category: cat ? cat.label : (raw.tipo || 'Otros'),
    categoryColor: cat ? cat.color : '#8a8f86',
    description: raw.descripcion || '',
    place: place ? place.label : (raw.lugar || 'General'),
    placeColor: place ? place.color : '#8a8f86',
    amount: Number(raw.importe) || 0,
  };
}

async function loadExpenses(cfg) {
  var cardsEl = document.getElementById('expense-cards');
  var chartEl = document.getElementById('expense-chart');
  var listEl = document.getElementById('expense-list');
  if (!listEl) return;

  listEl.innerHTML = '<p class="hint">Cargando gastos…</p>';

  try {
    var res = await fetch(cfg.apiUrl, { cache: 'no-store' });
    var data = await res.json();
    if (!data.ok) throw new Error(data.error || 'error');

    var items = data.items.map(function (raw) { return toExpenseItem(raw, cfg); });
    currentExpenseItems = items;
    currentExpenseConfig = cfg;

    renderExpenseCards(items, cfg, cardsEl);
    renderExpenseChart(items, cfg, chartEl);
    renderExpenseList(items, listEl);
  } catch (err) {
    if (listEl) listEl.innerHTML = '<p class="hint">No se ha podido cargar la hoja de gastos. Comprueba el enlace en EXPENSES_API_URL (data.py) y que el despliegue de Apps Script sigue activo.</p>';
    if (cardsEl) cardsEl.innerHTML = '';
    if (chartEl) chartEl.innerHTML = '';
  }
}

async function postExpense(apiUrl, payload) {
  var res = await fetch(apiUrl, { method: 'POST', body: JSON.stringify(payload) });
  var data = await res.json();
  if (!data.ok) throw new Error(data.error || 'error');
  return data;
}

function categoryTotals(items, cfg) {
  var totals = {};
  cfg.categories.forEach(function (c) { totals[c.label] = 0; });
  items.forEach(function (it) { totals[it.category] = (totals[it.category] || 0) + it.amount; });
  return totals;
}

function renderExpenseCards(items, cfg, el) {
  if (!el) return;
  var totals = categoryTotals(items, cfg);
  var grandTotal = items.reduce(function (s, it) { return s + it.amount; }, 0);

  el.innerHTML = '';

  var totalCard = document.createElement('div');
  totalCard.className = 'exp-stat--total';
  totalCard.innerHTML = '<div class="l">Total gastado</div><div class="v">' + fmtEUR(grandTotal) + '</div>';
  el.appendChild(totalCard);

  cfg.categories.forEach(function (c) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'exp-card';
    btn.style.setProperty('--c', c.color);
    var amt = totals[c.label] || 0;
    btn.innerHTML = '<span class="exp-card-label">' + c.label + '</span><span class="exp-card-amt">' + fmtEUR(amt) + '</span>';
    btn.addEventListener('click', function () { openExpensePopup(c.label, c.color, items); });
    el.appendChild(btn);
  });
}

function renderExpenseChart(items, cfg, el) {
  if (!el) return;
  var totals = categoryTotals(items, cfg);
  var grandTotal = items.reduce(function (s, it) { return s + it.amount; }, 0);

  if (grandTotal <= 0) {
    el.innerHTML = '<p class="hint">Todavía no hay gastos registrados.</p>';
    return;
  }

  var stops = [];
  var acc = 0;
  var legendItems = [];
  cfg.categories.forEach(function (c) {
    var amt = totals[c.label] || 0;
    if (amt <= 0) return;
    var start = (acc / grandTotal) * 100;
    acc += amt;
    var end = (acc / grandTotal) * 100;
    stops.push(c.color + ' ' + start.toFixed(2) + '% ' + end.toFixed(2) + '%');
    legendItems.push({ label: c.label, color: c.color, pct: Math.round((amt / grandTotal) * 100) });
  });

  var donut = document.createElement('div');
  donut.className = 'donut';
  donut.style.background = 'conic-gradient(' + stops.join(',') + ')';
  var hole = document.createElement('div');
  hole.className = 'donut-hole';
  hole.innerHTML = '<span class="donut-total">' + fmtEUR(grandTotal) + '</span><span class="donut-label">total</span>';
  donut.appendChild(hole);

  var legend = document.createElement('div');
  legend.className = 'donut-legend';
  legendItems.forEach(function (li) {
    var row = document.createElement('div');
    row.className = 'legend-row';
    row.innerHTML = '<span class="dot" style="background:' + li.color + '"></span>' + li.label + ' · ' + li.pct + '%';
    legend.appendChild(row);
  });

  el.innerHTML = '';
  el.appendChild(donut);
  el.appendChild(legend);
}

function buildExpenseRow(it, showCategory) {
  var row = document.createElement('div');
  row.className = 'exp-row';

  var date = document.createElement('span');
  date.className = 'exp-row-date';
  date.textContent = it.date;
  row.appendChild(date);

  if (showCategory) {
    var cat = document.createElement('span');
    cat.className = 'exp-row-cat';
    cat.textContent = it.category;
    cat.style.color = it.categoryColor;
    cat.style.borderColor = it.categoryColor;
    row.appendChild(cat);
  }

  var desc = document.createElement('span');
  desc.className = 'exp-row-desc';
  desc.textContent = it.description;
  row.appendChild(desc);

  var place = document.createElement('span');
  place.className = 'exp-row-place';
  place.textContent = it.place;
  place.style.color = it.placeColor;
  row.appendChild(place);

  var amt = document.createElement('span');
  amt.className = 'exp-row-amt';
  amt.textContent = fmtEUR(it.amount);
  row.appendChild(amt);

  var editBtn = document.createElement('button');
  editBtn.type = 'button';
  editBtn.className = 'exp-row-edit';
  editBtn.setAttribute('aria-label', 'Editar gasto');
  editBtn.innerHTML = '<svg class="icon" viewBox="0 0 24 24" style="width:14px;height:14px;stroke-width:2"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>';
  editBtn.addEventListener('click', function (e) { e.stopPropagation(); openExpenseForm(it); });
  row.appendChild(editBtn);

  return row;
}

function renderExpenseList(items, el) {
  el.innerHTML = '';
  if (!items.length) {
    el.innerHTML = '<p class="hint">Todavía no hay gastos registrados. Pulsa el botón "+" para añadir el primero.</p>';
    return;
  }
  items.slice().reverse().forEach(function (it) {
    el.appendChild(buildExpenseRow(it, true));
  });
}

function openExpensePopup(label, color, items) {
  var overlay = document.getElementById('exp-popup');
  var titleEl = document.getElementById('exp-popup-title');
  var listEl = document.getElementById('exp-popup-list');
  if (!overlay || !titleEl || !listEl) return;

  var filtered = items.filter(function (it) { return it.category === label; });
  var total = filtered.reduce(function (s, it) { return s + it.amount; }, 0);

  titleEl.textContent = label;
  titleEl.style.color = color;
  listEl.innerHTML = '';

  var summary = document.createElement('p');
  summary.className = 'hint';
  summary.style.margin = '0 0 12px';
  summary.textContent = filtered.length + (filtered.length === 1 ? ' gasto · ' : ' gastos · ') + 'Total ' + fmtEUR(total);
  listEl.appendChild(summary);

  if (!filtered.length) {
    var empty = document.createElement('p');
    empty.className = 'hint';
    empty.textContent = 'Sin gastos en esta categoría todavía.';
    listEl.appendChild(empty);
  } else {
    filtered.slice().reverse().forEach(function (it) {
      listEl.appendChild(buildExpenseRow(it, false));
    });
  }

  overlay.classList.add('show');
}

function closeExpensePopup() {
  var overlay = document.getElementById('exp-popup');
  if (overlay) overlay.classList.remove('show');
}

/* ---------------- Formulario de anadir / editar gasto ---------------- */

function populateExpenseFormSelects(cfg) {
  var tipoSel = document.getElementById('exp-form-tipo');
  var lugarSel = document.getElementById('exp-form-lugar');
  if (tipoSel) {
    tipoSel.innerHTML = '<option value="" disabled>Selecciona…</option>' +
      cfg.categories.map(function (c) { return '<option value="' + c.label + '">' + c.label + '</option>'; }).join('');
  }
  if (lugarSel) {
    lugarSel.innerHTML = cfg.places.map(function (p) { return '<option value="' + p.label + '">' + p.label + '</option>'; }).join('');
  }
}

function openExpenseForm(item) {
  var modal = document.getElementById('exp-form-modal');
  var title = document.getElementById('exp-form-title');
  var idField = document.getElementById('exp-form-id');
  var fechaField = document.getElementById('exp-form-fecha');
  var tipoField = document.getElementById('exp-form-tipo');
  var descField = document.getElementById('exp-form-desc');
  var lugarField = document.getElementById('exp-form-lugar');
  var importeField = document.getElementById('exp-form-importe');
  var deleteBtn = document.getElementById('exp-form-delete');
  var errorEl = document.getElementById('exp-form-error');
  if (!modal) return;

  errorEl.classList.remove('show');

  if (item) {
    title.textContent = 'Editar gasto';
    idField.value = item.id;
    fechaField.value = spanishDateToIso(item.date);
    tipoField.value = item.category;
    descField.value = item.description;
    lugarField.value = item.place;
    importeField.value = item.amount;
    deleteBtn.style.display = 'inline-flex';
  } else {
    title.textContent = 'Añadir gasto';
    idField.value = '';
    fechaField.value = new Date().toISOString().slice(0, 10);
    tipoField.value = '';
    descField.value = '';
    lugarField.value = 'General';
    importeField.value = '';
    deleteBtn.style.display = 'none';
  }

  modal.classList.add('show');
}

function closeExpenseForm() {
  var modal = document.getElementById('exp-form-modal');
  if (modal) modal.classList.remove('show');
}

function initExpenseForm(cfg) {
  populateExpenseFormSelects(cfg);

  var addBtn = document.getElementById('exp-add-btn');
  if (addBtn) addBtn.onclick = function () { openExpenseForm(); };

  if (expenseFormReady) return;
  expenseFormReady = true;

  var form = document.getElementById('exp-form');
  var errorEl = document.getElementById('exp-form-error');
  var saveBtn = form.querySelector('.exp-form-save');
  var deleteBtn = document.getElementById('exp-form-delete');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    errorEl.classList.remove('show');

    var id = document.getElementById('exp-form-id').value;
    var fechaIso = document.getElementById('exp-form-fecha').value;
    var tipo = document.getElementById('exp-form-tipo').value;
    var desc = document.getElementById('exp-form-desc').value.trim();
    var lugar = document.getElementById('exp-form-lugar').value;
    var importeStr = document.getElementById('exp-form-importe').value;
    var importe = parseFloat(importeStr);

    if (!fechaIso || !tipo || !importeStr || isNaN(importe) || importe <= 0) {
      errorEl.textContent = 'Revisa los campos obligatorios: fecha, tipo de gasto e importe.';
      errorEl.classList.add('show');
      return;
    }

    var payload = {
      action: id ? 'edit' : 'add',
      id: id || undefined,
      fecha: isoToSpanishDate(fechaIso),
      tipo: tipo,
      descripcion: desc,
      lugar: lugar || 'General',
      importe: importe,
    };

    saveBtn.disabled = true;
    saveBtn.textContent = 'Guardando…';
    try {
      await postExpense(currentExpenseConfig.apiUrl, payload);
      closeExpenseForm();
      await loadExpenses(currentExpenseConfig);
    } catch (err) {
      errorEl.textContent = 'No se ha podido guardar. Comprueba tu conexión e inténtalo de nuevo.';
      errorEl.classList.add('show');
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Guardar';
    }
  });

  deleteBtn.addEventListener('click', async function () {
    var id = document.getElementById('exp-form-id').value;
    if (!id) return;
    if (!confirm('¿Seguro que quieres eliminar este gasto?')) return;

    deleteBtn.disabled = true;
    try {
      await postExpense(currentExpenseConfig.apiUrl, { action: 'delete', id: id });
      closeExpenseForm();
      await loadExpenses(currentExpenseConfig);
    } catch (err) {
      errorEl.textContent = 'No se ha podido eliminar. Inténtalo de nuevo.';
      errorEl.classList.add('show');
    } finally {
      deleteBtn.disabled = false;
    }
  });
}

/* ---------------- Diario del día (por actividad) ---------------- */

async function initDiary(activityId, apiUrl) {
  var textEl = document.getElementById('diary-text');
  var saveBtn = document.getElementById('diary-save');
  var statusEl = document.getElementById('diary-status');
  if (!textEl || !saveBtn || !statusEl) return;

  if (!apiUrl) {
    textEl.disabled = true;
    textEl.placeholder = 'Conecta la API en TRIP_API_URL (data.py) para poder guardar el diario.';
    saveBtn.disabled = true;
    return;
  }

  statusEl.textContent = 'Cargando…';
  try {
    var res = await fetch(apiUrl + '?resource=diario', { cache: 'no-store' });
    var data = await res.json();
    if (data.ok) {
      var entry = data.items.find(function (it) { return it.activityId === activityId; });
      textEl.value = entry ? entry.texto : '';
    }
    statusEl.textContent = '';
  } catch (err) {
    statusEl.textContent = 'No se ha podido cargar el diario.';
  }

  saveBtn.addEventListener('click', async function () {
    saveBtn.disabled = true;
    statusEl.textContent = 'Guardando…';
    try {
      var res = await fetch(apiUrl, {
        method: 'POST',
        body: JSON.stringify({ resource: 'diario', activityId: activityId, texto: textEl.value }),
      });
      var data = await res.json();
      if (!data.ok) throw new Error(data.error || 'error');
      statusEl.textContent = 'Guardado ✓';
      setTimeout(function () { statusEl.textContent = ''; }, 2500);
    } catch (err) {
      statusEl.textContent = 'No se ha podido guardar. Inténtalo de nuevo.';
    } finally {
      saveBtn.disabled = false;
    }
  });
}
