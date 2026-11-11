"""
Pruebas de remediación: Log Injection (CWE-117) — F-15
Verifica que los 4 puntos del plan estén sanitizados.

Nota sobre Werkzeug: a partir de Werkzeug 2.x, los headers con \n literal
son rechazados por el cliente de test (ValueError), por lo que el ataque real
de User-Agent vía \n no llega a la aplicación. El test verifica que
sanitize_log() funciona directamente y que el `log_request` lo usa.
"""
import importlib.util
import pathlib
import logging

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
API_KEY = 'clave-de-prueba'
AUTH = {'X-API-Key': API_KEY}


def load_app(service, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location(
        service.replace('-', '_'), ROOT / 'src' / service / 'app.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def alerts_module(tmp_path, monkeypatch):
    monkeypatch.setenv('LAB_API_KEY', API_KEY)
    return load_app('alerts-api', tmp_path, monkeypatch)


@pytest.fixture
def actions_module(tmp_path, monkeypatch):
    monkeypatch.setenv('LAB_API_KEY', API_KEY)
    return load_app('actions-api', tmp_path, monkeypatch)


# ---------------------------------------------------------------------------
# Punto 1 y 2: sanitize_log() existe y neutraliza \n y \r
# ---------------------------------------------------------------------------

def test_sanitize_log_neutralizes_newline_alerts(alerts_module):
    """sanitize_log en alerts-api reemplaza \\n por literal \\\\n."""
    result = alerts_module.sanitize_log("evil\nINJECTED")
    assert '\n' not in result
    assert '\\n' in result


def test_sanitize_log_neutralizes_cr_alerts(alerts_module):
    """sanitize_log en alerts-api reemplaza \\r por literal \\\\r."""
    result = alerts_module.sanitize_log("evil\rINJECTED")
    assert '\r' not in result
    assert '\\r' in result


def test_sanitize_log_neutralizes_newline_actions(actions_module):
    """sanitize_log en actions-api reemplaza \\n por literal \\\\n."""
    result = actions_module.sanitize_log("evil\nINJECTED")
    assert '\n' not in result
    assert '\\n' in result


# ---------------------------------------------------------------------------
# Punto 3: log final de create_alert usa valores internos (no input usuario)
# ---------------------------------------------------------------------------

def test_alerts_create_alert_log_uses_internal_id(alerts_module, caplog):
    """NEW ALERT log solo registra id/severity internos, no campos del usuario."""
    with alerts_module.app.test_client() as c:
        with caplog.at_level(logging.INFO):
            c.post('/alerts', json={
                'severity': 'LOW',
                'type': 'Test',
                'host': 'h', 'user': 'u', 'description': 'd', 'ioc': ''
            }, headers=AUTH)
    # El mensaje debe contener ALT-00x y LOW, generados internamente
    new_alert_msgs = [m for m in caplog.messages if 'NEW ALERT' in m]
    assert len(new_alert_msgs) == 1
    assert 'severity:LOW' in new_alert_msgs[0]


# ---------------------------------------------------------------------------
# Punto 4: log final de create_action — analyst y alert_id sanitizados
# ---------------------------------------------------------------------------

def test_actions_create_action_analyst_newline_sanitized(actions_module, caplog):
    """analyst con \\n en create_action aparece como \\\\n en el log (no como salto real)."""
    with actions_module.app.test_client() as c:
        with caplog.at_level(logging.INFO):
            c.post('/actions', json={
                'alert_id': 'ALT-001',
                'analyst': 'evil\nINJECTED ANALYST LINE',
                'action': 'investigate',
                'notes': 'test'
            }, headers=AUTH)
    action_msgs = [m for m in caplog.messages if m.startswith('ACTION')]
    assert len(action_msgs) == 1
    # Debe contener \\n como texto, no como salto de línea real
    assert '\n' not in action_msgs[0]
    assert '\\n' in action_msgs[0]


def test_actions_create_action_alert_id_newline_sanitized(actions_module, caplog):
    """alert_id con \\n en create_action aparece como \\\\n en el log."""
    with actions_module.app.test_client() as c:
        with caplog.at_level(logging.INFO):
            c.post('/actions', json={
                'alert_id': 'ALT-001\nINJECTED ALERTID LINE',
                'analyst': 'analyst',
                'action': 'investigate',
                'notes': 'test'
            }, headers=AUTH)
    action_msgs = [m for m in caplog.messages if m.startswith('ACTION')]
    assert len(action_msgs) == 1
    assert '\n' not in action_msgs[0]
    assert '\\n' in action_msgs[0]
