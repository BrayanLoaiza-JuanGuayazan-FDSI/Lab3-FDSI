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
3. **L3 — Navegador (JS del dashboard) → Alerts API directo:** ~~el frontend llamaba a `http://<host>:5000` directamente~~ **[CORREGIDO y VERIFICADO en Parte I]** — se detectó en despliegue real (VM Ubuntu 26.04.1, `192.168.17.129`) que esta llamada cruzada de puerto era bloqueada por CORS en el navegador (Flask no envía `Access-Control-Allow-Origin`), mientras que `curl` sí funcionaba, ocultando el problema en pruebas de servidor a servidor. Se corrigió `frontend/index.html` para consumir la API vía el proxy de Nginx (`/api/alerts/`), quedando same-origin. Retest confirmado por captura de navegador: dashboard muestra las 5 alertas (1 CRITICAL, 2 HIGH, 1 MEDIUM, 1 LOW) tras el fix. Los puertos 5000/5001 siguen expuestos y sin autenticación para acceso directo (curl, Kali), por lo que la frontera de confianza original sigue siendo válida como amenaza, solo que ya no la atraviesa el propio dashboard.

## Superficie de ataque (línea base, antes del hardening)

- Puertos TCP expuestos: 80 (Nginx), 5000 y 5001 (Flask, bind `0.0.0.0`).
- Endpoints enumerables sin autenticación: `/alerts`, `/alerts/{id}`, `/alerts/severity/{level}`, `/actions`, `/actions/{id}`, `/actions/alert/{id}`, y el endpoint de diagnóstico `/debug/env`.
- Ambos microservicios corren con `app.run(..., debug=True)` — expone el debugger interactivo de Werkzeug si ocurre una excepción no controlada.
- Sin `server_tokens off`, sin `autoindex off` explícito, sin cabeceras de seguridad (CSP, X-Frame-Options, etc.) en la configuración actual de Nginx.

## Superficie de ataque vigente (después del retest)

- Solo `80/tcp` (Nginx) es alcanzable, y únicamente desde `LAB_CIDR` (UFW). Los puertos 5000/5001 aparecen `filtered` y los servicios escuchan en `127.0.0.1`.
- Endpoints enumerables sin autenticación: los de `/api/alerts/` y `/api/actions/` vía Nginx. `/debug/env` ya no existe.
- Respuestas sin versión de Nginx y con `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy`; sigue sin Content-Security-Policy.
- El tráfico sigue en HTTP sin cifrar. Comparación completa en `evidence/retest/comparacion-antes-despues.md`.

## Modelo de amenazas STRIDE

La matriz de hipótesis STRIDE (con elemento afectado, evidencia y mitigación propuesta) vive en
`threat-model/threat-model.xlsx` (hojas *Threats*, *Mitigation Candidates* e *Improvements*), no en este archivo.

## Estado de los riesgos

Estado a la fecha de la retest (detalle por amenaza en la columna *Estado* de la hoja *Threats*):

- **Corregido:** T06 (`/debug/env` eliminado, `server_tokens off`), T09 (puertos 5000/5001 filtrados y servicios en loopback), T10 (`debug=False`). Evidencia: `evidence/retest/`.
- **Mitigado parcialmente:** T05 (`source_ip` y `X-Real-IP` en logs; falta probarlo en la VM y la identidad autenticada).
- **Pendiente para Lab 4:** T01 (HTTP en texto claro, demostrado en `evidence/blue/lab3-http.pcap`), T02, T03, T04 y T08 (sin identidad, autenticación ni autorización).
- **Pendiente para Lab 4/5:** T07 (servidor de desarrollo y sin límite de tasa).
- **Aceptado en el Lab 3:** que el servicio siga sin HTTPS ni autenticación, porque la guía los reserva al Lab 4. Por eso T01–T04 y T08 quedan abiertas y no cerradas.
- **Pendiente:** Content-Security-Policy, no incluida en este hardening.

## Notas

- La evidencia de campo (Nmap, curl, ZAP pasivo, PCAP, logs, regla de detección, retest y línea de tiempo Purple Team) está en `evidence/` y `reports/zap-passive/`.
