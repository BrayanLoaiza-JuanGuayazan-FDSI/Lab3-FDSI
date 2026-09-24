# Preguntas de análisis — Lab 3

Respuestas basadas en la evidencia de `evidence/red/`, `evidence/blue/`, `evidence/retest/` y `reports/zap-passive/`.

## 1. ¿Qué pudo observar el Red Team sin explotar ninguna vulnerabilidad?

- **Puertos y servicios** (`nmap -sV`): 80/tcp con `nginx 1.28.3 (Ubuntu)` sobre Linux; antes de la corrección también 5000/5001 abiertos con `Werkzeug 3.1.8 / Python 3.14.4` (`evidence/red/nmap_ports_extra.nmap`).
- **Cabeceras** (`curl -I`): `Server: nginx/1.28.3 (Ubuntu)`, tipo de contenido, tamaño y `ETag` (`evidence/red/curl_headers.txt`).
- **Datos:** el cuerpo JSON completo de las 5 alertas, sin autenticación (`evidence/red/curl_alerts_body.json`).
- **ZAP pasivo:** ausencia de Content-Security-Policy, `X-Frame-Options` y `X-Content-Type-Options`, y la cabecera `Server` revelando tecnología (`reports/zap-passive/`).
- **En el PCAP:** rutas, cabeceras y cuerpos HTTP en texto claro entre `192.168.17.130` y `192.168.17.129` (`evidence/blue/lab3-http.pcap`).

## 2. ¿Qué pruebas de red no aparecieron en `access.log` y por qué?

- El reconocimiento de 5000/5001: esos servicios no pasaban por Nginx, así que solo se vio en la salida de Nmap.
- Un SYN scan puro (`-sS`) no completa el handshake, por lo que no genera una línea de log HTTP. Aquí se usó `-sV`, que sí envía sondas HTTP y por eso apareció (`GET /nmaplowercheck…`).
- Correlación completa en `evidence/purple-team-timeline.md`.

## 3. ¿Qué control aplicado reduce exposición, pero no resuelve el riesgo de HTTP?

`server_tokens off`, los headers defensivos, `autoindex off`, el bind a `127.0.0.1` y el UFW reducen la superficie y el fingerprint (de 3 puertos con versión a 1 puerto sin versión). Pero el tráfico por el puerto 80 sigue viajando sin cifrar: el PCAP posterior a la corrección seguiría mostrando contenido legible. Solo HTTPS resuelve confidencialidad e integridad en tránsito (Lab 4).

## 4. ¿Qué datos necesitaría Blue Team para distinguir curl legítimo de una actividad sospechosa?

Identidad del usuario (hoy no hay autenticación), un inventario de IPs autorizadas, una línea base de rutas y frecuencia normales, y la correlación de `X-Real-IP` con los logs de cada microservicio. El `User-Agent` solo no sirve: lo declara el cliente. Detalle en `evidence/blue/detection-rule.md`.

## 5. ¿Qué amenaza STRIDE debe priorizarse en el Lab 4?

**Spoofing (T02/T03) junto con Elevation of Privilege (T08)**: hoy cualquiera puede registrar una acción como si fuera un analista o cerrar una alerta CRITICAL, y ninguna de las correcciones del Lab 3 lo cambia. Debe ir acompañada de TLS (T01/T04), porque autenticar sin cifrar expondría las credenciales en tránsito.
