# Lab 3 FDSI — Red Team vs Blue Team
## CrowdStrike Falcon Alert Simulator

**Fundamentos de Seguridad de la Información (ISIS FDSI-4L) · Grupo 4L · 2026-2, Segundo Tercio**  
Escuela Colombiana de Ingeniería Julio Garavito

> ⚠️ **ADVERTENCIA:** Este sistema es intencionalmente vulnerable. Construido sin autenticación, sin TLS y con endpoints de diagnóstico expuestos, con el único propósito de practicar técnicas de Red Team y Blue Team en un entorno académico controlado. **No usar en producción.**

---

## Propósito del proyecto

Prototipo que simula la recepción, clasificación y registro de alertas ficticias de CrowdStrike Falcon. Permite:

- Consultar alertas de seguridad mediante una API REST
- Registrar acciones de respuesta realizadas por analistas
- Servir un dashboard web de monitoreo

El sistema conserva limitaciones intencionales (sin auth, sin TLS) para que el Red Team las identifique y el Blue Team las mitigue en laboratorios posteriores. En la Parte 2 se redujo la superficie de ataque (ver "Estado de la entrega").

---

## Arquitectura

```
Internet
    │
    ▼
[Nginx :80]  ← Frontend estático (index.html)
    │
    ├── /api/alerts/  → [Alerts API :5000]  (Flask)
    │                       └── alerts.log
    │
    └── /api/actions/ → [Actions API :5001]  (Flask)
                            └── actions.log
```

**Límites de confianza:**
1. Internet → Nginx (puerto 80, HTTP sin TLS)
2. Nginx → Microservicios internos (localhost, sin autenticación)

**Datos ficticios utilizados:**
- 5 alertas de seguridad precargadas (malware, movimiento lateral, escalamiento de privilegios, fuerza bruta, exfiltración)
- 3 acciones de analistas precargadas
- Usuarios ficticios: john.doe, jane.smith, carlos.garcia, maria.torres, contractor01

**Exclusiones (fuera de alcance en Parte I):**
- TLS / HTTPS (se activa en Lab 4)
- Autenticación y autorización
- Base de datos persistente (datos en memoria)
- Integración real con CrowdStrike

---

## Requisitos

- Ubuntu 20.04 o superior
- Python 3.8+
- Nginx
- pip3

---

## Ejecución local (sin servidor)

```bash
# Clonar el repositorio
git clone https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI.git
cd Lab3-FDSI

# Instalar dependencias
pip3 install flask

# Terminal 1 — Alerts API
cd services/alerts-api
python3 app.py

# Terminal 2 — Actions API
cd services/actions-api
python3 app.py

# Terminal 3 — Frontend
cd frontend
python3 -m http.server 8080

# Verificar
curl -I http://localhost:8080
curl http://localhost:5000/alerts
curl http://localhost:5001/actions
```

---

## Procedimiento de despliegue en servidor Linux

```bash
# Clonar en el servidor
git clone https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI.git
cd Lab3-FDSI

# Ejecutar script de despliegue (requiere sudo)
chmod +x deploy.sh
sudo ./deploy.sh

# Con firewall (UFW): permite 80/tcp solo desde el segmento del laboratorio + SSH
sudo LAB_CIDR=192.168.17.0/24 ./deploy.sh

# Verificar
nginx -v
systemctl status nginx --no-pager
systemctl status alerts-api --no-pager
systemctl status actions-api --no-pager
curl -I http://localhost
```

---

## URL publicada

VM Ubuntu Server 26.04.1 LTS en VMware Workstation (red NAT, alcanzable desde el host):

`http://192.168.17.129/`
Alerts API (vía proxy Nginx): `http://192.168.17.129/api/alerts/alerts`
Actions API (vía proxy Nginx): `http://192.168.17.129/api/actions/actions`

> Nota: IP interna de laboratorio (VMware NAT), no una IP pública de Internet. Se
> actualizará si el docente asigna una instancia en la nube para la Parte II.

---

## Endpoints de la API

Los microservicios escuchan solo en `127.0.0.1` (puertos 5000 y 5001) y se consumen a través de Nginx (`/api/alerts/` y `/api/actions/`).

### Alerts API (puerto 5000)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alerts` | Listar todas las alertas |
| GET | `/alerts/{id}` | Detalle de una alerta |
| GET | `/alerts/severity/{level}` | Filtrar por severidad |
| GET | `/alerts?status=open` | Filtrar por estado |
| POST | `/alerts` | Crear nueva alerta |

### Actions API (puerto 5001)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/actions` | Listar todas las acciones |
| GET | `/actions/{id}` | Detalle de una acción |
| GET | `/actions/alert/{alert_id}` | Acciones sobre una alerta |
| POST | `/actions` | Registrar nueva acción |

---

## Integrantes

| Nombre | Rol |
|--------|-----|
| Brayan Loaiza Leal | Ingeniería de Sistemas |
| Juan Sebastián Guayazán Clavijo | Ingeniería de Sistemas |

---

## Modelo de amenazas

Ver [`risk-register.md`](risk-register.md) para activos, actores, límites de confianza y
superficie de ataque. Las matrices de amenazas STRIDE, mitigaciones y la cadena
gap → riesgo → mejora están en `threat-model/threat-model.xlsx`. Diagramas de flujo de datos:
`diagrams/dfd-lab3.png` (arquitectura inicial) y `diagrams/dfd-lab3-fortalecida.png`
(arquitectura fortalecida).

## Estado de la entrega

- **Parte I (actual):** construcción, publicación, estructura de repositorio, evidencia
  de ejecución local y modelo de amenazas inicial.
- **Parte 2 (en curso):** reducción de superficie de ataque implementada en el repo (servicios
  solo en `127.0.0.1`, UFW opcional vía `LAB_CIDR` en `deploy.sh`, sin `/debug/env` ni
  `debug=True`, `source_ip` en las acciones, hardening de Nginx). Pendiente desplegarlo en la VM
  y hacer el retest.
- **Ronda Red/Blue Team (pendiente):** despliegue verificado en VM Ubuntu Server, reconocimiento
  Red Team (Nmap/curl/ZAP pasivo), captura y correlación Blue Team (tcpdump/logs),
  hardening de Nginx y retest. Evidencia en `evidence/red/`, `evidence/blue/` y
  `reports/zap-passive/`.

---

## Limitaciones de seguridad conocidas (intencionales)

- ❌ Sin autenticación en ningún endpoint
- ❌ Sin HTTPS / TLS
- ❌ Sin validación de entrada en campos de texto libre
- ❌ Sin rate limiting
- ❌ Sin CSP ni HSTS (HSTS requiere HTTPS); solo se aplicaron `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy`
- ❌ Servidor de desarrollo de Flask (sin gunicorn)
- ❌ Los endpoints siguen sin autenticación a través del proxy de Nginx (`/api/alerts/`, `/api/actions/`)
- ❌ Datos almacenados en memoria (sin persistencia)
- ❌ Logs sin cifrar ni control de acceso

Estas vulnerabilidades serán identificadas por el Red Team y mitigadas progresivamente en los laboratorios 4 y 5.
