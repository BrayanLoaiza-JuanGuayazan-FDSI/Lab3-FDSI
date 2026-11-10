"""Pruebas de regresion de los hallazgos remediados en el Lab 5."""
import ast
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
API_KEY = 'clave-de-prueba'
AUTH = {'X-API-Key': API_KEY}

PROTECTED = [
    ('alerts-api', 'GET', '/'),
    ('alerts-api', 'GET', '/alerts'),
    ('alerts-api', 'GET', '/alerts/ALT-001'),
    ('alerts-api', 'GET', '/alerts/severity/HIGH'),
    ('alerts-api', 'POST', '/alerts'),
    ('actions-api', 'GET', '/'),
    ('actions-api', 'GET', '/actions'),
    ('actions-api', 'GET', '/actions/ACT-001'),
    ('actions-api', 'GET', '/actions/alert/ALT-001'),
    ('actions-api', 'POST', '/actions'),
]


def load_client(service, tmp_path, monkeypatch):
    # app.py configura un log relativo al directorio actual.
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location(
        service.replace('-', '_'), ROOT / 'src' / service / 'app.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app.test_client()


@pytest.fixture
def client_for(tmp_path, monkeypatch):
    monkeypatch.setenv('LAB_API_KEY', API_KEY)
    return lambda service: load_client(service, tmp_path, monkeypatch)


@pytest.mark.parametrize('service,method,path', PROTECTED)
def test_cwe306_rejects_missing_key(client_for, service, method, path):
    assert client_for(service).open(path, method=method).status_code == 401


@pytest.mark.parametrize('service,method,path', PROTECTED)
def test_cwe306_rejects_wrong_key(client_for, service, method, path):
    response = client_for(service).open(path, method=method, headers={'X-API-Key': 'otra'})
    assert response.status_code == 401


@pytest.mark.parametrize('service,method,path', [p for p in PROTECTED if p[1] == 'GET'])
def test_cwe306_accepts_valid_key(client_for, service, method, path):
    assert client_for(service).open(path, method=method, headers=AUTH).status_code == 200


@pytest.mark.parametrize('service', ['alerts-api', 'actions-api'])
def test_health_stays_public(client_for, service):
    assert client_for(service).get('/health').status_code == 200


@pytest.mark.parametrize('service', ['alerts-api', 'actions-api'])
def test_cwe306_fails_closed_without_configured_key(tmp_path, monkeypatch, service):
    monkeypatch.delenv('LAB_API_KEY', raising=False)
    client = load_client(service, tmp_path, monkeypatch)
    assert client.get('/', headers={'X-API-Key': ''}).status_code == 401


@pytest.mark.parametrize('body', [
    {'severity': 'NOPE'},
    {'severity': 7},
    {'type': 'a' * 257},
    {'host': ['no-es-texto']},
])
def test_cwe20_rejects_invalid_alert(client_for, body):
    assert client_for('alerts-api').post('/alerts', json=body, headers=AUTH).status_code == 400


def test_cwe20_accepts_and_normalizes_valid_alert(client_for):
    response = client_for('alerts-api').post('/alerts', json={'severity': 'high'}, headers=AUTH)
    assert response.status_code == 201
    assert response.get_json()['severity'] == 'HIGH'


def test_cwe79_payload_is_stored_as_plain_text(client_for):
    payload = '<img src=x onerror=console.log(1)>'
    response = client_for('alerts-api').post('/alerts', json={'type': payload}, headers=AUTH)
    assert response.get_json()['type'] == payload


def test_cwe79_dashboard_does_not_build_html_from_data():
    source = (ROOT / 'frontend/app.js').read_text(encoding='utf-8')
    assert 'innerHTML' not in source
    assert 'textContent' in source


def test_csp_blocks_inline_code():
    conf = (ROOT / 'nginx/lab3-fdsi.conf').read_text(encoding='utf-8')
    assert "script-src 'self'" in conf
    assert 'unsafe-inline' not in conf
    html = (ROOT / 'frontend/index.html').read_text(encoding='utf-8')
    for inline in ('<script>', '<style>', 'onclick=', 'style="'):
        assert inline not in html


@pytest.mark.parametrize('service', ['alerts-api', 'actions-api'])
def test_server_header_does_not_identify_the_stack(client_for, service):
    response = client_for(service).get('/health')
    assert 'FalconSim' not in response.headers.get('Server', '')
    source = (ROOT / 'src' / service / 'app.py').read_text(encoding='utf-8')
    assert 'request_handler=NoBannerRequestHandler' in source


@pytest.mark.parametrize('service', ['alerts-api', 'actions-api'])
def test_debug_mode_is_disabled(service):
    tree = ast.parse((ROOT / 'src' / service / 'app.py').read_text(encoding='utf-8'))
    runs = [n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'run']
    assert runs
    for call in runs:
        debug = next(k for k in call.keywords if k.arg == 'debug')
        assert debug.value.value is False
