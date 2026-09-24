# Comparación antes / después — Fase F (retest final)

**Antes** (Fase C, `evidence/red/nmap_ports_extra.*`) vs **Después** (Fase F, `evidence/retest/nmap_final_after_fix.*`), tras aplicar en conjunto: hardening de Nginx (Fase E, esta sesión) + fix de código de `alerts-api`/`actions-api` (bind loopback, `debug=False`, sin `/debug/env`) + UFW restringido a `192.168.17.0/24` (rama del equipo).

| Elemento | Antes | Después |
|---|---|---|
| Puerto 80 (Nginx) | `nginx 1.28.3 (Ubuntu)` — versión y SO expuestos | `nginx` — sin versión ni SO |
| Puerto 5000 (Alerts API) | **open**, `Werkzeug 3.1.8 / Python 3.14.4` (bind 0.0.0.0) | **filtered** — bloqueado por UFW, y el servicio ya solo escucha en 127.0.0.1 |
| Puerto 5001 (Actions API) | **open**, `Werkzeug 3.1.8 / Python 3.14.4` | **filtered** |
| `GET :5000/debug/env` directo | `200 OK`, expone `os.environ` completo | `000` — conexión rechazada, el puerto ni siquiera responde desde la red |
| `GET /` (dashboard) | `200 OK` | `200 OK` — sin regresión funcional |
| `GET /api/alerts/alerts` (vía proxy) | `200 OK` | `200 OK` — sin regresión funcional |
| Headers de seguridad | Ausentes (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) | Presentes los tres |
| `/.git/config` | Habría dado 200 (fallback SPA) | `403 Forbidden` |
| CSP (Content-Security-Policy) | Ausente | **Sigue ausente** — pendiente, no se agregó en este hardening |

## Conclusión

La superficie de ataque expuesta directamente a la red pasó de **3 puertos abiertos** (80, 5000, 5001, con fingerprint completo de versión) a **1 puerto abierto** (80, sin fingerprint), sin afectar la funcionalidad legítima del dashboard ni de las APIs consumidas a través del proxy. El endpoint de diagnóstico intencional (`/debug/env`) queda completamente inalcanzable desde la red en vez de solo "escondido".

Pendiente explícito para Lab 4: TLS/HTTPS, autenticación/autorización, y Content-Security-Policy.
