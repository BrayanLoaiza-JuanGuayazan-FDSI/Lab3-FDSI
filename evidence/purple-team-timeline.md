# Línea de tiempo Purple Team — Lab 3 FDSI (sesión 2026-09-24)

Todas las horas en UTC. Fuentes: `evidence/red/`, `evidence/blue/`, `evidence/retest/`.

| Hora UTC | Acción Red Team | Evidencia Blue Team | Conclusión |
|---|---|---|---|
| 02:58:31 | Nmap `-sV` puerto 80 (`nmap_port80`) | `access.log`: sondas NSE de fingerprinting — `GET /nmaplowercheck...`, `GET /NmapUpperCheck...`, `GET /Nmap/folder/check...`, `POST /sdk` (405) | `-sV` sí completa el handshake TCP y manda sondas HTTP reales, por eso aparece en `access.log` (a diferencia de un SYN scan `-sS` puro, que no lo haría) |
| 02:59:09–03:00:26 | Nmap `-sV` puertos 80, 5000, 5001 (`nmap_ports_extra`) | Mismas sondas NSE repetidas a las 03:00:09 en `access.log`; Werkzeug/Python fingerprint solo visible en la salida de Nmap, **no** en `access.log` | Los puertos 5000/5001 no pasan por Nginx, así que Blue Team **no ve nada** en `access.log` de ese reconocimiento — solo lo detecta quien mira el tráfico de red directo (pcap) o los logs propios de Flask |
| 03:04:40 | `curl -i http://.../` (`curl_home.txt`) | `access.log`: `GET / HTTP/1.1" 200 9083/9050 ... curl/8.20.0` | Correlación exacta comando ↔ log confirmada |
| 03:05:06 | `curl -I .../api/alerts/alerts` (`curl_headers.txt`) | `access.log`: `HEAD /api/alerts/alerts HTTP/1.1" 200` | `curl -I` genera `HEAD`, no `GET` — detalle que Blue Team necesita para distinguir el tipo de sondeo |
| 03:05:33 | `curl -s .../api/alerts/alerts` (`curl_alerts_body.json`) | `access.log`: `GET /api/alerts/alerts HTTP/1.1" 200 1711` | Cuerpo JSON completo de las 5 alertas obtenido sin autenticación |
| 03:26:59–03:34:31 | ZAP Manual Explore (navegación pasiva + refresco automático del dashboard) | `zap-report.html`/`.csv`: alertas pasivas — CSP ausente, X-Frame-Options ausente, X-Content-Type-Options ausente, Server leak | Confirma H4 (Information Disclosure) sin ejecutar Active Scan |
| 03:52:02–03:52:32 | `curl /` y `curl /api/alerts/alerts` durante la ventana de captura | `lab3-http.pcap` (104 paquetes) + `access.log` a las 03:52:05 | Tráfico HTTP visible en texto claro en Wireshark — confirma H1/H2 (Information Disclosure / sin confidencialidad) |
| 03:52:25 | 6× `curl /api/alerts/no-existe` (ruta inexistente bajo la API) | `detection_404.txt`: 6 respuestas 404 de la misma IP agrupadas en el mismo segundo | Regla de detección ("5+ 404 en 5 min") validada con datos reales |
| 03:54:53 | *(Blue Team)* aplica hardening de Nginx y recarga el servicio | `journal_nginx.txt`: evento de reload registrado por systemd | Corrección aplicada y verificable en el log del propio sistema, no solo "de palabra" |
| 03:55:03 | Retest parcial (solo Nginx): `curl -I /`, `curl /.git/config` | `headers_after.txt`, `hidden_path.txt`: headers de seguridad presentes; `/.git/config` → 403 | Hardening de Nginx verificado, aunque los microservicios Flask seguían expuestos en 5000/5001 |
| 04:02:42 | *(Builder)* redespliega con el fix de código (Flask a loopback, sin `debug`, sin `/debug/env`) + UFW restringido a `192.168.17.0/24` | Salida de `deploy.sh`: los 3 servicios `active`, UFW `active` con regla `80/tcp ALLOW 192.168.17.0/24` | Corrección de código y de red aplicadas juntas |
| 04:03:xx | Retest final: `nmap -sV -p 80,5000,5001`, `curl` directo a `:5000/debug/env` | `nmap_final_after_fix`: 5000 y 5001 pasan de `open` a **`filtered`**; `/debug/env` directo → `000` (conexión rechazada) | Superficie de ataque expuesta a la red reducida de 3 puertos con fingerprint completo a 1 puerto sin versión, sin romper el dashboard ni las APIs (ambas siguen en 200 vía proxy) |

## Qué no apareció en `access.log` y por qué

- El reconocimiento de puertos 5000/5001 (fase inicial) no deja rastro en `access.log` de Nginx porque esos servicios no pasan por el proxy — solo aparecen en la salida de Nmap o en un log propio de Flask.
- Un hipotético SYN scan puro (`-sS`, no usado aquí) tampoco habría dejado rastro en `access.log`, porque no completa el handshake TCP a nivel de aplicación — esto es una limitación conocida de basar la detección solo en logs HTTP.
