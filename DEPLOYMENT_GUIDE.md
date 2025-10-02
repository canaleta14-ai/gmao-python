# 🚀 Guía de Deployment - GMAO Sistema

**Fecha:** 2 de octubre de 2025  
**Destino:** Google Cloud Platform (App Engine + Cloud SQL)

---

## 📋 Prerequisitos

### 1. Instalar Google Cloud SDK

**Windows:**
```powershell
# Descargar instalador desde:
# https://cloud.google.com/sdk/docs/install

# O usando chocolatey:
choco install gcloudsdk

# Verificar instalación
gcloud --version
```

**Mac:**
```bash
# Usando Homebrew
brew install --cask google-cloud-sdk

# Verificar instalación
gcloud --version
```

**Linux:**
```bash
# Usando snap
sudo snap install google-cloud-sdk --classic

# O descarga directa
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### 2. Autenticación

```bash
# Login con tu cuenta Google
gcloud auth login

# Configurar proyecto por defecto
gcloud config set project gmao-sistema

# Configurar región
gcloud config set compute/region us-central1
```

---

## 🔧 Configuración Inicial

### Paso 1: Crear Proyecto GCP (5 min)

```bash
# Crear proyecto
gcloud projects create gmao-sistema \
    --name="GMAO Sistema" \
    --set-as-default

# Habilitar facturación (requiere cuenta de facturación)
# Se hace desde la consola web: https://console.cloud.google.com/billing

# Habilitar APIs necesarias
gcloud services enable \
    sqladmin.googleapis.com \
    storage-api.googleapis.com \
    secretmanager.googleapis.com \
    appengine.googleapis.com \
    cloudscheduler.googleapis.com \
    compute.googleapis.com
```

### Paso 2: Crear Cloud SQL Instance (15 min)

```bash
# Crear instancia PostgreSQL
gcloud sql instances create gmao-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=SECURE_PASSWORD_HERE \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00

# Esperar a que se cree (puede tomar 5-10 minutos)
gcloud sql instances list

# Crear base de datos
gcloud sql databases create gmao \
    --instance=gmao-postgres

# Crear usuario de aplicación
gcloud sql users create gmao-user \
    --instance=gmao-postgres \
    --password=APP_USER_PASSWORD_HERE
```

### Paso 3: Configurar Secret Manager (10 min)

```bash
# Crear secretos para credenciales
echo -n "YOUR_SECRET_KEY_HERE" | \
    gcloud secrets create secret-key --data-file=-

echo -n "APP_USER_PASSWORD_HERE" | \
    gcloud secrets create db-password --data-file=-

echo -n "YOUR_OPENAI_API_KEY" | \
    gcloud secrets create openai-api-key --data-file=-

# Dar permisos a App Engine para acceder a secretos
PROJECT_NUMBER=$(gcloud projects describe gmao-sistema --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding secret-key \
    --member="serviceAccount:gmao-sistema@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:gmao-sistema@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:gmao-sistema@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Paso 4: Configurar Cloud Storage (5 min)

```bash
# Crear bucket para uploads
gsutil mb -p gmao-sistema -c STANDARD -l us-central1 gs://gmao-uploads

# Configurar permisos
gsutil iam ch serviceAccount:gmao-sistema@appspot.gserviceaccount.com:objectAdmin \
    gs://gmao-uploads

# Configurar CORS (para uploads directos)
echo '[
  {
    "origin": ["https://gmao-sistema.uc.r.appspot.com"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]' > cors-config.json

gsutil cors set cors-config.json gs://gmao-uploads
rm cors-config.json
```

---

## 🗄️ Migración de Base de Datos

### Paso 5: Conectar a Cloud SQL desde Local (10 min)

```bash
# Instalar Cloud SQL Proxy
# Windows: Descargar desde https://cloud.google.com/sql/docs/postgres/sql-proxy
# Mac/Linux:
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# En otra terminal, ejecutar proxy
./cloud_sql_proxy -instances=gmao-sistema:us-central1:gmao-postgres=tcp:5432

# En la terminal principal, configurar variables de entorno
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=gmao
export DB_USER=gmao-user
export DB_PASSWORD=APP_USER_PASSWORD_HERE
export DATABASE_URL="postgresql://gmao-user:APP_USER_PASSWORD_HERE@localhost:5432/gmao"
```

### Paso 6: Ejecutar Migraciones (5 min)

```bash
# Verificar que estás en el directorio del proyecto
cd c:\gmao - copia

# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar migraciones
flask db upgrade

# Verificar que las tablas se crearon
# Conectar a la BD:
psql "host=localhost port=5432 dbname=gmao user=gmao-user password=APP_USER_PASSWORD_HERE"

# Dentro de psql:
\dt  # Listar tablas
\q   # Salir
```

### Paso 7: Seed de Datos Iniciales (5 min)

```bash
# Ejecutar script de inicialización
python init_db.py

# O crear usuario admin manualmente:
flask shell
>>> from app.models.usuario import Usuario
>>> from app.extensions import db
>>> admin = Usuario(
...     username='admin',
...     email='admin@gmao.com',
...     nombre='Administrador',
...     rol='Administrador'
... )
>>> admin.set_password('admin123')  # Cambiar en producción
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()
```

---

## 🚀 Deployment a App Engine

### Paso 8: Actualizar app.yaml (5 min)

Editar `app.yaml` y actualizar:

```yaml
env_variables:
  DB_HOST: "/cloudsql/gmao-sistema:us-central1:gmao-postgres"
  DB_NAME: "gmao"
  DB_USER: "gmao-user"
  # Las contraseñas se obtienen de Secret Manager
  
beta_settings:
  cloud_sql_instances: "gmao-sistema:us-central1:gmao-postgres"
```

### Paso 9: Actualizar factory.py para Secret Manager

Verificar que `app/utils/secrets.py` está correctamente configurado para leer de Secret Manager en producción.

### Paso 10: Deploy Inicial (10 min)

```bash
# Asegurarse de estar en el directorio del proyecto
cd c:\gmao - copia

# Deploy a App Engine
gcloud app deploy app.yaml --project=gmao-sistema

# Responder 'Y' cuando pregunte si deseas continuar

# Esperar a que termine (puede tomar 5-10 minutos)

# Ver logs durante el deploy
gcloud app logs tail -s default
```

### Paso 11: Verificar Deployment (5 min)

```bash
# Abrir aplicación en navegador
gcloud app browse

# Verificar health check
curl https://gmao-sistema.uc.r.appspot.com/health

# Ver logs
gcloud app logs tail -s default

# Ver versiones deployed
gcloud app versions list

# Ver servicios
gcloud app services list
```

---

## 📊 Configurar Cron Jobs

### Paso 12: Deploy cron.yaml (5 min)

```bash
# Deploy configuración de cron
gcloud app deploy cron.yaml --project=gmao-sistema

# Verificar cron jobs
gcloud app logs tail -s default

# Ver cron jobs configurados
gcloud scheduler jobs list
```

---

## 🔍 Monitoreo y Debugging

### Ver Logs en Tiempo Real

```bash
# Ver todos los logs
gcloud app logs tail -s default

# Filtrar por severidad
gcloud app logs tail -s default --level=error

# Ver logs de hace 1 hora
gcloud app logs read --limit 50 --filter="timestamp>=\"$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S')\"" 
```

### Acceder a Cloud SQL

```bash
# Conectar vía proxy local
gcloud sql connect gmao-postgres --user=gmao-user --database=gmao

# O conectar directamente
psql "host=/cloudsql/gmao-sistema:us-central1:gmao-postgres dbname=gmao user=gmao-user"
```

### Ver Métricas

```bash
# Abrir Cloud Console
echo "https://console.cloud.google.com/appengine?project=gmao-sistema"

# Ver métricas en dashboard
gcloud app open-console --service=default
```

---

## 🔄 Actualizaciones y Rollback

### Deploy Nueva Versión

```bash
# Deploy con promoción de tráfico
gcloud app deploy --promote

# Deploy sin promoción (staging)
gcloud app deploy --no-promote --version=v2

# Migrar tráfico gradualmente
gcloud app services set-traffic default --splits=v1=0.9,v2=0.1

# Migrar todo el tráfico
gcloud app services set-traffic default --splits=v2=1.0
```

### Rollback

```bash
# Ver versiones
gcloud app versions list

# Migrar a versión anterior
gcloud app services set-traffic default --splits=v1=1.0

# Eliminar versión problemática
gcloud app versions delete v2
```

---

## 💰 Optimización de Costos

### Reducir Instancias

```yaml
# En app.yaml
automatic_scaling:
  min_instances: 0  # Permite escalar a 0 (ahorra costos)
  max_instances: 5
```

### Downsizing Cloud SQL

```bash
# Cambiar a tier más pequeño
gcloud sql instances patch gmao-postgres \
    --tier=db-f1-micro \
    --activation-policy=ALWAYS
```

### Configurar Budget Alerts

```bash
# Desde Cloud Console:
# Navigation menu > Billing > Budgets & alerts
# Crear alerta a $50/mes
```

---

## 🔒 Seguridad

### Configurar HTTPS

```bash
# App Engine tiene HTTPS por defecto
# Verificar en app.yaml:
handlers:
  - url: /.*
    secure: always  # Fuerza HTTPS
```

### Configurar Dominio Personalizado

```bash
# Verificar dominio
gcloud app domain-mappings create www.midominio.com

# Configurar DNS (ejemplo CloudFlare)
# Tipo: CNAME
# Nombre: www
# Valor: ghs.googlehosted.com
```

### Firewall Rules

```bash
# Permitir solo IPs específicas (opcional)
gcloud app firewall-rules create 1000 \
    --action=ALLOW \
    --source-range=1.2.3.4/32 \
    --description="Oficina"
```

---

## 📈 Checklist Final

- [ ] Google Cloud SDK instalado y configurado
- [ ] Proyecto GCP creado con facturación habilitada
- [ ] Cloud SQL instance creada y configurada
- [ ] Base de datos migrada y con datos seed
- [ ] Secret Manager configurado con credenciales
- [ ] Cloud Storage bucket creado
- [ ] app.yaml actualizado correctamente
- [ ] Primera versión deployed exitosamente
- [ ] Health check respondiendo OK
- [ ] Login funcionando
- [ ] CRUD básico funcionando
- [ ] Cron jobs configurados
- [ ] Logs monitoreables
- [ ]Budget alerts configurados

---

## 🆘 Troubleshooting

### Error: "database connection failed"
```bash
# Verificar que Cloud SQL instance está running
gcloud sql instances list

# Verificar conexión desde App Engine
gcloud app logs tail -s default | grep -i "database"
```

### Error: "secret not found"
```bash
# Verificar que secretos existen
gcloud secrets list

# Verificar permisos
gcloud secrets get-iam-policy secret-key
```

### Error: "502 Bad Gateway"
```bash
# Verificar logs
gcloud app logs tail -s default --level=error

# Verificar que gunicorn está configurado
# Ver entrypoint en app.yaml
```

---

## 📚 Recursos

- [App Engine Python Docs](https://cloud.google.com/appengine/docs/standard/python3)
- [Cloud SQL Docs](https://cloud.google.com/sql/docs)
- [Secret Manager Docs](https://cloud.google.com/secret-manager/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

---

**Estimado de costos mensual:**
- App Engine F2: ~$50-100/mes (depende de tráfico)
- Cloud SQL db-f1-micro: ~$15-25/mes
- Cloud Storage: ~$1-5/mes
- **Total estimado: $66-130/mes**

**Tiempo total de deployment: ~2-3 horas primera vez**
