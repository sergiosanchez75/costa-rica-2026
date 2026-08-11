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
 * La hoja usa (y crea sola si hace falta) esta cabecera en la fila 1, en
 * este orden de columnas exacto (A, B, C, D, E, F). El script identifica
 * las columnas por posición, no por el texto de la cabecera, para evitar
 * problemas si algún acento se pega distinto:
 *   A: ID | B: Fecha | C: Tipo de Gasto | D: Descripción | E: Lugar | F: Importe
 */

var COL = { ID: 0, FECHA: 1, TIPO: 2, DESCRIPCION: 3, LUGAR: 4, IMPORTE: 5 };
var HEADERS = ['ID', 'Fecha', 'Tipo de Gasto', 'Descripción', 'Lugar', 'Importe'];

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheets()[0];
  if (sheet.getLastRow() < 1) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  }
  return sheet;
}

function formatDate_(value) {
  if (Object.prototype.toString.call(value) === '[object Date]') {
    return Utilities.formatDate(value, Session.getScriptTimeZone(), 'dd/MM/yyyy');
  }
  return String(value || '');
}

function readAll_() {
  var sheet = getSheet_();
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  var values = sheet.getRange(2, 1, lastRow - 1, HEADERS.length).getValues();
  var items = [];
  for (var r = 0; r < values.length; r++) {
    var row = values[r];
    if (row.every(function (c) { return c === '' || c === null; })) continue;
    items.push({
      rowNumber: r + 2,
      id: String(row[COL.ID] || ''),
      fecha: formatDate_(row[COL.FECHA]),
      tipo: String(row[COL.TIPO] || ''),
      descripcion: String(row[COL.DESCRIPCION] || ''),
      lugar: String(row[COL.LUGAR] || ''),
      importe: Number(row[COL.IMPORTE] || 0),
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

    if (action === 'add') {
      if (!body.fecha || !body.tipo || !body.importe) {
        return jsonOut_({ ok: false, error: 'missing_fields' });
      }
      var id = Utilities.getUuid();
      var row = [];
      row[COL.ID] = id;
      row[COL.FECHA] = body.fecha;
      row[COL.TIPO] = body.tipo;
      row[COL.DESCRIPCION] = body.descripcion || '';
      row[COL.LUGAR] = body.lugar || 'General';
      row[COL.IMPORTE] = Number(body.importe);
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
      editRow[COL.ID] = body.id;
      editRow[COL.FECHA] = body.fecha;
      editRow[COL.TIPO] = body.tipo;
      editRow[COL.DESCRIPCION] = body.descripcion || '';
      editRow[COL.LUGAR] = body.lugar || 'General';
      editRow[COL.IMPORTE] = Number(body.importe);
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
