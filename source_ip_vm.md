# Verificación en la VM — `source_ip` (T05 / M-009 / G04)

**Fecha/hora UTC:** 2026-10-16T01:15:40Z
**Origen de la prueba:** Kali (`192.168.17.130`) → VM Ubuntu (`192.168.17.129`), vía Nginx.
**Objetivo:** confirmar que `actions-api` registra la IP real del cliente (`source_ip`, inyectada por Nginx como `X-Real-IP`) en vez de `127.0.0.1`, y que coincide con `access.log`.

## Comando ejecutado (desde Kali)

```bash
curl -s -X POST http://192.168.17.129/api/actions/actions \
  -H 'Content-Type: application/json' \
  -d '{"alert_id":"ALT-002","analyst":"carlos.garcia","action":"investigate","notes":"prueba de verificacion source_ip Parte II"}'
```

## Respuesta obtenida

```json
{
  "action": "investigate",
  "alert_id": "ALT-002",
  "analyst": "carlos.garcia",
  "id": "ACT-004",
  "notes": "prueba de verificacion source_ip Parte II",
  "source_ip": "192.168.17.130",
  "timestamp": "2026-10-16T01:15:40.358935Z"
}
```

## Correlación en los logs del servidor

**`access.log` (Nginx):**
```
192.168.17.130 - - [16/Oct/2026:01:15:40 +0000] "POST /api/actions/actions HTTP/1.1" 201 210 "-" "curl/8.20.0"
```

**`actions.log` (actions-api, Flask):**
```
2026-10-16 01:15:40,357 INFO REQUEST POST /actions from 192.168.17.130
2026-10-16 01:15:40,358 INFO ACTION ACT-004: investigate on ALT-002 by carlos.garcia from 192.168.17.130
```

## Resultado

Las tres fuentes (respuesta de la API, `access.log` de Nginx y `actions.log` de Flask) reportan la **misma IP real del cliente** (`192.168.17.130`, la de la estación Kali, no `127.0.0.1`) y el **mismo timestamp**. Confirma que `X-Real-IP` se propaga correctamente desde Nginx y que `client_ip()` en `actions-api/app.py` lo captura bien.

**Conclusión para el registro de riesgos:** T05 pasa de "Mitigado parcialmente (verificación en la VM pendiente)" a **"Mitigado — verificado en la VM"**. Sigue sin resolver el problema de fondo (no hay sesión autenticada que ligue la acción a una identidad real; `analyst` sigue siendo un campo declarado por el cliente) — eso permanece pendiente para el Laboratorio 4.
