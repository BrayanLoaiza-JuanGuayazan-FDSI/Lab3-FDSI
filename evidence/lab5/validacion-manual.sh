#!/bin/bash
# Validacion manual no destructiva contra el staging local (peticiones inocuas, datos ficticios).
# Uso: validacion-manual.sh <base_url> <contenedor> [api_key]
BASE=$1; CTR=$2; KEY=${3:-}
H=(); [ -n "$KEY" ] && H=(-H "X-API-Key: $KEY")
show() { echo; echo "### $1"; shift; "$@" 2>&1; echo; }
code() { curl -s -o /dev/null -w 'HTTP %{http_code}\n' "$@"; }
J='Content-Type: application/json'

show "H1 CWE-306: GET /alerts SIN credencial"           code "$BASE/api/alerts/alerts"
show "H1 CWE-306: GET /actions SIN credencial"          code "$BASE/api/actions/actions"
show "H1 CWE-306: POST /actions SIN credencial"         code -X POST -H "$J" -d '{"alert_id":"ALT-001","analyst":"lab.tester","action":"close"}' "$BASE/api/actions/actions"
show "H1 CWE-306: POST /alerts con credencial INVALIDA" code -X POST -H "$J" -H 'X-API-Key: clave-incorrecta' -d '{"type":"lab"}' "$BASE/api/alerts/alerts"
show "H1 control: GET /health sigue publico"            code "$BASE/api/alerts/health"
show "H1 control: GET /alerts con credencial valida"    code "${H[@]}" "$BASE/api/alerts/alerts"

P='{"type":"<img src=x onerror=console.log(1)>","host":"POC-HOST","user":"poc.tester","severity":"LOW"}'
show "H2 CWE-79: POST de carga inocua (se almacena)"    curl -s -w '\nHTTP %{http_code}\n' -X POST -H "$J" "${H[@]}" -d "$P" "$BASE/api/alerts/alerts"
show "H2 CWE-79: el dashboard usa innerHTML con datos?" sh -c "curl -s '$BASE/' '$BASE/app.js' | grep -c 'tbody.innerHTML = alerts'"
show "M CWE-20: severity fuera del enum"                code -X POST -H "$J" "${H[@]}" -d '{"type":"lab","severity":"NOPE"}' "$BASE/api/alerts/alerts"
show "M CWE-20: campo de longitud excesiva"             code -X POST -H "$J" "${H[@]}" -d "{\"type\":\"$(printf 'a%.0s' {1..300})\"}" "$BASE/api/alerts/alerts"
show "M CWE-200: header Server alerts-api (loopback)"   docker exec "$CTR" sh -c "curl -sI -X GET http://127.0.0.1:5000/health | grep -i '^server'"
show "M CWE-200: header Server actions-api (loopback)"  docker exec "$CTR" sh -c "curl -sI -X GET http://127.0.0.1:5001/health | grep -i '^server'"
show "M CSP: header Content-Security-Policy en /"       sh -c "curl -sI '$BASE/' | grep -i '^content-security-policy' || echo AUSENTE"
show "M debug: consola Werkzeug /console"               docker exec "$CTR" sh -c "curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:5000/console"
