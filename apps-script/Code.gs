/**
 * Costa Rica 2026 — API de gastos.
 *
 * Convierte esta Google Sheet en una pequeña API (leer / añadir / editar /
 * borrar) que usa la web del viaje para la página de Gastos.
 *
 * INSTALACIÓN
 * 1. Abre (o crea) la Google Sheet donde quieres guardar los gastos.
 * 2. Extensiones -> Apps Script.
 * 3. Borra el contenido de Code.gs que aparece por defecto y pega este
 *    archivo entero.
 * 4. Implementar -> Nueva implementación -> tipo "Aplicación web".
 *      - Ejecutar como: Yo
 *      - Quién tiene acceso: Cualquier usuario
 * 5. Autoriza el acceso cuando te lo pida (es tu propia hoja, es normal
 *    que Google avise de que es un script "no verificado" — es tuyo).
 * 6. Copia la URL que termina en /exec y pégala en EXPENSES_API_URL,
 *    dentro de data.py.
 *
 * La hoja usa (y crea sola si hace falta) esta cabecera en la fila 1:
 *   ID | Fecha | Tipo de Gasto | Descripción | Lugar | Importe
 */

var HEADERS = ['ID', 'Fecha', 'Tipo de Gasto', 'Descripción', 'Lugar', 'Importe'];

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheets()[0];
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
  }
  return sheet;
}

function headerIndex_(sheet) {
  var headerRow = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var idx = {};
  headerRow.forEach(function (h, i) { idx[String(h).trim()] = i; });
  return idx;
}

function formatDate_(value) {
  if (Object.prototype.toString.call(value) === '[object Date]') {
    return Utilities.formatDate(value, Session.getScriptTimeZone(), 'dd/MM/yyyy');
  }
  return String(value || '');
}

function readAll_() {
  var sheet = getSheet_();
  var idx = headerIndex_(sheet);
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  var values = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).getValues();
  var items = [];
  for (var r = 0; r < values.length; r++) {
    var row = values[r];
    if (row.every(function (c) { return c === '' || c === null; })) continue;
    items.push({
      rowNumber: r + 2,
      id: String(row[idx['ID']] || ''),
      fecha: formatDate_(row[idx['Fecha']]),
      tipo: String(row[idx['Tipo de Gasto']] || ''),
      descripcion: String(row[idx['Descripción']] || ''),
      lugar: String(row[idx['Lugar']] || ''),
      importe: Number(row[idx['Importe']] || 0),
    });
  }
  return items;
}

function jsonOut_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  return jsonOut_({ ok: true, items: readAll_() });
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var action = body.action;
    var sheet = getSheet_();
    var idx = headerIndex_(sheet);

    if (action === 'add') {
      if (!body.fecha || !body.tipo || !body.importe) {
        return jsonOut_({ ok: false, error: 'missing_fields' });
      }
      var id = Utilities.getUuid();
      var row = [];
      row[idx['ID']] = id;
      row[idx['Fecha']] = body.fecha;
      row[idx['Tipo de Gasto']] = body.tipo;
      row[idx['Descripción']] = body.descripcion || '';
      row[idx['Lugar']] = body.lugar || 'General';
      row[idx['Importe']] = Number(body.importe);
      sheet.appendRow(row);
      return jsonOut_({ ok: true, id: id });
    }

    if (action === 'edit') {
      if (!body.id || !body.fecha || !body.tipo || !body.importe) {
        return jsonOut_({ ok: false, error: 'missing_fields' });
      }
      var items = readAll_();
      var target = null;
      for (var i = 0; i < items.length; i++) {
        if (items[i].id === body.id) { target = items[i]; break; }
      }
      if (!target) return jsonOut_({ ok: false, error: 'not_found' });

      var editRow = [];
      editRow[idx['ID']] = body.id;
      editRow[idx['Fecha']] = body.fecha;
      editRow[idx['Tipo de Gasto']] = body.tipo;
      editRow[idx['Descripción']] = body.descripcion || '';
      editRow[idx['Lugar']] = body.lugar || 'General';
      editRow[idx['Importe']] = Number(body.importe);
      sheet.getRange(target.rowNumber, 1, 1, HEADERS.length).setValues([editRow]);
      return jsonOut_({ ok: true });
    }

    if (action === 'delete') {
      if (!body.id) return jsonOut_({ ok: false, error: 'missing_fields' });
      var itemsD = readAll_();
      var targetD = null;
      for (var j = 0; j < itemsD.length; j++) {
        if (itemsD[j].id === body.id) { targetD = itemsD[j]; break; }
      }
      if (!targetD) return jsonOut_({ ok: false, error: 'not_found' });
      sheet.deleteRow(targetD.rowNumber);
      return jsonOut_({ ok: true });
    }

    return jsonOut_({ ok: false, error: 'unknown_action' });
  } catch (err) {
    return jsonOut_({ ok: false, error: String(err) });
  }
}
