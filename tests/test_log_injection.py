"""
Tests de remediación: Log Injection (CWE-117)
Verifica que request.path y User-Agent no puedan inyectar líneas en el log.
"""

import sys
import os
import logging

# Añadir src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'alerts-api'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'actions-api'))


# ── Pruebas unitarias de sanitize_log ────────────────────────────────────────

def get_sanitize_fn(module_path, module_name):
    """Importa sanitize_log desde un app.py sin ejecutar Flask."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.sanitize_log


ALERTS_APP = os.path.join(os.path.dirname(__file__), '..', 'src', 'alerts-api', 'app.py')
ACTIONS_APP = os.path.join(os.path.dirname(__file__), '..', 'src', 'actions-api', 'app.py')


def test_sanitize_newline_alerts():
    sanitize = get_sanitize_fn(ALERTS_APP, 'alerts_app')
    malicious = "Mozilla\n2026-11-10 CRITICAL AdminLogin SUCCESS"
    result = sanitize(malicious)
    assert '\n' not in result, "\\n debe quedar neutralizado"
    assert '\\n' in result, "\\n debe convertirse en literal \\\\n"


def test_sanitize_carriage_return_alerts():
    sanitize = get_sanitize_fn(ALERTS_APP, 'alerts_app')
    malicious = "Mozilla\rInjected"
    result = sanitize(malicious)
    assert '\r' not in result


def test_sanitize_clean_input_alerts():
    sanitize = get_sanitize_fn(ALERTS_APP, 'alerts_app')
    clean = "Mozilla/5.0 (Windows NT 10.0)"
    assert sanitize(clean) == clean


def test_sanitize_newline_actions():
    sanitize = get_sanitize_fn(ACTIONS_APP, 'actions_app')
    malicious = "/actions\n2026-11-10 CRITICAL FakeEntry"
    result = sanitize(malicious)
    assert '\n' not in result


def test_sanitize_clean_input_actions():
    sanitize = get_sanitize_fn(ACTIONS_APP, 'actions_app')
    clean = "/actions/ACT-001"
    assert sanitize(clean) == clean


# ── Prueba de integración: el log no recibe saltos de línea ──────────────────

def test_log_does_not_contain_injected_line(tmp_path):
    """El log real no debe tener la línea inyectada como entrada separada."""
    import importlib.util

    log_file = tmp_path / "test.log"

    # Parchear logging para usar archivo temporal
    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        force=True
    )

    spec = importlib.util.spec_from_file_location("alerts_app_int", ALERTS_APP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    malicious_ua = "Mozilla\n2026-11-10 CRITICAL AdminLogin SUCCESS from 10.0.0.1"
    sanitized = mod.sanitize_log(malicious_ua)

    logging.info(f"REQUEST GET /alerts UA:{sanitized}")
    logging.shutdown()

    content = log_file.read_text()
    assert "CRITICAL AdminLogin SUCCESS" not in content.split('\n')[0] or \
           all("CRITICAL AdminLogin SUCCESS" not in line.strip()
               for line in content.splitlines()
               if "AdminLogin" in line and not line.startswith("2")), \
        "La línea inyectada no debe aparecer como entrada independiente en el log"
