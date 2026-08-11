// Costa Rica 2026 — comportamiento compartido: menú móvil, cortina de gastos
// y lector de la Google Sheet de gastos.

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
  if (expenseConfig && expenseConfig.csvUrl) loadExpenses(expenseConfig);
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

/* ---------------- Gastos: lectura de la Google Sheet ---------------- */

function normalizeLabel(s) {
  return (s || '').toString().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
}

function parseAmount(s) {
  if (!s) return 0;
  s = s.toString().trim().replace(/[€$\s]/g, '');
  if (s.indexOf(',') > -1 && s.indexOf('.') > -1) {
    s = s.replace(/\./g, '').replace(',', '.');
  } else if (s.indexOf(',') > -1) {
    s = s.replace(',', '.');
  }
  var n = parseFloat(s);
  return isNaN(n) ? 0 : n;
}

function fmtEUR(n) {
  return n.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
}

function parseCSV(text) {
  var rows = [];
  var row = [];
  var field = '';
  var inQuotes = false;
  for (var i = 0; i < text.length; i++) {
    var c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; } else { inQuotes = false; }
      } else {
        field += c;
      }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ',') {
      row.push(field); field = '';
    } else if (c === '\n') {
      row.push(field); rows.push(row); row = []; field = '';
    } else if (c === '\r') {
      // saltar
    } else {
      field += c;
    }
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows.filter(function (r) { return r.some(function (c) { return c.trim() !== ''; }); });
}

function rowsToObjects(rows) {
  if (!rows.length) return [];
  var headers = rows[0].map(function (h) { return h.trim(); });
  return rows.slice(1).map(function (r) {
    var obj = {};
    headers.forEach(function (h, i) { obj[h] = (r[i] || '').trim(); });
    return obj;
  });
}

function matchByLabel(list, label) {
  var n = normalizeLabel(label);
  return list.find(function (x) { return normalizeLabel(x.label) === n; });
}

async function loadExpenses(cfg) {
  var cardsEl = document.getElementById('expense-cards');
  var chartEl = document.getElementById('expense-chart');
  var listEl = document.getElementById('expense-list');
  if (!listEl) return;

  var loading = '<p class="hint">Cargando gastos…</p>';
  if (listEl) listEl.innerHTML = loading;

  try {
    var res = await fetch(cfg.csvUrl, { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    var text = await res.text();
    var objs = rowsToObjects(parseCSV(text));

    var items = objs.map(function (o) {
      var catLabel = o['Tipo de Gasto'] || '';
      var placeLabel = o['Lugar'] || '';
      var cat = matchByLabel(cfg.categories, catLabel);
      var place = matchByLabel(cfg.places, placeLabel);
      return {
        date: o['Fecha'] || '',
        category: cat ? cat.label : (catLabel || 'Otros'),
        categoryColor: cat ? cat.color : '#8a8f86',
        description: o['Descripción'] || o['Descripcion'] || '',
        place: place ? place.label : (placeLabel || 'General'),
        placeColor: place ? place.color : '#8a8f86',
        amount: parseAmount(o['Importe']),
      };
    }).filter(function (it) { return it.date || it.description || it.amount; });

    renderExpenseCards(items, cfg, cardsEl);
    renderExpenseChart(items, cfg, chartEl);
    renderExpenseList(items, listEl);
  } catch (err) {
    if (listEl) listEl.innerHTML = '<p class="hint">No se ha podido cargar la hoja de gastos. Comprueba el enlace publicado en data.py.</p>';
    if (cardsEl) cardsEl.innerHTML = '';
    if (chartEl) chartEl.innerHTML = '';
  }
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

  return row;
}

function renderExpenseList(items, el) {
  el.innerHTML = '';
  if (!items.length) {
    el.innerHTML = '<p class="hint">Todavía no hay gastos registrados. Añádelos en la Google Sheet.</p>';
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
