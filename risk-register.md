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

## Superficie de ataque

- Puertos TCP expuestos: 80 (Nginx), 5000 y 5001 (Flask, bind `0.0.0.0`).
- Endpoints enumerables sin autenticación: `/alerts`, `/alerts/{id}`, `/alerts/severity/{level}`, `/actions`, `/actions/{id}`, `/actions/alert/{id}`, y el endpoint de diagnóstico `/debug/env`.
- Ambos microservicios corren con `app.run(..., debug=True)` — expone el debugger interactivo de Werkzeug si ocurre una excepción no controlada.
- Sin `server_tokens off`, sin `autoindex off` explícito, sin cabeceras de seguridad (CSP, X-Frame-Options, etc.) en la configuración actual de Nginx.

## Modelo de amenazas STRIDE

La matriz de hipótesis STRIDE (mínimo una por categoría, con elemento afectado,
evidencia y mitigación propuesta) vive en `threat-model/threat-model.xlsx`
(hojas *Threats* y *Mitigation Candidates*), no en este archivo.

## Notas

- Evidencia de campo (PCAP, ZAP pasivo, nmap, logs correlacionados) se agrega en `evidence/red/` y `evidence/blue/` una vez desplegado en la VM y ejecutada la ronda Red/Blue Team (Parte II).
