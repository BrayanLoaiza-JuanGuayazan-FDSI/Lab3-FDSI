const ALERTS_API = '/api/alerts';
const REFRESH_MS = 30000;

const statusEl = document.getElementById('status');
const tbody = document.getElementById('alerts-body');
const apiKeyInput = document.getElementById('api-key');

function cell(text, className) {
  const td = document.createElement('td');
  td.textContent = text;
  if (className) td.className = className;
  return td;
}

function badgeCell(value) {
  const td = document.createElement('td');
  const badge = document.createElement('span');
  badge.className = 'badge ' + value;
  badge.textContent = value;
  td.appendChild(badge);
  return td;
}

function showMessage(text, isError) {
  const row = document.createElement('tr');
  const td = cell(text, isError ? 'message-cell error' : 'message-cell');
  td.colSpan = 7;
  row.appendChild(td);
  tbody.replaceChildren(row);
}

function alertRow(a) {
  // Los campos vienen del API: siempre como texto, nunca como HTML.
  const row = document.createElement('tr');
  row.append(
    cell(a.id, 'mono'),
    badgeCell(a.severity),
    cell(a.type),
    cell(a.host, 'mono'),
    cell(a.user, 'mono'),
    badgeCell(a.status),
    cell(String(a.created_at).replace('T', ' ').replace('Z', ''), 'mono')
  );
  return row;
}

async function loadAlerts() {
  const apiKey = apiKeyInput.value;
  if (!apiKey) {
    statusEl.textContent = 'sin API key';
    showMessage('Ingrese la API key para ver las alertas.', false);
    return;
  }

  statusEl.textContent = 'actualizando...';
  try {
    const res = await fetch(ALERTS_API + '/alerts', { headers: { 'X-API-Key': apiKey } });
    if (res.status === 401) {
      statusEl.textContent = 'API key invalida';
      showMessage('API key invalida.', true);
      return;
    }
    const data = await res.json();
    const alerts = data.alerts || [];

    const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
    alerts.forEach(a => { if (counts[a.severity] !== undefined) counts[a.severity]++; });
    document.getElementById('cnt-critical').textContent = counts.CRITICAL;
    document.getElementById('cnt-high').textContent = counts.HIGH;
    document.getElementById('cnt-medium').textContent = counts.MEDIUM;
    document.getElementById('cnt-low').textContent = counts.LOW;

    tbody.replaceChildren(...alerts.map(alertRow));
    statusEl.textContent = `${alerts.length} alertas · ${new Date().toLocaleTimeString()}`;
  } catch (e) {
    statusEl.textContent = 'Error conectando a la API';
    showMessage('No se pudo conectar a ' + ALERTS_API + '/alerts', true);
  }
}

document.getElementById('refresh').addEventListener('click', loadAlerts);
apiKeyInput.addEventListener('change', loadAlerts);
setInterval(loadAlerts, REFRESH_MS);
