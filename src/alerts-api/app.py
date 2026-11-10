"""
CrowdStrike Falcon Alert Simulator - Alerts API
Microservicio que recibe y expone alertas ficticias de seguridad.
ADVERTENCIA: Sin autenticacion, sin TLS - vulnerabilidades intencionales para Lab 3 FDSI.
"""

from flask import Flask, jsonify, request
import json
import datetime
import logging

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

@app.before_request
def log_request():
    logging.info(f"REQUEST {request.method} {request.path} from {request.headers.get('X-Real-IP', request.remote_addr)} UA:{request.headers.get('User-Agent','')}")

@app.after_request
def log_response(response):
    logging.info(f"RESPONSE {response.status_code} for {request.method} {request.path}")
    response.headers['Server'] = 'FalconSim/1.0'
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
    new_alert = {
        "id": f"ALT-{len(ALERTS)+1:03d}",
        "severity": data.get("severity", "MEDIUM"),
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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
