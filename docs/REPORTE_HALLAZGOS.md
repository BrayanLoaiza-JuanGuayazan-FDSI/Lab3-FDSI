# Informe técnico de hallazgos

**Proyecto:** CrowdStrike Falcon Alert Simulator (base del Lab 3, reutilizada en el Lab 5)  
**Integrantes:** Brayan Loaiza Leal, Juan Sebastián Guayazán Clavijo  
**Repositorio / commit:** `BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI`. Línea base `6440081` (rama `chore/estructura-minima`). Remediación en la rama `security/lab-fsi`.  
**Entorno autorizado:** staging local en Docker (Nginx + las dos APIs Flask, datos ficticios, solo `127.0.0.1`). Es la alternativa local que permite la guía cuando no hay staging HTTPS. Definición en [`evidence/lab5/staging-local/`](../evidence/lab5/staging-local/).  
**Fecha:** 2026-11-10

## Resumen ejecutivo

Los tres riesgos principales eran:

1. **Cualquiera podía leer y modificar datos sin autenticarse (CWE-306).** Un cliente anónimo creaba alertas y registraba acciones a nombre de cualquier analista.
2. **XSS almacenado en el dashboard (CWE-79).** Una alerta con HTML se ejecutaba en el navegador del analista. Se confirmó en Chromium.
3. **Cadena de suministro del pipeline.** Seis acciones de GitHub estaban fijadas por tag mutable.

Los tres quedaron corregidos en `security/lab-fsi`, con 44 pruebas de regresión: 31 fallan sobre la línea base y las 44 pasan después de la corrección.

El Log Injection (CWE-117) se corrigió en la Parte 1 (ver F-15).

### Comparación antes y después

| Control | Antes (`6440081`) | Después (`security/lab-fsi`) |
|---|---|---|
| Semgrep (`p/owasp-top-ten`, `p/secrets`) | 15 resultados (línea base) | 2 resultados tras la primera remediación; 0 tras corregir F-16 (`ca6fa69`) |
| OWASP ZAP baseline | 1 Medium, 4 Low, 2 Info | 0 Medium, 4 Low, 2 Info |
| pip-audit | 1 aviso (2 registros del mismo PYSEC) en Flask | 0 avisos |
| `GET /alerts` sin credencial | 200 | 401 |
| `POST /actions` sin credencial | 201 | 401 |
| XSS en Chromium | se ejecuta (`console.log` dispara, 1 `<img>` inyectado) | no se ejecuta (0 `<img>`, payload visible como texto) |
| `severity` fuera del enum | 201 | 400 |
| Header `Server` en las APIs | `Werkzeug/3.1.9 Python/3.12.16`, `FalconSim/1.0` | `api` |
| Pruebas de regresión | 31 fallan, 13 pasan | 44 pasan |

Evidencia: [`evidence/lab5/antes/`](../evidence/lab5/antes/) y [`evidence/lab5/despues/`](../evidence/lab5/despues/).

## Metodología

Identificación del alcance → SAST (Semgrep 1.184.0) → detección de secretos (Gitleaks en CI) → SCA (pip-audit) → DAST pasivo (ZAP baseline sobre staging local) → validación manual no destructiva con `curl` y Chromium → corrección por commits separados → reescaneo.

Solo se usaron peticiones inocuas y datos ficticios. La carga de prueba del XSS es `console.log(1)`.

## Matriz de hallazgos

La severidad es la asignada por el equipo según impacto real. Semgrep reporta `WARNING` o `MEDIUM` en su campo de severidad y `HIGH` o `LOW` en el metadato de impacto.

| ID | Hallazgo | Origen | CWE | Severidad | Clasificación | Estado | Commit |
|---|---|---|---|---|---|---|---|
| F-03 | Endpoints sin autenticación | Revisión manual | CWE-306 | **Alta** | Verdadero | Corregido | `edffa29` |
| F-01 | XSS almacenado en el dashboard | Revisión manual, validado en navegador | CWE-79 | **Alta** | Verdadero | Corregido | `bcf7656` |
| F-12 | 6 acciones de GitHub por tag mutable | Semgrep (impacto HIGH) | CWE-1357 | Media | Verdadero | Corregido | `13226ba` |
| F-09 | Sin `Content-Security-Policy` | ZAP (Medium, confianza High) | CWE-693 | **Media** | Verdadero | Corregido | `6766985` |
| F-11 | Header `Server` identifica el stack | Validación manual | CWE-200 | **Media** | Verdadero | Corregido | `07f5b73` |
| F-02 | `create_alert` sin validar entrada | Revisión manual | CWE-20 | **Media** | Verdadero | Corregido | `b05f7b3` |
| F-13 | Dependabot sin periodo de espera | Semgrep (severidad MEDIUM) | CWE-1357 | Baja | Verdadero | Corregido | `13226ba` |
| F-06 / SCA | Flask 3.0.3 con aviso y Werkzeug sin fijar | pip-audit | CVE-2026-27205 | Baja | Verdadero, no explotable aquí | Corregido | `f971d02` |
| F-14 | Modo debug de Flask | Lista de la tarea | CWE-489 | n/a | Ya estaba corregido | Prueba de regresión | `0efcada` |
| F-15 | Log Injection en las 2 APIs | Revisión manual | CWE-117 | Media | Verdadero | **Corregido** | `326e488` |
| F-16 | `proxy_set_header Host $host` en config viva (2) | Semgrep | CWE-290 | Baja | Verdadero, bajo impacto | **Corregido** | `ca6fa69` |
| **F-17** | Los mismos `Host $host` en `evidence/` (4) | Semgrep | CWE-290 | n/a | **Falsa alarma** | Excluido del escaneo | `13226ba` |
| **F-18** | Credencial en script de validación | Gitleaks | CWE-798 | n/a | **Falsa alarma** | Documentado | n/a |

Meta de remediación: **2 High** (F-03, F-01) cumplida. **4 Medium** completas: F-09, F-11, F-02 (Parte 2) y F-15 (Parte 1 — Log Injection). ✅ Meta alcanzada.

## Hallazgo F-03

- **Título:** endpoints de negocio accesibles sin autenticación.
- **Categoría OWASP/CWE:** A07:2021 Identification and Authentication Failures, CWE-306.
- **Severidad y justificación:** Alta. Es explotable por cualquier cliente con acceso de red, sin requisitos previos, y permite cerrar o escalar alertas suplantando a un analista.
- **Evidencia minimizada:** `POST /api/actions/actions` sin credencial devolvía `201`; `GET /api/alerts/alerts` devolvía `200`.
- **Impacto:** confidencialidad (lectura de alertas) e integridad (creación de alertas y acciones falsas).
- **Pasos de validación segura:** ejecutar [`evidence/lab5/validacion-manual.sh`](../evidence/lab5/validacion-manual.sh) contra el staging local.
- **Corrección:** `edffa29`. Todas las rutas excepto `/health` exigen el header `X-API-Key`, comparado en tiempo constante con `LAB_API_KEY`. Si la variable no está configurada, se rechaza todo. `deploy.sh` genera la clave una sola vez en `/etc/lab3-fdsi.env` (permisos 0600).
- **Resultado del reescaneo:** las mismas peticiones devuelven `401`; con la clave válida, `200`; `/health` sigue en `200`.

## Hallazgo F-01

- **Título:** XSS almacenado por uso de `innerHTML` con datos del API.
- **Categoría OWASP/CWE:** A03:2021 Injection, CWE-79.
- **Severidad y justificación:** Alta. Ejecuta código en el navegador del analista. Semgrep no lo detectó con estas reglas; se encontró por revisión manual.
- **Evidencia minimizada:** en Chromium headless, `type` con `<img src=x onerror=console.log(1)>` insertó un `<img>` en la tabla y la consola registró `1`.
- **Impacto:** confidencialidad e integridad de la sesión del analista.
- **Pasos de validación segura:** crear la alerta con la carga inocua en el staging local y abrir el dashboard.
- **Corrección:** `bcf7656`. Las filas se construyen con `createElement` y `textContent`, y `6766985` añade una CSP sin `unsafe-inline` como segunda barrera.
- **Resultado del reescaneo:** 0 `<img>` inyectados, el texto aparece literal, y la consola queda sin errores ni violaciones de CSP.

## Hallazgo F-17 (falsa alarma)

- **Título:** `request-host-used` reportado en archivos de evidencia.
- **Análisis:** 4 de los 6 resultados de esta regla están en `evidence/blue/nginx-config-before.conf` y `evidence/server-nginx.txt`, copias históricas del Lab 3 que no se despliegan.
- **Decisión:** no se editan porque son evidencia. Se excluyen del escaneo con `.semgrepignore`. Los 2 resultados de la configuración viva se registraron como F-16. La corrección posterior reemplazó `$host` por `$proxy_host` en las dos directivas activas; el commit `ca6fa69` corrigió F-16 y el reescaneo de Semgrep quedó en 0.

## Hallazgo F-18 (falsa alarma)

- **Título:** Gitleaks `curl-auth-header` en `evidence/lab5/validacion-manual.sh:7`.
- **Análisis:** el valor detectado es `clave-incorrecta`, la credencial inválida a propósito con la que el script comprueba que el API responde `401`. No da acceso a nada.
- **Decisión:** se mantiene y se documenta. El job de Gitleaks termina en verde aunque haya resultados (`|| true`), por lo que hay que revisar el artefacto.

## Resultado en CI

Corrida [42908756960](https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI/actions/runs/42908756960) sobre el Pull Request #3: pruebas de regresión 44 de 44, Semgrep 1.185.0 con 2 resultados de F-16 en esa ejecución intermedia, y Gitleaks con 1 resultado (F-18). En el reescaneo posterior a `ca6fa69`, Semgrep reportó 0 resultados.

## Decisión SCA (Flask y Werkzeug)

- **Dependencia:** Flask 3.0.3, aviso PYSEC-2026-2151 / CVE-2026-27205, corregido en 3.1.3. Werkzeug era transitiva y no estaba fijada.
- **¿Aplica al código?** No es explotable hoy. El aviso exige usar el objeto `session` detrás de una caché, y ninguna de las APIs usa `session`.
- **Medida:** se actualizó a `flask==3.1.3` y se fijó `werkzeug==3.1.9`, porque el cambio es pequeño y las 44 pruebas lo validan. pip-audit queda sin avisos.

## Limitaciones y riesgo residual

- **Sin TLS (F-10 del plan):** la API key viaja en claro por HTTP. La autenticación reduce el riesgo pero no lo elimina hasta tener HTTPS.
- **Clave compartida:** no hay identidad por analista, así que el campo `analyst` sigue siendo declarativo (CWE-862, F-04).
- **Staging:** el DAST y la validación corrieron en Docker local, no en la VM del laboratorio, que no estuvo accesible. `deploy.sh` solo pasó verificación de sintaxis (`bash -n`).
- **ZAP pasivo** solo vio el frontend. Tras la corrección las APIs responden `401` al escáner, por lo que no analiza sus respuestas autenticadas.
- **Servidor de desarrollo:** las APIs siguen usando el servidor de Werkzeug, detrás de Nginx y solo en loopback.

## Reflexión final

Las herramientas encontraron problemas de configuración y de dependencias: tags mutables, ausencia de CSP y un aviso en Flask. Los dos riesgos más graves, la falta de autenticación y el XSS, no los marcó Semgrep con las reglas usadas; salieron de revisar el código y probar la aplicación. Un pipeline en verde no significa una aplicación segura.

Semgrep también contó copias históricas como hallazgos nuevos, así que cada resultado requiere triage. La integración al ciclo de desarrollo queda con SAST, secretos y pruebas de regresión en cada Pull Request.
