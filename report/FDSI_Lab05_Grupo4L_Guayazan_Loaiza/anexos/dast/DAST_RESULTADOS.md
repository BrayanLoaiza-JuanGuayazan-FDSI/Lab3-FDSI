# DAST pasivo con OWASP ZAP Baseline (Lab 5)

## Configuración

| Dato | Valor |
|---|---|
| Fecha | 2026-11-10, 23:48 a 23:50 hora Colombia (2026-11-11 04:48 a 04:50 UTC) |
| Versión evaluada | `main`, commit `27a871adde809ff74bbc2746be73d8c39c740927` |
| Aplicación | Nginx 1.26.3, Flask 3.1.3, Werkzeug 3.1.9, Python 3.12 |
| Entorno | Staging local en Docker, red aislada `lab5-dast`, datos ficticios. Es la alternativa local que permite la guía (sin staging HTTPS) |
| Herramienta | OWASP ZAP 2.17.0, `zap-baseline.py` (solo análisis pasivo, sin ataques activos) |

| Análisis | Objetivo | Credencial | Reporte |
|---|---|---|---|
| 1 | `http://lab5-dast-target/` | Sin credencial | `reportes/zap-frontend.html` |
| 2 | `/api/alerts/alerts` | `X-API-Key` de staging | `reportes/zap-api-alerts.html` |
| 3 | `/api/actions/actions` | `X-API-Key` de staging | `reportes/zap-api-actions.html` |

En los análisis 2 y 3 la credencial se agregó con la regla `replacer` de ZAP. Los reportes muestran 90 % de respuestas 2xx y 9 % 3xx, sin 401, por lo que ZAP sí entró a las APIs.

## Resultado general

| Análisis | High | Medium | Low | Informational | Reglas PASS |
|---|---|---|---|---|---|
| Frontend | 0 | 0 | 4 | 2 | 64 |
| API Alerts | 0 | 0 | 5 | 2 | 63 |
| API Actions | 0 | 0 | 4 | 2 | 64 |

No aparecieron vulnerabilidades High ni Medium. FAIL-NEW fue 0 en los tres análisis.

## Clasificación de las alertas

| ID | Alerta ZAP | CWE | Riesgo ZAP | Dónde | Relevancia para el proyecto |
|---|---|---|---|---|---|
| D-01 | Storable and Cacheable Content | 524 | Informational | Frontend y APIs, incluida `/api/alerts/alerts` | **Relevante, baja.** Las respuestas autenticadas del API no envían `Cache-Control` (verificado con `curl`). Una caché intermedia podría guardarlas. Medida sugerida: `Cache-Control: no-store` en `/api/`. |
| D-02 | Permissions Policy Header Not Set | 693 | Low | Frontend y rutas estáticas | **Endurecimiento, baja.** El dashboard no usa cámara, micrófono ni geolocalización, así que se puede restringir con una línea en Nginx. |
| D-03 | Cross-Origin-Embedder / Opener / Resource-Policy (3 alertas) | 693 | Low | Frontend y APIs | **Baja relevancia.** El sitio no carga recursos de otros orígenes y ya tiene CSP y `frame-ancestors 'none'`. |
| D-04 | Private IP Disclosure | 497 | Low | `/api/alerts/alerts` | **Falso positivo.** `192.168.1.105` es un dato ficticio del simulador: el IOC de la alerta ALT-002 (`src/alerts-api/app.py:44`). No es una IP de la infraestructura. |
| D-05 | Modern Web Application | n/a | Informational | Frontend | **Sin riesgo.** Solo indica que la página usa JavaScript para generar contenido. |

## Limitaciones

- Es un análisis pasivo: ZAP revisa respuestas, no intenta explotar nada. Un resultado sin High ni Medium no demuestra ausencia de vulnerabilidades.
- El sitio corre por HTTP en local, por lo que las reglas de TLS no aportan información. La falta de HTTPS sigue como riesgo residual del proyecto.
- El commit evaluado no incluye el cambio de Nginx del PR #9, que seguía abierto.
- No se modificó la aplicación ni se hicieron pruebas destructivas.

## Evidencia

- `reportes/`: tres reportes HTML, JSON y la salida de terminal de cada análisis.
- `capturas/01-ejecucion-zap-terminal.png`: salida real del análisis 1, renderizada a imagen desde `zap-frontend-terminal.txt`, omitiendo las líneas PASS.
- `capturas/02` a `07`: resumen y tabla de alertas de cada reporte HTML.
