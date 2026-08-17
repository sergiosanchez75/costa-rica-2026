/**
 * Costa Rica 2026 — API del viaje (gastos + diario del día).
 *
 * Convierte esta Google Sheet en una pequeña API que usa la web del viaje
 * para dos cosas:
 *   - La página de Gastos (leer / añadir / editar / borrar gastos).
 *   - El "Diario del día" de cada actividad (leer / guardar texto libre).
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
 * 6. Copia la URL que termina en /exec y pégala en TRIP_API_URL,
 *    dentro de data.py.
 *
 * GASTOS: usa la primera pestaña de la hoja (la crea con cabecera si hace
 * falta), con esta cabecera en la fila 1, por posición (A-F), no por texto:
 *   A: ID | B: Fecha | C: Tipo de Gasto | D: Descripción | E: Lugar | F: Importe
 *
 * DIARIO: usa (y crea sola si hace falta) una segunda pestaña llamada
 * "Diario", con columnas A: ActivityId | B: Texto.
 */

var COL = { ID: 0, FECHA: 1, TIPO: 2, DESCRIPCION: 3, LUGAR: 4, IMPORTE: 5 };
var HEADERS = ['ID', 'Fecha', 'Tipo de Gasto', 'Descripción', 'Lugar', 'Importe'];

var DIARIO_SHEET_NAME = 'Diario';
var DIARIO_COL = { ACTIVITY_ID: 0, TEXTO: 1 };
var DIARIO_HEADERS = ['ActivityId', 'Texto'];

/* ---------------------------------------------------------------- gastos */

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

/* ---------------------------------------------------------------- diario */

function getDiarioSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(DIARIO_SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(DIARIO_SHEET_NAME);
  }
  if (sheet.getLastRow() < 1) {
    sheet.getRange(1, 1, 1, DIARIO_HEADERS.length).setValues([DIARIO_HEADERS]);
  }
  return sheet;
}

function readDiario_() {
  var sheet = getDiarioSheet_();
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  var values = sheet.getRange(2, 1, lastRow - 1, DIARIO_HEADERS.length).getValues();
  var items = [];
  for (var r = 0; r < values.length; r++) {
    var row = values[r];
    if (!row[DIARIO_COL.ACTIVITY_ID]) continue;
    items.push({
      rowNumber: r + 2,
      activityId: String(row[DIARIO_COL.ACTIVITY_ID] || ''),
      texto: String(row[DIARIO_COL.TEXTO] || ''),
    });
  }
  return items;
}

function saveDiario_(activityId, texto) {
  var sheet = getDiarioSheet_();
  var items = readDiario_();
  var target = null;
  for (var i = 0; i < items.length; i++) {
    if (items[i].activityId === activityId) { target = items[i]; break; }
  }
  if (target) {
    sheet.getRange(target.rowNumber, DIARIO_COL.TEXTO + 1).setValue(texto);
  } else {
    var row = [];
    row[DIARIO_COL.ACTIVITY_ID] = activityId;
    row[DIARIO_COL.TEXTO] = texto;
    sheet.appendRow(row);
  }
}

/* ------------------------------------------------------------------ web */

function jsonOut_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  var resource = e.parameter && e.parameter.resource;
  if (resource === 'diario') {
    return jsonOut_({ ok: true, items: readDiario_() });
  }
  return jsonOut_({ ok: true, items: readAll_() });
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);

    if (body.resource === 'diario') {
      if (!body.activityId) return jsonOut_({ ok: false, error: 'missing_fields' });
      saveDiario_(body.activityId, body.texto || '');
      return jsonOut_({ ok: true });
    }

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
