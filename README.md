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

El sistema expone vulnerabilidades intencionales (sin auth, sin TLS, endpoint `/debug/env`) para que el Red Team las identifique y el Blue Team las mitigue en laboratorios posteriores.

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

# Verificar
nginx -v
systemctl status nginx --no-pager
systemctl status alerts-api --no-pager
systemctl status actions-api --no-pager
curl -I http://localhost
```

---

## URL publicada

`http://<IP-DEL-SERVIDOR>/`  
Alerts API: `http://<IP-DEL-SERVIDOR>:5000/alerts`  
Actions API: `http://<IP-DEL-SERVIDOR>:5001/actions`

---

## Endpoints de la API

### Alerts API (puerto 5000)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alerts` | Listar todas las alertas |
| GET | `/alerts/{id}` | Detalle de una alerta |
| GET | `/alerts/severity/{level}` | Filtrar por severidad |
| GET | `/alerts?status=open` | Filtrar por estado |
| POST | `/alerts` | Crear nueva alerta |
| GET | `/debug/env` | ⚠️ Expone variables de entorno (vulnerabilidad intencional) |

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

## Limitaciones de seguridad conocidas (intencionales)

- ❌ Sin autenticación en ningún endpoint
- ❌ Sin HTTPS / TLS
- ❌ Endpoint `/debug/env` expone variables de entorno del servidor
- ❌ Sin validación de entrada en campos de texto libre
- ❌ Sin rate limiting
- ❌ Sin cabeceras de seguridad HTTP (CSP, HSTS, X-Frame-Options)
- ❌ CORS abierto (permite cualquier origen)
- ❌ Datos almacenados en memoria (sin persistencia)
- ❌ Logs sin cifrar ni control de acceso

Estas vulnerabilidades serán identificadas por el Red Team y mitigadas progresivamente en los laboratorios 4 y 5.
