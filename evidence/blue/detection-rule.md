# Regla de detección — Blue Team (Fase D)

## Regla

Generar una señal cuando **una misma IP produce 5 o más respuestas HTTP 404 en una ventana de 5 minutos** en `/var/log/nginx/lab3_access.log`.

- Implementación: [`detect_404.py`](detect_404.py) (ventana deslizante por IP, umbral 5, sin dependencias externas).
- Uso: `python3 evidence/blue/detect_404.py /var/log/nginx/lab3_access.log`
- Consulta rápida equivalente (solo agrega, no aplica la ventana): `awk '$9 ~ /404/ {print $1, $4, $7, $9}' /var/log/nginx/lab3_access.log | sort | uniq -c | sort -nr | head` (salida en [`detection_404.txt`](detection_404.txt)).

## Validación con datos reales

| Prueba | Entrada | Resultado esperado | Resultado |
|---|---|---|---|
| Positiva | `access_tail.txt` (6 × `GET /api/alerts/no-existe` → 404 desde 192.168.17.130 a las 03:52:25 UTC) | Alerta | `ALERTA ... ip=192.168.17.130 404s_en_5min=5` ([`detection_rule_result.txt`](detection_rule_result.txt)) |
| Negativa | El mismo log sin las líneas 404 | Sin alertas | Sin alertas |
| Umbral | Solo 4 líneas 404 | Sin alertas | Sin alertas |

La alerta salta con el 5.º 404, no con el 6.º: el umbral se evalúa en cada evento.

## Limitaciones

- **Solo ve tráfico que pasa por Nginx.** Los puertos 5000/5001 no pasaban por el proxy cuando se hizo el reconocimiento inicial, por lo que esas sondas no dejaron rastro en `access.log` (ver `evidence/purple-team-timeline.md`).
- **No detecta escaneos sin handshake completo** (un SYN scan `-sS` no genera línea de log HTTP).
- **Evasión por baja frecuencia:** 4 solicitudes 404 por ventana, o rotar la IP de origen, no activan la regla.
- **Solo mira el código 404.** Un atacante que enumera rutas existentes (200/403) no se detecta con esta regla.
- **Detrás de NAT o proxy compartido** varias personas aparecen como una sola IP y se suman.
- **Depende de que el log no se manipule ni rote** durante la ventana.

## Falsos positivos

- Un navegador o cliente con enlaces rotos o recursos faltantes (por ejemplo `/favicon.ico`, mapas de fuentes) puede acumular 404 legítimos.
- Una prueba de funcionamiento o monitoreo que consulta rutas aún no desplegadas.
- Una herramienta de revisión autorizada (como el Red Team de este mismo laboratorio): la alerta es correcta, pero no es un incidente real.

## Datos que faltarían para distinguir curl legítimo de actividad sospechosa

User-Agent confiable (es declarado por el cliente y falsificable), identidad del usuario (hoy no hay autenticación), inventario de IPs autorizadas, la cabecera `X-Real-IP` correlacionada con el log de cada microservicio y una línea base de tráfico normal por ruta.
