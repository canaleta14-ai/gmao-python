# Guía de Deployment GMAO - Google Cloud Disfood España

## 🇪🇸 Configuración para Empresa Española

### Cumplimiento normativo

- **GDPR**: Región europea (europe-west1)
- **Zona horaria**: Europe/Madrid
- **Idioma**: Español (es_ES.UTF-8)
- **Retención datos**: 7 años (normativa española)

## 🚀 Preparación para Producción

### Prerrequisitos

1. **Google Cloud SDK instalado**

   ```bash
   # Descargar desde: https://cloud.google.com/sdk
   gcloud --version
   ```

2. **Autenticación en Google Cloud**

   ```bash
   gcloud auth login
   gcloud config set project disfood-gmao
   gcloud config set compute/region europe-west1
   gcloud config set compute/zone europe-west1-b
   ```

3. **Permisos necesarios**
   - App Engine Admin
   - Cloud SQL Admin
   - Storage Admin
   - Secret Manager Admin
   - VPC Access Admin

### Configuración del Proyecto

1. **Crear proyecto en Google Cloud Console**

   - Nombre: `disfood-gmao`
   - ID: `disfood-gmao`
   - Región: `europe-west1` (GDPR compliant)

2. **Habilitar APIs**
   ```bash
   gcloud services enable appengine.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable storage.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   gcloud services enable redis.googleapis.com
   gcloud services enable vpcaccess.googleapis.com
   ```

## 🗄️ Configuración de Base de Datos (Región Europea)

### 1. Crear instancia Cloud SQL PostgreSQL

```bash
# Crear instancia en región europea
gcloud sql instances create gmao-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=europe-west1 \
    --backup-start-time=03:00 \
    --maintenance-release-channel=production \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04

# Crear base de datos
gcloud sql databases create gmao_production \
    --instance=gmao-db

# Crear usuario
gcloud sql users create gmao_user \
    --instance=gmao-db \
    --password=$(openssl rand -base64 32)
```

### 2. Configurar secretos

```bash
# Crear secretos en Secret Manager
echo "$(openssl rand -base64 64)" | gcloud secrets create flask-secret-key --data-file=-
echo "$(openssl rand -base64 32)" | gcloud secrets create db-password --data-file=-
echo "Disfood2024!" | gcloud secrets create admin-password --data-file=-
```

## 📁 Configuración de Storage

### Crear bucket para archivos

```bash
# Crear bucket
gsutil mb -p disfood-gmao -l us-central1 gs://disfood-gmao-uploads

# Configurar permisos
gsutil iam ch allUsers:objectViewer gs://disfood-gmao-uploads
```

## 🌐 Configuración de Red

### Crear VPC Connector

```bash
gcloud compute networks vpc-access connectors create gmao-connector \
    --region=us-central1 \
    --subnet-project=disfood-gmao \
    --subnet=default \
    --min-instances=2 \
    --max-instances=3
```

## 🚀 Deployment

### 1. Preparar código

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/gmao-sistema.git
cd gmao-sistema

# Instalar dependencias locales para testing
pip install -r requirements-production.txt
```

### 2. Ejecutar migraciones

```bash
# Configurar Cloud SQL Proxy (para migraciones)
gcloud sql instances describe gmao-db
./cloud_sql_proxy -instances=disfood-gmao:us-central1:gmao-db=tcp:5432 &

# Ejecutar setup de base de datos
python setup_production_db.py
```

### 3. Deployment a App Engine

```bash
# Método automático (recomendado)
chmod +x deploy.sh
./deploy.sh

# O método manual
gcloud app deploy app-production.yaml \
    --project=disfood-gmao \
    --version=v$(date +%Y%m%d-%H%M%S) \
    --promote \
    --stop-previous-version
```

## 🔧 Post-Deployment

### 1. Verificar deployment

```bash
# Obtener URL
gcloud app browse --project=disfood-gmao

# Verificar logs
gcloud app logs tail -s default
```

### 2. Configurar dominio personalizado (opcional)

```bash
# Mapear dominio
gcloud app domain-mappings create gmao.disfood.com \
    --certificate-management=AUTOMATIC
```

### 3. Configurar monitoring

```bash
# Crear alertas básicas
gcloud alpha monitoring policies create \
    --policy-from-file=monitoring-policy.yaml
```

## 🔐 Seguridad

### Configuraciones importantes

1. **Variables de entorno sensibles**

   - Solo en Secret Manager
   - No en código fuente

2. **Permisos mínimos**

   - Service accounts específicas
   - IAM roles granulares

3. **HTTPS forzado**
   - Configurado en app.yaml
   - Redirects automáticos

## 🏷️ Variables de Entorno de Producción

```yaml
# En app-production.yaml
env_variables:
  SECRETS_PROVIDER: "gcp"
  FLASK_ENV: "production"
  DB_TYPE: "postgresql"
  GOOGLE_CLOUD_PROJECT: "disfood-gmao"
  GCS_BUCKET_NAME: "disfood-gmao-uploads"
  SESSION_COOKIE_SECURE: "true"
  REMEMBER_COOKIE_SECURE: "true"
  WTF_CSRF_SSL_STRICT: "true"
```

## 📊 Monitoreo y Mantenimiento

### Logs importantes

```bash
# Ver logs de aplicación
gcloud app logs tail -s default

# Ver logs de Cloud SQL
gcloud sql operations list --instance=gmao-db

# Ver métricas
gcloud app services describe default
```

### Backups automáticos

- **Base de datos**: Backup diario automático a las 03:00
- **Storage**: Versionado automático habilitado
- **Código**: Tags en Git para cada deployment

## 🆘 Troubleshooting

### Problemas comunes

1. **Error de conexión a DB**

   ```bash
   # Verificar VPC Connector
   gcloud compute networks vpc-access connectors describe gmao-connector --region=us-central1
   ```

2. **Errores de permisos**

   ```bash
   # Verificar service account
   gcloud iam service-accounts list
   ```

3. **Problemas de storage**
   ```bash
   # Verificar bucket
   gsutil ls -b gs://disfood-gmao-uploads
   ```

## 🎯 Checklist Final

- [ ] Proyecto Google Cloud creado
- [ ] APIs habilitadas
- [ ] Cloud SQL PostgreSQL configurado
- [ ] Secretos en Secret Manager
- [ ] Storage bucket creado
- [ ] VPC Connector configurado
- [ ] App desplegada en App Engine
- [ ] Base de datos inicializada
- [ ] Usuario admin creado
- [ ] Dominio configurado (opcional)
- [ ] Monitoring configurado
- [ ] Backups verificados

## 🏢 Información de Contacto Disfood

- **Proyecto**: disfood-gmao
- **URL**: https://disfood-gmao.appspot.com
- **Región**: us-central1
- **Admin**: admin@disfood.com

---

✅ **Sistema GMAO listo para producción en Google Cloud Disfood**
