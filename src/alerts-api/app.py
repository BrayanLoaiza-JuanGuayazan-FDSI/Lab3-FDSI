"""
CrowdStrike Falcon Alert Simulator - Alerts API
Microservicio que recibe y expone alertas ficticias de seguridad.
Requiere el header X-API-Key en todas las rutas excepto /health. Sin TLS (riesgo residual documentado).
"""

from flask import Flask, jsonify, request
import json
import datetime
import hmac
import logging
import os
from werkzeug.serving import WSGIRequestHandler

logging.basicConfig(
    filename='alerts.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

app = Flask(__name__)

ALERTS = [
    {
        "id": "ALT-001",
        "severity": "HIGH",
        "type": "MalwareDetected",
        "host": "WORKSTATION-42",
        "user": "john.doe",
        "description": "Suspicious executable detected: invoice_Q3.exe",
        "status": "open",
        "created_at": "2026-09-13T08:15:00Z",
        "ioc": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    {
        "id": "ALT-002",
        "severity": "CRITICAL",
        "type": "LateralMovement",
        "host": "SERVER-DC01",
        "user": "SYSTEM",
        "description": "Abnormal SMB traffic from internal host",
        "status": "open",
        "created_at": "2026-09-13T09:30:00Z",
        "ioc": "ip:192.168.1.105"
    },
    {
        "id": "ALT-003",
        "severity": "MEDIUM",
        "type": "PrivilegeEscalation",
        "host": "LAPTOP-007",
        "user": "jane.smith",
        "description": "Sudo command executed outside business hours",
        "status": "investigating",
        "created_at": "2026-09-13T02:47:00Z",
        "ioc": "process:sudo bash"
    },
    {
        "id": "ALT-004",
        "severity": "LOW",
        "type": "FailedLogin",
        "host": "VPN-GW01",
        "user": "unknown",
        "description": "Multiple failed login attempts from external IP",
        "status": "closed",
        "created_at": "2026-09-12T23:10:00Z",
        "ioc": "ip:203.0.113.45"
    },
    {
        "id": "ALT-005",
        "severity": "HIGH",
        "type": "DataExfiltration",
        "host": "FILESERVER-01",
        "user": "contractor01",
        "description": "Unusual large file transfer to external storage",
        "status": "open",
        "created_at": "2026-09-13T11:05:00Z",
        "ioc": "domain:dropbox.com"
    }
]

ACTIONS_LOG = []

ALLOWED_SEVERITIES = {'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'}
TEXT_FIELDS = ('type', 'host', 'user', 'description', 'ioc')
MAX_TEXT_LENGTH = 256


def sanitize_log(value: str) -> str:
    """Neutraliza saltos de línea para prevenir Log Injection (CWE-117)."""
    return value.replace('\n', '\\n').replace('\r', '\\r')


@app.before_request
def log_request():
    path = sanitize_log(request.path)
    ua   = sanitize_log(request.headers.get('User-Agent', ''))
    ip   = request.headers.get('X-Real-IP', request.remote_addr)
    logging.info(f"REQUEST {request.method} {path} from {ip} UA:{ua}")

def api_key_is_valid():
    expected = os.environ.get('LAB_API_KEY', '')
    provided = request.headers.get('X-API-Key', '')
    return bool(expected) and hmac.compare_digest(provided.encode(), expected.encode())

@app.before_request
def require_api_key():
    # /health queda publico para el monitoreo; sin LAB_API_KEY configurada se rechaza todo.
    if request.endpoint != 'health' and not api_key_is_valid():
        return jsonify({"error": "Unauthorized"}), 401

@app.after_request
def log_response(response):
    path = sanitize_log(request.path)
    logging.info(f"RESPONSE {response.status_code} for {request.method} {path}")
    return response

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "CrowdStrike Falcon Alert Simulator",
        "version": "1.0.0",
        "endpoints": {
            "GET /alerts": "List all alerts",
            "GET /alerts/<id>": "Get alert by ID",
            "POST /alerts": "Create new alert",
            "GET /alerts/severity/<level>": "Filter by severity",
            "GET /health": "Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()})

@app.route('/alerts', methods=['GET'])
def get_alerts():
    status_filter = request.args.get('status')
    if status_filter:
        filtered = [a for a in ALERTS if a['status'] == status_filter]
        return jsonify({"total": len(filtered), "alerts": filtered})
    return jsonify({"total": len(ALERTS), "alerts": ALERTS})

@app.route('/alerts/<alert_id>', methods=['GET'])
def get_alert(alert_id):
    alert = next((a for a in ALERTS if a['id'] == alert_id), None)
    if not alert:
        return jsonify({"error": "Alert not found", "id": alert_id}), 404
    return jsonify(alert)

@app.route('/alerts/severity/<level>', methods=['GET'])
def get_by_severity(level):
    filtered = [a for a in ALERTS if a['severity'] == level.upper()]
    return jsonify({"severity": level.upper(), "total": len(filtered), "alerts": filtered})

@app.route('/alerts', methods=['POST'])
def create_alert():
    data = request.get_json(silent=True) or {}
    severity = data.get("severity", "MEDIUM")
    if not isinstance(severity, str) or severity.upper() not in ALLOWED_SEVERITIES:
        return jsonify({"error": f"Invalid severity. Allowed: {sorted(ALLOWED_SEVERITIES)}"}), 400
    for field in TEXT_FIELDS:
        value = data.get(field, "")
        if not isinstance(value, str) or len(value) > MAX_TEXT_LENGTH:
            return jsonify({"error": f"Invalid field: {field}"}), 400

    new_alert = {
        "id": f"ALT-{len(ALERTS)+1:03d}",
        "severity": severity.upper(),
        "type": data.get("type", "Unknown"),
        "host": data.get("host", "UNKNOWN-HOST"),
        "user": data.get("user", "unknown"),
        "description": data.get("description", ""),
        "status": "open",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "ioc": data.get("ioc", "")
    }
    ALERTS.append(new_alert)
    logging.info(f"NEW ALERT created: {new_alert['id']} severity:{new_alert['severity']}")
    return jsonify(new_alert), 201

class NoBannerRequestHandler(WSGIRequestHandler):
    # El servidor de Werkzeug anuncia su version y la de Python en el header Server.
    def version_string(self):
        return 'api'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, request_handler=NoBannerRequestHandler)
