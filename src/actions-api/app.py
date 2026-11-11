"""
CrowdStrike Falcon Alert Simulator - Actions API
Microservicio que registra las acciones realizadas sobre alertas.
Requiere el header X-API-Key en todas las rutas excepto /health. Sin TLS (riesgo residual documentado).
"""

from flask import Flask, jsonify, request
import datetime
import hmac
import logging
import os
from werkzeug.serving import WSGIRequestHandler

logging.basicConfig(
    filename='actions.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

app = Flask(__name__)

ACTIONS = [
    {
        "id": "ACT-001",
        "alert_id": "ALT-002",
        "analyst": "carlos.garcia",
        "action": "escalate",
        "notes": "Escalated to CSIRT team - potential ransomware lateral movement",
        "timestamp": "2026-09-13T09:45:00Z"
    },
    {
        "id": "ACT-002",
        "alert_id": "ALT-001",
        "analyst": "maria.torres",
        "action": "investigate",
        "notes": "Started forensic analysis on endpoint WORKSTATION-42",
        "timestamp": "2026-09-13T08:30:00Z"
    },
    {
        "id": "ACT-003",
        "alert_id": "ALT-004",
        "analyst": "carlos.garcia",
        "action": "close",
        "notes": "False positive - legitimate user locked out, reset credentials",
        "timestamp": "2026-09-12T23:40:00Z"
    }
]

def client_ip():
    return request.headers.get('X-Real-IP', request.remote_addr)


def sanitize_log(value: str) -> str:
    """Neutraliza saltos de línea para prevenir Log Injection (CWE-117)."""
    return value.replace('\n', '\\n').replace('\r', '\\r')


@app.before_request
def log_request():
    path = sanitize_log(request.path)
    logging.info(f"REQUEST {request.method} {path} from {client_ip()}")

def api_key_is_valid():
    expected = os.environ.get('LAB_API_KEY', '')
    provided = request.headers.get('X-API-Key', '')
    return bool(expected) and hmac.compare_digest(provided.encode(), expected.encode())

@app.before_request
def require_api_key():
    # /health queda publico para el monitoreo; sin LAB_API_KEY configurada se rechaza todo.
    if request.endpoint != 'health' and not api_key_is_valid():
        return jsonify({"error": "Unauthorized"}), 401

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Actions API",
        "version": "1.0.0",
        "endpoints": {
            "GET /actions": "List all actions",
            "GET /actions/<id>": "Get action by ID",
            "GET /actions/alert/<alert_id>": "Get actions for an alert",
            "POST /actions": "Register a new action",
            "GET /health": "Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()})

@app.route('/actions', methods=['GET'])
def get_actions():
    return jsonify({"total": len(ACTIONS), "actions": ACTIONS})

@app.route('/actions/<action_id>', methods=['GET'])
def get_action(action_id):
    action = next((a for a in ACTIONS if a['id'] == action_id), None)
    if not action:
        return jsonify({"error": "Action not found"}), 404
    return jsonify(action)

@app.route('/actions/alert/<alert_id>', methods=['GET'])
def get_actions_by_alert(alert_id):
    filtered = [a for a in ACTIONS if a['alert_id'] == alert_id]
    return jsonify({"alert_id": alert_id, "total": len(filtered), "actions": filtered})

@app.route('/actions', methods=['POST'])
def create_action():
    data = request.get_json(silent=True) or {}
    allowed_actions = ['investigate', 'escalate', 'contain', 'close', 'reopen']
    action_type = data.get('action', 'investigate')
    if action_type not in allowed_actions:
        return jsonify({"error": f"Invalid action. Allowed: {allowed_actions}"}), 400

    # Validar antes de construir o guardar la acción para evitar estados parciales.
    for field, default in (("alert_id", ""), ("analyst", "anonymous")):
        value = data.get(field, default)
        if not isinstance(value, str):
            return jsonify({"error": f"Invalid field: {field}"}), 400

    new_action = {
        "id": f"ACT-{len(ACTIONS)+1:03d}",
        "alert_id": data.get("alert_id", ""),
        "analyst": data.get("analyst", "anonymous"),
        "action": action_type,
        "notes": data.get("notes", ""),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "source_ip": client_ip()
    }
    ACTIONS.append(new_action)
    alert_id_safe = sanitize_log(new_action['alert_id'])
    analyst_safe  = sanitize_log(new_action['analyst'])
    logging.info(f"ACTION {new_action['id']}: {action_type} on {alert_id_safe} by {analyst_safe} from {new_action['source_ip']}")
    return jsonify(new_action), 201

class NoBannerRequestHandler(WSGIRequestHandler):
    # El servidor de Werkzeug anuncia su version y la de Python en el header Server.
    def version_string(self):
        return 'api'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False, request_handler=NoBannerRequestHandler)
