#!/bin/bash
# deploy.sh — Script de despliegue Lab 3 FDSI
# Uso: chmod +x deploy.sh && sudo ./deploy.sh

set -e
echo "=== Lab 3 FDSI — Deploy ==="
echo "Fecha: $(date)"
echo "Usuario: $(whoami)"
echo "Host: $(hostname)"

# 1. Actualizar e instalar dependencias
echo "[1/7] Instalando dependencias..."
apt-get update -qq
apt-get install -y nginx python3 python3-pip python3-venv -qq

# 2. Copiar frontend a /var/www/lab3
echo "[2/7] Desplegando frontend..."
mkdir -p /var/www/lab3
cp frontend/index.html /var/www/lab3/
chmod -R 755 /var/www/lab3

# 3. Configurar Nginx
echo "[3/7] Configurando Nginx..."
cp nginx/lab3-fdsi.conf /etc/nginx/sites-available/lab3-fdsi
ln -sf /etc/nginx/sites-available/lab3-fdsi /etc/nginx/sites-enabled/lab3-fdsi
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
systemctl enable nginx

# 4. Instalar dependencias Python para microservicios
echo "[4/7] Instalando dependencias Python..."
cd services/alerts-api
pip3 install -r requirements.txt -q --break-system-packages
cd ../../
cd services/actions-api
pip3 install -r requirements.txt -q --break-system-packages
cd ../../

# 5. Crear servicios systemd
echo "[5/7] Configurando servicios systemd..."
WORKDIR=$(pwd)
# El proyecto vive dentro del $HOME de quien lo clonó (permisos 750 en Ubuntu
# moderno); www-data no puede atravesar esa carpeta ni escribir los .log ahi,
# asi que los servicios corren como el usuario dueño del repo.
SERVICE_USER=${SUDO_USER:-$(whoami)}

cat > /etc/systemd/system/alerts-api.service << EOF
[Unit]
Description=FDSI Lab3 Alerts API
After=network.target

[Service]
User=$SERVICE_USER
WorkingDirectory=$WORKDIR/services/alerts-api
ExecStart=/usr/bin/python3 app.py
Restart=always
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/actions-api.service << EOF
[Unit]
Description=FDSI Lab3 Actions API
After=network.target

[Service]
User=$SERVICE_USER
WorkingDirectory=$WORKDIR/services/actions-api
ExecStart=/usr/bin/python3 app.py
Restart=always
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable alerts-api actions-api
systemctl restart alerts-api actions-api

# 6. Firewall (UFW): reduce la superficie de ataque a 80/TCP desde el segmento
#    autorizado del laboratorio. Los microservicios ya solo escuchan en 127.0.0.1.
#    Uso: sudo LAB_CIDR=192.168.17.0/24 ./deploy.sh
#    Si LAB_CIDR no está definido no se toca el firewall, para no bloquear el acceso.
echo "[6/7] Configurando firewall..."
if [ -n "${LAB_CIDR:-}" ]; then
    apt-get install -y ufw -qq
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow OpenSSH
    ufw allow from "$LAB_CIDR" to any port 80 proto tcp
    ufw --force enable
    ufw status numbered
else
    echo "LAB_CIDR no definido: se omite la configuración de UFW."
fi

# 7. Verificación
echo "[7/7] Verificando despliegue..."
sleep 2
echo "Nginx: $(systemctl is-active nginx)"
echo "Alerts API: $(systemctl is-active alerts-api)"
echo "Actions API: $(systemctl is-active actions-api)"
echo ""
echo "=== Verificaciones HTTP ==="
curl -s -o /dev/null -w "Frontend (HTTP 80): %{http_code}\n" http://localhost/
curl -s -o /dev/null -w "Alerts API (5000): %{http_code}\n" http://localhost:5000/health
curl -s -o /dev/null -w "Actions API (5001): %{http_code}\n" http://localhost:5001/health

echo ""
echo "✅ Despliegue completado."
echo "IP pública: $(curl -s ifconfig.me 2>/dev/null || echo 'no disponible')"
