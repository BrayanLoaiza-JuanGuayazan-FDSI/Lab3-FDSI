# Registro de riesgos — Lab 3 FDSI (Parte I)

**Proyecto:** CrowdStrike Falcon Alert Simulator
**Grupo:** 4L — Brayan Loaiza Leal, Juan Sebastián Guayazán Clavijo
**Alcance:** Modelo de amenazas inicial sobre la línea base HTTP sin autenticación (Fases A y B). Las validaciones de Red/Blue Team (Nmap, ZAP, PCAP, logs de servidor) se completan en la Parte II una vez desplegado en la VM Ubuntu del laboratorio.

## Activos

| Activo | Descripción |
|---|---|
| Datos de alertas (`ALERTS`) | Incidentes ficticios de seguridad (severidad, host, usuario, IOC) |
| Datos de acciones (`ACTIONS`) | Bitácora de respuesta de analistas sobre alertas |
| Código fuente | Repositorio Git (`Lab3-FDSI`) |
| Configuración Nginx | `nginx/lab3-fdsi.conf` |
| Procesos backend | `alerts-api` (:5000), `actions-api` (:5001) — Flask dev server |
| Logs | `alerts.log`, `actions.log`, `access.log`, `error.log` |
| Host | VM Ubuntu Server del laboratorio |

## Actores

- **Analista SOC (Blue Team):** consume el dashboard, revisa alertas.
- **Red Team / Kali:** reconocimiento y pruebas autorizadas (nmap, curl, ZAP).
- **Cliente HTTP anónimo:** cualquier origen en la red del laboratorio — no hay diferencia de privilegio porque no existe autenticación.
- **Product/Builder:** mantiene el repositorio y ejecuta `deploy.sh` con sudo.

## Límites de confianza

1. **L1 — Internet/LAN → Nginx (:80):** frontera de red no confiable hacia el host.
2. **L2 — Nginx → microservicios Flask (:5000/:5001):** frontera interna del host; se asume "solo localhost" pero ambos servicios hacen bind en `0.0.0.0`, por lo que **también son alcanzables directamente desde la red**, saltándose esta frontera.
3. **L3 — Navegador (JS del dashboard) → Alerts API directo:** ~~el frontend llamaba a `http://<host>:5000` directamente~~ **[CORREGIDO en Parte I]** — se detectó en despliegue real (VM Ubuntu 26.04.1) que esta llamada cruzada de puerto era bloqueada por CORS en el navegador (Flask no envía `Access-Control-Allow-Origin`), mientras que `curl` sí funcionaba, ocultando el problema en pruebas de servidor a servidor. Se corrigió `frontend/index.html` para consumir la API vía el proxy de Nginx (`/api/alerts/`), quedando same-origin. Los puertos 5000/5001 siguen expuestos y sin autenticación para acceso directo (curl, Kali), por lo que la frontera de confianza original sigue siendo válida como amenaza, solo que ya no la atraviesa el propio dashboard.

## Superficie de ataque

- Puertos TCP expuestos: 80 (Nginx), 5000 y 5001 (Flask, bind `0.0.0.0`).
- Endpoints enumerables sin autenticación: `/alerts`, `/alerts/{id}`, `/alerts/severity/{level}`, `/actions`, `/actions/{id}`, `/actions/alert/{id}`, y el endpoint de diagnóstico `/debug/env`.
- Ambos microservicios corren con `app.run(..., debug=True)` — expone el debugger interactivo de Werkzeug si ocurre una excepción no controlada.
- Sin `server_tokens off`, sin `autoindex off` explícito, sin cabeceras de seguridad (CSP, X-Frame-Options, etc.) en la configuración actual de Nginx.

## Hipótesis STRIDE (mínimo una por categoría)

| ID | STRIDE | Hipótesis técnica | Evidencia / prueba asociada | Mitigación propuesta | Estado |
|---|---|---|---|---|---|
| H1 | **S**poofing | Sin autenticación, cualquiera puede registrar una acción suplantando a un analista (`analyst` es texto libre). | `curl -X POST http://<host>:5001/actions -d '{"alert_id":"ALT-002","analyst":"ceo_boss","action":"close"}'` crea el registro sin verificar identidad. | Autenticación de analistas (roles/sesión) — planificado para Lab 4. | Pendiente Lab 4 |
| H2 | **T**ampering | Sin TLS ni validación de esquema, el contenido de una alerta puede alterarse en tránsito o inyectarse con campos arbitrarios al crearla. | `curl -X POST /alerts` con `severity`, `host`, `ioc` arbitrarios se acepta sin validar tipos/rangos. | Validación de esquema de entrada + HTTPS en Lab 4. | Pendiente Lab 4 |
| H3 | **R**epudiation | La bitácora de acciones no está ligada a una identidad autenticada ni firmada; un analista puede negar haber ejecutado una acción, o esta puede atribuirse a otra persona. | `logging.info` en `actions-api` solo registra el campo `analyst` que envía el propio cliente, sin token de sesión que lo respalde. | Vincular acciones a sesiones autenticadas; log de auditoría append-only con hash-chain. | Pendiente Lab 4 |
| H4 | **I**nformation Disclosure | `/debug/env` expone todas las variables de entorno del servidor; los headers de Flask/Nginx revelan versión y tecnología. | `curl -i http://<host>:5000/debug/env` devuelve el entorno completo del proceso. | Eliminar/proteger `/debug/env` fuera del laboratorio; `server_tokens off`; ocultar banner de Werkzeug. | Mitigado parcialmente (aceptado en Parte I por diseño pedagógico) |
| H5 | **D**enial of Service | El servidor de desarrollo de Flask (single-threaded, no apto para producción) puede saturarse con solicitudes concurrentes; los POST no tienen límite, permitiendo crecimiento no acotado de `ALERTS`/`ACTIONS` en memoria. | Ráfaga de `curl -X POST /alerts` en bucle incrementa la lista sin límite ni rate limiting. | Servir con WSGI de producción (gunicorn) + `limit_req` en Nginx + límite de tamaño/tasa de payload. | Pendiente Lab 4/5 |
| H6 | **E**levation of Privilege | No existe modelo de autorización: cualquier cliente anónimo puede ejecutar acciones "privilegiadas" (cerrar o escalar una alerta CRITICAL) igual que un analista real. | `curl -X POST /actions -d '{"alert_id":"ALT-002","action":"close"}'` cambia el estado de una alerta crítica sin control de rol. | Modelo RBAC (viewer/analyst/admin) con verificación de autorización por tipo de acción — Lab 4. | Pendiente Lab 4 |

## Notas

- Las hipótesis H1–H6 cubren las seis categorías STRIDE exigidas para Parte I. H4 (server tokens, debug env) es la única con mitigación parcial ya aplicable sin adelantar Lab 4; las demás dependen de autenticación/HTTPS y quedan explícitamente pendientes, tal como lo indica el límite pedagógico del laboratorio.
- Evidencia de campo (PCAP, ZAP pasivo, nmap, logs correlacionados) se agrega en `evidence/red/` y `evidence/blue/` una vez desplegado en la VM y ejecutada la ronda Red/Blue Team (Parte II).
