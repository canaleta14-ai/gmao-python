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

## � IMPORTANTE: Migración de Datos de Producción

**Si tienes datos existentes en tu entorno de desarrollo que necesitas migrar a producción**, sigue esta sección ANTES de continuar con el despliegue.

### Escenario de Migración

Este sistema incluye scripts especializados para migrar datos cuando:

- Tus datos de desarrollo son en realidad datos de producción
- Necesitas transferir una base de datos PostgreSQL completa
- Quieres garantizar integridad de datos con verificación de checksums
- Requieres un proceso seguro con backups automáticos

**Scripts disponibles:**

- `export_production_data.py` / `export_production_data.sh` - Exportación de BD
- `import_production_data.py` / `import_production_data.sh` - Importación en servidor

> **💡 Recomendación**: Usar los scripts Python (`.py`) ya que funcionan nativamente en Windows, Linux y Mac sin necesidad de Git Bash.

### 📤 Fase 1: Exportar Datos (Entorno de Desarrollo)

#### 1.1. Preparar el Script de Exportación

Los scripts exportarán tu base de datos con todas las medidas de seguridad:

```bash
# En tu máquina de desarrollo (Windows/Linux/Mac)
cd c:\Users\canal\gmao-python\gmao-sistema
```

> **Nota**: Los scripts Python no requieren permisos especiales ni Git Bash en Windows.

#### 1.2. Verificar Configuración de Base de Datos

Asegúrate de que tu archivo `.env` contiene las credenciales correctas:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/gmao_db
```

#### 1.3. Ejecutar la Exportación

**OPCIÓN RECOMENDADA: Script Python (multiplataforma)**

```bash
# Windows, Linux, Mac - Funciona en todos los sistemas
python export_production_data.py
```

**Opción alternativa: Script Bash (requiere Git Bash en Windows)**

```bash
# Linux/Mac
./export_production_data.sh

# Windows Git Bash
bash export_production_data.sh
```

> **💡 Nota**: El script Python es más fácil de usar en Windows ya que detecta automáticamente la instalación de PostgreSQL sin necesidad de configurar PATH ni usar Git Bash.

**Salida esperada:**

```
📦 Exportación de Base de Datos GMAO - Producción
================================================================
📅 Fecha: 2024-01-15 10:30:45
🖥️  Sistema: Windows/Linux/Mac
================================================================

✅ Directorio de exportación creado: db_export/
📊 Exportando base de datos...
✅ Base de datos exportada: db_export/gmao_data_export_20240115_103045.sql
🗜️  Comprimiendo archivo...
✅ Archivo comprimido: db_export/gmao_data_export_20240115_103045.sql.gz
🔐 Generando checksum SHA256...
✅ Checksum generado: db_export/gmao_data_export_20240115_103045.sql.gz.sha256
📝 README generado: db_export/README.txt

================================================================
✅ EXPORTACIÓN COMPLETADA
================================================================
Archivos generados en: db_export/

Archivos:
- gmao_data_export_20240115_103045.sql.gz (archivo de datos)
- gmao_data_export_20240115_103045.sql.gz.sha256 (checksum)
- README.txt (instrucciones)

Tamaño: 15.3 MB

SIGUIENTE PASO:
1. Transferir estos archivos al servidor de producción:
   scp db_export/gmao_data_export_*.sql.gz* usuario@servidor:/ruta/
2. En el servidor, ejecutar: ./import_production_data.sh
```

#### 1.4. Verificar los Archivos Generados

```bash
ls -lh db_export/

# Deberías ver:
# gmao_data_export_YYYYMMDD_HHMMSS.sql.gz         (base de datos comprimida)
# gmao_data_export_YYYYMMDD_HHMMSS.sql.gz.sha256  (checksum de verificación)
# README.txt                                       (instrucciones detalladas)
```

### 🔄 Fase 2: Transferir Archivos al Servidor

#### 2.1. Usar SCP para Transferencia Segura

```bash
# Desde tu máquina de desarrollo
scp db_export/gmao_data_export_*.sql.gz* usuario@tu-servidor.com:/home/gmao/

# Ejemplo con IP específica
scp db_export/gmao_data_export_*.sql.gz* gmao@192.168.1.100:/home/gmao/
```

#### 2.2. Alternativas de Transferencia

**Opción 2: SFTP**

```bash
sftp usuario@tu-servidor.com
put db_export/gmao_data_export_*.sql.gz*
exit
```

**Opción 3: rsync (más robusto para archivos grandes)**

```bash
rsync -avz --progress db_export/gmao_data_export_*.sql.gz* \
  usuario@tu-servidor.com:/home/gmao/
```

**Opción 4: Servicios en la nube (si el archivo es muy grande)**

- Subir a Google Drive / Dropbox / OneDrive
- Descargar desde el servidor con `wget` o `curl`

### 📥 Fase 3: Importar Datos (Servidor de Producción)

#### 3.1. Conectarse al Servidor

```bash
ssh usuario@tu-servidor.com
cd /home/gmao
```

#### 3.2. Verificar Archivos Recibidos

```bash
ls -lh gmao_data_export_*.sql.gz*

# Verificar integridad con el checksum
sha256sum -c gmao_data_export_*.sql.gz.sha256

# Salida esperada:
# gmao_data_export_20240115_103045.sql.gz: OK
```

#### 3.3. Copiar Script de Importación al Servidor

```bash
# En el servidor, navegar al directorio del proyecto
cd /home/gmao/gmao-python/gmao-sistema

# Verificar que los scripts están disponibles
ls -l import_production_data.py import_production_data.sh
```

> **Nota**: Los scripts ya están en el repositorio. Si usas el script Python (`.py`), no necesitas dar permisos de ejecución.

#### 3.4. **IMPORTANTE: Preparativos Antes de Importar**

⚠️ **ADVERTENCIAS CRÍTICAS:**

1. **La aplicación se detendrá durante la importación** (aprox. 5-15 minutos)
2. **Se creará un backup automático** de cualquier dato existente
3. **La base de datos actual será reemplazada completamente**
4. **Requiere contraseña de PostgreSQL y confirmación explícita**

**Checklist Pre-Importación:**

- [ ] Base de datos PostgreSQL ya creada (ver Paso 1.3 de esta guía)
- [ ] Usuario PostgreSQL con permisos (ver Paso 1.3)
- [ ] Archivo `.env` configurado con credenciales correctas
- [ ] Supervisor configurado (si ya está en uso)
- [ ] Backup manual adicional realizado (opcional pero recomendado)
- [ ] Ventana de mantenimiento coordinada con usuarios

#### 3.6. Ejecutar la Importación

**OPCIÓN RECOMENDADA: Script Python (multiplataforma)**

```bash
# Windows, Linux, Mac - Funciona en todos los sistemas
python import_production_data.py gmao_data_export_20240115_103045.sql.gz
```

**Opción alternativa: Script Bash (Linux/Mac o Git Bash en Windows)**

```bash
./import_production_data.sh gmao_data_export_20240115_103045.sql.gz
```

> **💡 Nota**: El script Python detecta automáticamente PostgreSQL y puede ejecutarse directamente en PowerShell sin necesidad de Git Bash.

**Proceso interactivo:**

```
================================================================
📥 IMPORTACIÓN DE BASE DE DATOS GMAO - PRODUCCIÓN
================================================================

📦 Archivo a importar: gmao_data_export_20240115_103045.sql.gz
🔐 Verificando checksum...
✅ Checksum verificado correctamente

⚠️  ADVERTENCIA IMPORTANTE ⚠️
================================================================
Este proceso:
1. Detendrá la aplicación GMAO (si está corriendo)
2. Creará un backup de la base de datos actual
3. Reemplazará TODOS los datos con el archivo importado
4. Ejecutará las migraciones de Flask
5. Reiniciará la aplicación

Tiempo estimado: 5-15 minutos
================================================================

Para confirmar, escribe: SI CONFIRMO
Confirmación: _
```

Escribe exactamente: **SI CONFIRMO**

**Salida del proceso:**

```
✅ Confirmación recibida

🛑 Paso 1/6: Deteniendo aplicación...
gmao: stopped
✅ Aplicación detenida

💾 Paso 2/6: Creando backup de seguridad...
✅ Backup creado: /home/gmao/backups/pre_import_backup_20240115_112030.sql

📦 Paso 3/6: Descomprimiendo archivo...
✅ Archivo descomprimido: gmao_data_export_20240115_103045.sql

📥 Paso 4/6: Importando datos a PostgreSQL...
[... salida de psql ...]
✅ Datos importados correctamente

🔄 Paso 5/6: Ejecutando migraciones de Flask...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
✅ Migraciones completadas

🚀 Paso 6/6: Reiniciando aplicación...
gmao: started
✅ Aplicación reiniciada

================================================================
✅ IMPORTACIÓN COMPLETADA EXITOSAMENTE
================================================================

📊 Verificación post-importación:
- Backup previo: /home/gmao/backups/pre_import_backup_20240115_112030.sql
- Base de datos actualizada: gmao_db
- Aplicación: CORRIENDO

🔍 Próximos pasos:
1. Verificar que la aplicación funciona: http://tu-servidor.com
2. Revisar logs: tail -f logs/gunicorn-access.log
3. Probar inicio de sesión y funcionalidades críticas
4. Mantener el backup por al menos 7 días

En caso de problemas, ver sección de ROLLBACK abajo.
```

#### 3.7. Verificación Post-Importación

**Verificar aplicación:**

```bash
# Estado del servicio
sudo supervisorctl status gmao

# Ver logs en tiempo real
tail -f /home/gmao/gmao-python/gmao-sistema/logs/gunicorn-access.log

# Verificar conexión a base de datos
psql -U gmao_user -d gmao_db -c "SELECT COUNT(*) FROM usuario;"
```

**Pruebas funcionales:**

```bash
# Probar endpoint de salud (si existe)
curl http://localhost:5000/health

# Verificar desde navegador
http://tu-servidor.com
```

#### 3.8. 🔙 ROLLBACK en Caso de Problemas

Si algo sale mal durante o después de la importación:

```bash
# 1. Detener la aplicación
sudo supervisorctl stop gmao

# 2. Restaurar el backup automático
psql -U gmao_user -d gmao_db < /home/gmao/backups/pre_import_backup_20240115_112030.sql

# 3. Reiniciar la aplicación
sudo supervisorctl start gmao

# 4. Verificar que todo funciona
sudo supervisorctl status gmao
```

### 📋 Resumen del Proceso Completo

| Fase              | Ubicación             | Comando                                           | Tiempo    |
| ----------------- | --------------------- | ------------------------------------------------- | --------- |
| **1. Exportar**   | Desarrollo            | `python export_production_data.py`                | 2-5 min   |
| **2. Transferir** | Desarrollo → Servidor | `scp db_export/*.gz* usuario@servidor:/path/`     | 5-30 min  |
| **3. Verificar**  | Servidor              | `sha256sum -c *.sha256`                           | 1 min     |
| **4. Importar**   | Servidor              | `python import_production_data.py archivo.sql.gz` | 5-15 min  |
| **5. Verificar**  | Servidor              | Pruebas funcionales                               | 10-20 min |

**Tiempo total estimado: 23-71 minutos**

> **💡 Scripts disponibles**: Existen versiones en Python (`.py`) y Bash (`.sh`) de ambos scripts. Se recomienda usar los scripts Python por su mejor compatibilidad multiplataforma, especialmente en Windows.

### 🔐 Consideraciones de Seguridad

1. **Credenciales**: Nunca incluir contraseñas en el control de versiones
2. **Checksums**: Siempre verificar integridad antes de importar
3. **Backups**: El script crea backup automático, pero considera hacer uno manual adicional
4. **Permisos**: Los archivos `.sql` pueden contener datos sensibles, eliminarlos después de importar
5. **Red**: Usar conexiones cifradas (SSH/SCP) para transferir archivos

### 🗑️ Limpieza Post-Migración

```bash
# En el servidor, después de verificar que todo funciona (esperar 7 días)
rm -f /home/gmao/gmao_data_export_*.sql.gz*
rm -f /home/gmao/gmao_data_export_*.sql

# En desarrollo, puedes mantener los exports como backup adicional
# o eliminarlos si ya tienes otros backups
```

---

## �🔧 Paso 1: Preparar el Servidor

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
