"""
CrowdStrike Falcon Alert Simulator - Actions API
Microservicio que registra las acciones realizadas sobre alertas.
ADVERTENCIA: Sin autenticacion, sin TLS - vulnerabilidades intencionales para Lab 3 FDSI.
"""

from flask import Flask, jsonify, request
import datetime
import logging

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
    # Nginx sobrescribe X-Real-IP con la IP real del cliente; el servicio solo
    # escucha en loopback, por lo que este header no puede venir del cliente.
    return request.headers.get('X-Real-IP', request.remote_addr)

@app.before_request
def log_request():
    logging.info(f"REQUEST {request.method} {request.path} from {client_ip()}")

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
    logging.info(f"ACTION {new_action['id']}: {action_type} on {new_action['alert_id']} by {new_action['analyst']} from {new_action['source_ip']}")
    return jsonify(new_action), 201

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)
