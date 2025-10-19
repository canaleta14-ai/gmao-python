# 🚀 Guía de Despliegue a Producción - Sistema GMAO

## 📋 Requisitos Previos del Servidor

### Hardware Mínimo Recomendado

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 20 GB SSD
- **Red**: Conexión estable a Internet

### Software Requerido

- **Sistema Operativo**: Ubuntu 20.04 LTS o superior / CentOS 8 / Debian 11
- **Python**: 3.10 o superior
- **PostgreSQL**: 13 o superior
- **Nginx**: 1.18 o superior
- **Git**: Para clonar el repositorio
- **Supervisor** o **systemd**: Para gestión de procesos

---

## 🔧 Paso 1: Preparar el Servidor

### 1.1. Actualizar el Sistema

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 1.2. Instalar Dependencias del Sistema

```bash
# Ubuntu/Debian
sudo apt install -y python3.10 python3.10-venv python3-pip \
    postgresql postgresql-contrib nginx supervisor git \
    build-essential libpq-dev python3-dev

# CentOS/RHEL
sudo yum install -y python3 python3-devel python3-pip \
    postgresql-server postgresql-contrib nginx supervisor git \
    gcc make libpq-devel
```

### 1.3. Configurar PostgreSQL

```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear usuario y base de datos
sudo -u postgres psql <<EOF
CREATE USER gmao_user WITH PASSWORD 'tu_contraseña_segura_aqui';
CREATE DATABASE gmao_db OWNER gmao_user;
GRANT ALL PRIVILEGES ON DATABASE gmao_db TO gmao_user;
\q
EOF
```

---

## 📦 Paso 2: Desplegar la Aplicación

### 2.1. Crear Usuario de Sistema

```bash
# Crear usuario dedicado para la aplicación
sudo useradd -m -s /bin/bash gmao
sudo usermod -aG www-data gmao
```

### 2.2. Clonar el Repositorio

```bash
# Cambiar al usuario gmao
sudo su - gmao

# Clonar el repositorio
git clone https://github.com/canaleta14-ai/gmao-python.git
cd gmao-python/gmao-sistema

# Verificar que estamos en la rama correcta
git checkout master
```

### 2.3. Crear Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip
```

### 2.4. Instalar Dependencias

```bash
# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar servidor WSGI (Gunicorn)
pip install gunicorn psycopg2-binary
```

### 2.5. Configurar Variables de Entorno

```bash
# Crear archivo .env
nano .env
```

Contenido del archivo `.env`:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=genera_una_clave_secreta_muy_larga_y_aleatoria_aqui

# Database Configuration
DATABASE_URL=postgresql://gmao_user:tu_contraseña_segura_aqui@localhost:5432/gmao_db
DB_USER=gmao_user
DB_PASSWORD=tu_contraseña_segura_aqui
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gmao_db

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600

# Email Configuration (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@empresa.com
MAIL_PASSWORD=tu_contraseña_email

# Application Settings
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/home/gmao/gmao-python/gmao-sistema/uploads
LOG_LEVEL=INFO
```

**⚠️ IMPORTANTE**: Cambiar todas las contraseñas y claves por valores seguros.

### 2.6. Generar Clave Secreta

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copiar el resultado y usarlo como `SECRET_KEY` en el archivo `.env`.

---

## 🗄️ Paso 3: Configurar Base de Datos

### 3.1. Ejecutar Migraciones

```bash
# Asegurarse de estar en el entorno virtual
source .venv/bin/activate

# Inicializar migraciones (si es necesario)
flask db init

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migraciones
flask db upgrade
```

### 3.2. Crear Usuario Administrador

```bash
# Ejecutar script de creación de admin
python scripts/crear_admin_postgres.py
```

O crear manualmente desde Python:

```python
from app.factory import create_app
from app.models import User
from app.extensions import db, bcrypt

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@empresa.com',
        password_hash=bcrypt.generate_password_hash('contraseña_segura').decode('utf-8'),
        rol='Administrador',
        activo=True
    )
    db.session.add(admin)
    db.session.commit()
    print("Usuario administrador creado")
```

---

## 🚀 Paso 4: Configurar Gunicorn

### 4.1. Crear Archivo de Configuración

```bash
nano /home/gmao/gmao-python/gmao-sistema/gunicorn_config.py
```

Contenido:

```python
import multiprocessing

# Configuración del servidor
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/home/gmao/gmao-python/gmao-sistema/logs/gunicorn-access.log"
errorlog = "/home/gmao/gmao-python/gmao-sistema/logs/gunicorn-error.log"
loglevel = "info"

# Proceso
daemon = False
pidfile = "/home/gmao/gmao-python/gmao-sistema/gunicorn.pid"
user = "gmao"
group = "www-data"

# Seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

### 4.2. Crear Script de Inicio

```bash
nano /home/gmao/gmao-python/gmao-sistema/start_gunicorn.sh
```

Contenido:

```bash
#!/bin/bash

# Directorio de la aplicación
APP_DIR="/home/gmao/gmao-python/gmao-sistema"
cd $APP_DIR

# Activar entorno virtual
source .venv/bin/activate

# Crear directorio de logs si no existe
mkdir -p logs

# Iniciar Gunicorn
exec gunicorn \
    --config gunicorn_config.py \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    "app.factory:create_app()"
```

Dar permisos de ejecución:

```bash
chmod +x /home/gmao/gmao-python/gmao-sistema/start_gunicorn.sh
```

---

## 🔄 Paso 5: Configurar Supervisor (Gestor de Procesos)

### 5.1. Crear Configuración de Supervisor

```bash
sudo nano /etc/supervisor/conf.d/gmao.conf
```

Contenido:

```ini
[program:gmao]
command=/home/gmao/gmao-python/gmao-sistema/start_gunicorn.sh
directory=/home/gmao/gmao-python/gmao-sistema
user=gmao
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/gmao/gmao-python/gmao-sistema/logs/supervisor.log
stderr_logfile=/home/gmao/gmao-python/gmao-sistema/logs/supervisor-error.log
environment=PATH="/home/gmao/gmao-python/gmao-sistema/.venv/bin"
```

### 5.2. Recargar y Iniciar Supervisor

```bash
# Recargar configuración
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar la aplicación
sudo supervisorctl start gmao

# Verificar estado
sudo supervisorctl status gmao
```

---

## 🌐 Paso 6: Configurar Nginx (Proxy Inverso)

### 6.1. Crear Configuración de Nginx

```bash
sudo nano /etc/nginx/sites-available/gmao
```

Contenido:

```nginx
# Redirección HTTP a HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name tu-dominio.empresa.com;

    # Redireccionar todo el tráfico a HTTPS
    return 301 https://$server_name$request_uri;
}

# Configuración HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name tu-dominio.empresa.com;

    # Certificados SSL (Let's Encrypt recomendado)
    ssl_certificate /etc/letsencrypt/live/tu-dominio.empresa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.empresa.com/privkey.pem;

    # Configuración SSL segura
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logs
    access_log /var/log/nginx/gmao-access.log;
    error_log /var/log/nginx/gmao-error.log;

    # Tamaño máximo de subida
    client_max_body_size 20M;

    # Archivos estáticos
    location /static {
        alias /home/gmao/gmao-python/gmao-sistema/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Archivos subidos
    location /uploads {
        alias /home/gmao/gmao-python/gmao-sistema/uploads;
        internal;
    }

    # Proxy a Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 6.2. Habilitar Sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/gmao /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## 🔒 Paso 7: Configurar SSL con Let's Encrypt (Opcional pero Recomendado)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d tu-dominio.empresa.com

# Renovación automática (ya configurada por defecto)
sudo systemctl enable certbot.timer
```

---

## 🔥 Paso 8: Configurar Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable

# Verificar estado
sudo ufw status
```

---

## 📊 Paso 9: Configurar Logs y Monitoreo

### 9.1. Rotación de Logs

```bash
sudo nano /etc/logrotate.d/gmao
```

Contenido:

```
/home/gmao/gmao-python/gmao-sistema/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 gmao www-data
    sharedscripts
    postrotate
        supervisorctl restart gmao > /dev/null
    endscript
}
```

### 9.2. Monitoreo Básico

```bash
# Ver logs en tiempo real
tail -f /home/gmao/gmao-python/gmao-sistema/logs/gunicorn-error.log
tail -f /var/log/nginx/gmao-error.log

# Ver estado de la aplicación
sudo supervisorctl status gmao

# Ver procesos
ps aux | grep gunicorn
```

---

## 🔄 Paso 10: Script de Actualización

Crear script para actualizaciones futuras:

```bash
nano /home/gmao/update_app.sh
```

Contenido:

```bash
#!/bin/bash

echo "🔄 Actualizando aplicación GMAO..."

# Ir al directorio de la aplicación
cd /home/gmao/gmao-python/gmao-sistema

# Hacer backup de la base de datos
echo "📦 Haciendo backup de la base de datos..."
pg_dump -U gmao_user gmao_db > backups/gmao_db_$(date +%Y%m%d_%H%M%S).sql

# Obtener últimos cambios
echo "📥 Obteniendo últimos cambios..."
git fetch origin
git pull origin master

# Activar entorno virtual
source .venv/bin/activate

# Actualizar dependencias
echo "📦 Actualizando dependencias..."
pip install -r requirements.txt --upgrade

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
flask db upgrade

# Recolectar archivos estáticos si es necesario
# flask collectstatic --noinput

# Reiniciar aplicación
echo "🔄 Reiniciando aplicación..."
sudo supervisorctl restart gmao

echo "✅ Actualización completada!"
echo "🔍 Verificando estado..."
sudo supervisorctl status gmao
```

Dar permisos:

```bash
chmod +x /home/gmao/update_app.sh
```

---

## 🛡️ Paso 11: Backups Automáticos

### 11.1. Script de Backup

```bash
nano /home/gmao/backup_gmao.sh
```

Contenido:

```bash
#!/bin/bash

BACKUP_DIR="/home/gmao/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio de backups
mkdir -p $BACKUP_DIR

# Backup de la base de datos
pg_dump -U gmao_user gmao_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup de archivos subidos
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" /home/gmao/gmao-python/gmao-sistema/uploads/

# Eliminar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "✅ Backup completado: $DATE"
```

### 11.2. Programar con Cron

```bash
crontab -e
```

Agregar:

```cron
# Backup diario a las 2 AM
0 2 * * * /home/gmao/backup_gmao.sh >> /home/gmao/logs/backup.log 2>&1
```

---

## ✅ Verificación Final

### Checklist de Despliegue

- [ ] PostgreSQL instalado y configurado
- [ ] Base de datos creada y migraciones aplicadas
- [ ] Usuario administrador creado
- [ ] Variables de entorno configuradas
- [ ] Gunicorn iniciado correctamente
- [ ] Supervisor configurado y aplicación corriendo
- [ ] Nginx configurado como proxy inverso
- [ ] SSL/HTTPS configurado (Let's Encrypt)
- [ ] Firewall configurado
- [ ] Logs rotando correctamente
- [ ] Backups programados
- [ ] Script de actualización probado

### Comandos de Verificación

```bash
# Verificar que la aplicación está corriendo
sudo supervisorctl status gmao

# Verificar que Nginx está activo
sudo systemctl status nginx

# Verificar que PostgreSQL está activo
sudo systemctl status postgresql

# Probar la aplicación
curl https://tu-dominio.empresa.com

# Ver logs en tiempo real
tail -f /home/gmao/gmao-python/gmao-sistema/logs/gunicorn-error.log
```

---

## 🆘 Solución de Problemas

### La aplicación no inicia

```bash
# Ver logs de supervisor
sudo tail -f /home/gmao/gmao-python/gmao-sistema/logs/supervisor-error.log

# Ver logs de Gunicorn
tail -f /home/gmao/gmao-python/gmao-sistema/logs/gunicorn-error.log

# Reiniciar aplicación
sudo supervisorctl restart gmao
```

### Error de base de datos

```bash
# Verificar conexión a PostgreSQL
psql -U gmao_user -d gmao_db -h localhost

# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

### Error 502 Bad Gateway

```bash
# Verificar que Gunicorn está corriendo
ps aux | grep gunicorn

# Ver logs de Nginx
sudo tail -f /var/log/nginx/gmao-error.log

# Reiniciar servicios
sudo supervisorctl restart gmao
sudo systemctl restart nginx
```

---

## 📞 Contacto y Soporte

Para soporte o preguntas sobre el despliegue:

- **Email**: soporte@empresa.com
- **Repositorio**: https://github.com/canaleta14-ai/gmao-python

---

## 📝 Notas Finales

1. **Seguridad**: Cambiar TODAS las contraseñas por defecto
2. **Backups**: Verificar regularmente que los backups se están creando
3. **Monitoreo**: Configurar alertas para errores críticos
4. **Actualizaciones**: Mantener el sistema y dependencias actualizadas
5. **Documentación**: Mantener esta guía actualizada con cambios específicos

**¡Buena suerte con el despliegue! 🚀**
