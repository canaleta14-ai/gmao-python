# 🚀 Script de Deployment Rápido - GMAO Sistema

## Instalación de Google Cloud SDK

### Windows (PowerShell como Administrador)

```powershell
# Descargar instalador
Invoke-WebRequest -Uri "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe" -OutFile "$env:TEMP\GoogleCloudSDKInstaller.exe"

# Ejecutar instalador
Start-Process -FilePath "$env:TEMP\GoogleCloudSDKInstaller.exe" -Wait

# Reiniciar PowerShell después de instalación
```

**O manualmente:**
1. Descargar desde: https://cloud.google.com/sdk/docs/install
2. Ejecutar instalador
3. Reiniciar terminal
4. Verificar: `gcloud --version`

---

## Configuración Inicial (15 min)

```bash
# 1. Login a Google Cloud
gcloud auth login

# 2. Crear proyecto (si no existe)
gcloud projects create gmao-sistema --name="GMAO Sistema"

# 3. Configurar proyecto por defecto
gcloud config set project gmao-sistema

# 4. Habilitar facturación
# Ir a: https://console.cloud.google.com/billing
# Asociar proyecto a cuenta de facturación

# 5. Habilitar APIs necesarias
gcloud services enable \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    appengine.googleapis.com \
    cloudscheduler.googleapis.com

# 6. Crear app de App Engine
gcloud app create --region=us-central
```

---

## Configuración de Cloud SQL (20 min)

```bash
# 1. Crear instancia PostgreSQL
gcloud sql instances create gmao-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password="CAMBIAR_PASSWORD_AQUI" \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup-start-time=03:00

# ESPERAR 5-10 minutos a que se cree...

# 2. Verificar que se creó
gcloud sql instances list

# 3. Crear base de datos
gcloud sql databases create gmao --instance=gmao-postgres

# 4. Crear usuario de aplicación
gcloud sql users create gmao-user \
    --instance=gmao-postgres \
    --password="CAMBIAR_PASSWORD_APP"

# 5. Anotar connection string:
# gmao-sistema:us-central1:gmao-postgres
```

---

## Configurar Secretos (10 min)

```bash
# Generar SECRET_KEY seguro
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Crear secretos
echo -n "TU_SECRET_KEY_GENERADO_ARRIBA" | gcloud secrets create secret-key --data-file=-
echo -n "CAMBIAR_PASSWORD_APP" | gcloud secrets create db-password --data-file=-
echo -n "TU_OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-

# Dar permisos a App Engine
PROJECT_ID="gmao-sistema"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="$PROJECT_ID@appspot.gserviceaccount.com"

for SECRET in secret-key db-password openai-api-key; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
done
```

---

## Migrar Base de Datos (15 min)

```bash
# 1. Descargar Cloud SQL Proxy
# Windows:
# https://dl.google.com/cloudsql/cloud_sql_proxy.exe
# Renombrar a: cloud_sql_proxy.exe

# Mac/Linux:
curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
chmod +x cloud_sql_proxy

# 2. Ejecutar proxy en otra terminal
# Windows:
.\cloud_sql_proxy.exe -instances=gmao-sistema:us-central1:gmao-postgres=tcp:5432

# Mac/Linux:
./cloud_sql_proxy -instances=gmao-sistema:us-central1:gmao-postgres=tcp:5432

# 3. En esta terminal, configurar variables
set DATABASE_URL=postgresql://gmao-user:CAMBIAR_PASSWORD_APP@localhost:5432/gmao

# 4. Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# 5. Ejecutar migraciones
flask db upgrade

# 6. Crear usuario admin
python -c "
from app.factory import create_app
from app.models.usuario import Usuario
from app.extensions import db

app = create_app()
with app.app_context():
    admin = Usuario(
        username='admin',
        email='admin@gmao.com',
        nombre='Administrador',
        rol='Administrador'
    )
    admin.set_password('admin123')  # CAMBIAR EN PRODUCCIÓN
    db.session.add(admin)
    db.session.commit()
    print('✓ Usuario admin creado')
"
```

---

## DEPLOYMENT! (10 min)

```bash
# 1. Estar en el directorio del proyecto
cd c:\gmao - copia  # Windows
cd /path/to/gmao    # Mac/Linux

# 2. Verificar que app.yaml está correcto
cat app.yaml

# 3. DEPLOY!
gcloud app deploy app.yaml --project=gmao-sistema

# Responder 'Y' cuando pregunte

# ESPERAR 5-10 minutos...

# 4. Deploy cron jobs
gcloud app deploy cron.yaml --project=gmao-sistema

# 5. Ver la aplicación
gcloud app browse
```

---

## Verificar que Funciona

```bash
# 1. Health check
curl https://gmao-sistema.uc.r.appspot.com/health

# Debería responder:
# {"status":"healthy","database":"connected"}

# 2. Ver logs
gcloud app logs tail -s default

# 3. Login a la aplicación
# Ir a: https://gmao-sistema.uc.r.appspot.com
# Usuario: admin
# Password: admin123
```

---

## Comandos Útiles Post-Deployment

```bash
# Ver logs en tiempo real
gcloud app logs tail -s default

# Ver versiones deployed
gcloud app versions list

# Escalar instancias manualmente
gcloud app versions set-traffic default --splits=v1=1.0

# Conectar a base de datos
gcloud sql connect gmao-postgres --user=gmao-user --database=gmao

# Ver cron jobs
gcloud scheduler jobs list

# Ver costos actuales
gcloud billing accounts get-iam-policy $(gcloud billing projects describe gmao-sistema --format="value(billingAccountName)")
```

---

## Rollback de Emergencia

```bash
# Ver versiones
gcloud app versions list

# Migrar tráfico a versión anterior
gcloud app versions set-traffic --splits=v1=1.0

# Eliminar versión problemática
gcloud app versions delete v2
```

---

## Costos Estimados

- **App Engine F2:** ~$50-100/mes (según tráfico)
- **Cloud SQL db-f1-micro:** ~$15-25/mes
- **Cloud Storage:** ~$1-5/mes
- **Total:** ~$66-130/mes

**Reducir costos:**
```yaml
# En app.yaml cambiar:
automatic_scaling:
  min_instances: 0  # Escala a 0 cuando no hay tráfico
  max_instances: 3  # Límite de instancias
```

---

## Troubleshooting

### Error: "gcloud: command not found"
- Reiniciar terminal después de instalar SDK
- Windows: Agregar a PATH: `C:\Users\<usuario>\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`

### Error: "database connection failed"
```bash
# Verificar instancia SQL
gcloud sql instances list

# Verificar connection string en app.yaml
# Debe ser: gmao-sistema:us-central1:gmao-postgres
```

### Error: "502 Bad Gateway"
```bash
# Ver logs de error
gcloud app logs tail -s default --level=error

# Verificar que gunicorn está en requirements.txt
grep gunicorn requirements.txt
```

### Error: "Secret not found"
```bash
# Listar secretos
gcloud secrets list

# Verificar permisos
gcloud secrets get-iam-policy secret-key
```

---

## ¿Necesitas ayuda?

- Docs: https://cloud.google.com/appengine/docs/standard/python3
- Support: https://cloud.google.com/support
- Console: https://console.cloud.google.com

---

**¡LISTO! Tu aplicación está en producción 🎉**
