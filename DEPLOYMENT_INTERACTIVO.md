# 🚀 DEPLOYMENT INTERACTIVO - Paso a Paso

**Fecha:** 2 de octubre de 2025  
**Objetivo:** Deployment a Google Cloud Platform

---

## 📋 PASO 1: Instalar Google Cloud SDK (10 minutos)

### Windows (Tu Sistema)

**Opción A: Instalador Oficial (RECOMENDADO)**

1. **Descargar el instalador:**
   - Ir a: https://cloud.google.com/sdk/docs/install
   - O directamente: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe

2. **Ejecutar el instalador:**
   - Doble clic en `GoogleCloudSDKInstaller.exe`
   - Seguir el wizard de instalación
   - **IMPORTANTE:** Marcar la opción "Run gcloud init"
   - Marcar "Add gcloud to system PATH"

3. **Verificar instalación:**
   ```powershell
   # Cerrar y reabrir PowerShell
   gcloud --version
   ```
   
   Deberías ver algo como:
   ```
   Google Cloud SDK 458.0.0
   bq 2.0.101
   core 2024.01.23
   gcloud 2024.01.23
   ```

**Opción B: Chocolatey (Si tienes Chocolatey instalado)**

```powershell
# Como administrador
choco install gcloudsdk

# Reiniciar PowerShell
gcloud --version
```

### ⏸️ PAUSA - Instala el SDK y regresa

**Cuando tengas `gcloud --version` funcionando, continúa al Paso 2.**

---

## 📋 PASO 2: Autenticación y Configuración Inicial (10 minutos)

### 2.1 Login a Google Cloud

```powershell
# Esto abrirá tu navegador
gcloud auth login
```

**En el navegador:**
- Selecciona tu cuenta de Google
- Acepta los permisos
- Espera el mensaje "You are now authenticated"

### 2.2 Configurar tu Cuenta de Facturación

**CRÍTICO:** Necesitas una cuenta de facturación activa

1. **Ir a:** https://console.cloud.google.com/billing
2. **Si no tienes cuenta:**
   - Click "Crear cuenta de facturación"
   - Ingresar datos de tarjeta de crédito
   - Google da $300 USD de crédito gratis por 90 días
3. **Si ya tienes cuenta:**
   - Asegúrate de que esté activa

### 2.3 Crear el Proyecto GCP

```powershell
# Crear proyecto
gcloud projects create gmao-sistema --name="GMAO Sistema"

# Configurar como proyecto por defecto
gcloud config set project gmao-sistema

# Verificar
gcloud config get-value project
# Debería mostrar: gmao-sistema
```

### 2.4 Vincular Facturación al Proyecto

```powershell
# Listar cuentas de facturación
gcloud billing accounts list

# Copiar el ACCOUNT_ID y vincular al proyecto
gcloud billing projects link gmao-sistema --billing-account=TU_ACCOUNT_ID_AQUI
```

### 2.5 Habilitar APIs Necesarias

```powershell
# Habilitar todas las APIs necesarias (toma ~2 minutos)
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable appengine.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable compute.googleapis.com

# Verificar que se habilitaron
gcloud services list --enabled
```

### 2.6 Crear la Aplicación de App Engine

```powershell
# Crear app en región us-central (Iowa, USA)
gcloud app create --region=us-central

# Verificar
gcloud app describe
```

**✅ Checkpoint:** Deberías tener:
- [x] gcloud autenticado
- [x] Proyecto gmao-sistema creado
- [x] Facturación vinculada
- [x] APIs habilitadas
- [x] App Engine creado

---

## 📋 PASO 3: Crear Cloud SQL (PostgreSQL) (15 minutos)

### 3.1 Crear la Instancia de PostgreSQL

```powershell
# IMPORTANTE: Cambia "TU_PASSWORD_SEGURO" por una contraseña fuerte
gcloud sql instances create gmao-postgres `
  --database-version=POSTGRES_15 `
  --tier=db-f1-micro `
  --region=us-central1 `
  --root-password=TU_PASSWORD_SEGURO_AQUI `
  --storage-type=SSD `
  --storage-size=10GB `
  --storage-auto-increase `
  --backup-start-time=03:00

# Esto tomará 5-10 minutos. Espera...
```

**Mientras esperas, genera tu SECRET_KEY:**

```powershell
# En otra ventana de PowerShell
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copia el resultado (ejemplo: xK9mP2_vQw7nR8sT5uY1zA3bC4dE6fG7hJ8kL0mN2oP4qR6)
# Lo necesitarás en el Paso 4
```

### 3.2 Verificar que la Instancia se Creó

```powershell
# Listar instancias
gcloud sql instances list

# Deberías ver:
# NAME            DATABASE_VERSION  LOCATION       TIER         STATUS
# gmao-postgres   POSTGRES_15       us-central1-a  db-f1-micro  RUNNABLE
```

### 3.3 Crear la Base de Datos

```powershell
# Crear base de datos "gmao"
gcloud sql databases create gmao --instance=gmao-postgres

# Listar bases de datos
gcloud sql databases list --instance=gmao-postgres
```

### 3.4 Crear Usuario de Aplicación

```powershell
# IMPORTANTE: Cambia "TU_PASSWORD_APP" por una contraseña fuerte
gcloud sql users create gmao-user `
  --instance=gmao-postgres `
  --password=TU_PASSWORD_APP_AQUI

# Listar usuarios
gcloud sql users list --instance=gmao-postgres
```

### 3.5 Anotar el Connection String

**IMPORTANTE:** Anota esto, lo necesitarás más adelante:

```
Connection String: gmao-sistema:us-central1:gmao-postgres
DB Name: gmao
DB User: gmao-user
DB Password: [el que pusiste en TU_PASSWORD_APP]
```

**✅ Checkpoint:** Cloud SQL listo
- [x] Instancia gmao-postgres creada
- [x] Base de datos "gmao" creada
- [x] Usuario gmao-user creado
- [x] Connection string anotado

---

## 📋 PASO 4: Configurar Secret Manager (10 minutos)

### 4.1 Crear Secretos

```powershell
# SECRET_KEY (usa el que generaste antes)
echo -n "xK9mP2_vQw7nR8sT5uY1zA3bC4dE6fG7hJ8kL0mN2oP4qR6" | gcloud secrets create secret-key --data-file=-

# DB Password (usa el que pusiste en TU_PASSWORD_APP)
echo -n "TU_PASSWORD_APP_AQUI" | gcloud secrets create db-password --data-file=-

# OpenAI API Key (si tienes, si no, omite este paso)
echo -n "sk-..." | gcloud secrets create openai-api-key --data-file=-
```

### 4.2 Dar Permisos a App Engine

```powershell
# Obtener número de proyecto
$PROJECT_NUMBER = gcloud projects describe gmao-sistema --format="value(projectNumber)"
$SERVICE_ACCOUNT = "gmao-sistema@appspot.gserviceaccount.com"

# Dar permisos para secret-key
gcloud secrets add-iam-policy-binding secret-key `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/secretmanager.secretAccessor"

# Dar permisos para db-password
gcloud secrets add-iam-policy-binding db-password `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/secretmanager.secretAccessor"

# Si creaste openai-api-key:
gcloud secrets add-iam-policy-binding openai-api-key `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/secretmanager.secretAccessor"
```

### 4.3 Verificar Secretos

```powershell
# Listar secretos
gcloud secrets list

# Deberías ver:
# NAME             CREATED              REPLICATION_POLICY  LOCATIONS
# db-password      [fecha]              automatic           -
# openai-api-key   [fecha]              automatic           -
# secret-key       [fecha]              automatic           -
```

**✅ Checkpoint:** Secret Manager configurado
- [x] SECRET_KEY creado
- [x] db-password creado
- [x] Permisos IAM configurados

---

## 📋 PASO 5: Migrar Base de Datos (15 minutos)

### 5.1 Descargar Cloud SQL Proxy

**Windows:**

```powershell
# Descargar Cloud SQL Proxy
Invoke-WebRequest -Uri "https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe" -OutFile "cloud_sql_proxy.exe"

# Mover a una ubicación conveniente (opcional)
# O dejarlo en el directorio actual
```

### 5.2 Ejecutar Cloud SQL Proxy

**En una NUEVA ventana de PowerShell:**

```powershell
# Ir al directorio del proyecto
cd "C:\gmao - copia"

# Ejecutar proxy
.\cloud_sql_proxy.exe -instances=gmao-sistema:us-central1:gmao-postgres=tcp:5432
```

**Deja esta ventana abierta.** Deberías ver:
```
Listening on 127.0.0.1:5432 for gmao-sistema:us-central1:gmao-postgres
Ready for new connections
```

### 5.3 Configurar Variables de Entorno

**En tu ventana PRINCIPAL de PowerShell:**

```powershell
# Ir al directorio del proyecto
cd "C:\gmao - copia"

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Configurar DATABASE_URL (CAMBIA TU_PASSWORD_APP)
$env:DATABASE_URL="postgresql://gmao-user:TU_PASSWORD_APP_AQUI@localhost:5432/gmao"

# Verificar
echo $env:DATABASE_URL
```

### 5.4 Ejecutar Migraciones

```powershell
# Ejecutar migraciones
flask db upgrade

# Deberías ver:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> 499968d1e362, agregar relación orden plan de...
```

### 5.5 Crear Usuario Administrador

```powershell
# Ejecutar script para crear admin
python -c "
from app.factory import create_app
from app.models.usuario import Usuario
from app.extensions import db

app = create_app()
with app.app_context():
    # Verificar si ya existe
    admin_existe = Usuario.query.filter_by(username='admin').first()
    if admin_existe:
        print('✓ Usuario admin ya existe')
    else:
        admin = Usuario(
            username='admin',
            email='admin@gmao.com',
            nombre='Administrador del Sistema',
            rol='Administrador'
        )
        admin.set_password('admin123')  # CAMBIAR EN PRODUCCIÓN
        db.session.add(admin)
        db.session.commit()
        print('✓ Usuario admin creado exitosamente')
        print('  Username: admin')
        print('  Password: admin123')
"
```

### 5.6 Verificar la Migración

```powershell
# Conectar a la base de datos con psql (si lo tienes instalado)
# Si no, puedes omitir este paso

# Listar tablas
gcloud sql connect gmao-postgres --user=gmao-user --database=gmao

# En el prompt de psql:
\dt
# Deberías ver todas las tablas: activo, orden_trabajo, plan_mantenimiento, etc.

\q  # Para salir
```

**✅ Checkpoint:** Base de datos lista
- [x] Migraciones ejecutadas
- [x] Usuario admin creado
- [x] Tablas verificadas

**IMPORTANTE:** Mantén el Cloud SQL Proxy corriendo en la otra ventana.

---

## 📋 PASO 6: DEPLOYMENT! (10 minutos)

### 6.1 Verificar app.yaml

Tu `app.yaml` ya está configurado, pero verifica que tenga:

```yaml
beta_settings:
  cloud_sql_instances: gmao-sistema:us-central1:gmao-postgres
```

### 6.2 Deploy a App Engine

```powershell
# Asegúrate de estar en el directorio del proyecto
cd "C:\gmao - copia"

# DEPLOY!
gcloud app deploy app.yaml --project=gmao-sistema

# Responde 'Y' cuando pregunte:
# Do you want to continue (Y/n)?  Y
```

**Esto tomará 5-10 minutos.** Verás:

```
Beginning deployment of service [default]...
Building and pushing image for service [default]
Started cloud build...
...
Updating service [default]...done.
Setting traffic split for service [default]...done.
Deployed service [default] to [https://gmao-sistema.uc.r.appspot.com]
```

### 6.3 Deploy Cron Jobs

```powershell
# Deploy configuración de cron
gcloud app deploy cron.yaml --project=gmao-sistema

# Responde 'Y'
```

### 6.4 Abrir la Aplicación

```powershell
# Esto abrirá tu navegador con la app
gcloud app browse
```

**¡Tu app debería estar funcionando!**

---

## 📋 PASO 7: Verificación (5 minutos)

### 7.1 Health Check

```powershell
# Verificar health check
curl https://gmao-sistema.uc.r.appspot.com/health

# Deberías ver:
# {"status":"healthy","database":"connected"}
```

### 7.2 Login a la Aplicación

1. Ir a: https://gmao-sistema.uc.r.appspot.com
2. Login con:
   - **Username:** admin
   - **Password:** admin123

### 7.3 Ver Logs

```powershell
# Ver logs en tiempo real
gcloud app logs tail -s default

# Presiona Ctrl+C para detener
```

### 7.4 Verificar Dashboard

- Navega por la aplicación
- Crea un activo de prueba
- Crea una orden de trabajo
- Verifica que todo funciona

---

## 🎉 ¡DEPLOYMENT COMPLETADO!

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         ✅ APLICACIÓN DEPLOYADA EXITOSAMENTE ✅              ║
║                                                              ║
║  URL: https://gmao-sistema.uc.r.appspot.com                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 📊 Información Importante

### URLs
- **Aplicación:** https://gmao-sistema.uc.r.appspot.com
- **Console GCP:** https://console.cloud.google.com/appengine?project=gmao-sistema
- **Logs:** https://console.cloud.google.com/logs?project=gmao-sistema

### Credenciales Iniciales
- **Usuario:** admin
- **Password:** admin123
- **⚠️ CAMBIAR INMEDIATAMENTE EN PRODUCCIÓN**

### Costos Estimados
- App Engine F2: ~$50-100/mes
- Cloud SQL db-f1-micro: ~$15-25/mes
- Total: ~$65-125/mes

### Comandos Útiles

```powershell
# Ver logs
gcloud app logs tail -s default

# Ver versiones
gcloud app versions list

# Conectar a Cloud SQL
gcloud sql connect gmao-postgres --user=gmao-user --database=gmao

# Ver cron jobs
gcloud scheduler jobs list

# Detener app (para ahorrar costos)
gcloud app services set-traffic default --splits=STOP

# Reactivar app
gcloud app deploy
```

---

## 🆘 Troubleshooting

### Error: "502 Bad Gateway"
```powershell
# Ver logs de error
gcloud app logs tail -s default --level=error

# Verificar que Cloud SQL está conectado
gcloud sql instances list
```

### Error: "Database connection failed"
```powershell
# Verificar connection string en app.yaml
# Debe ser: gmao-sistema:us-central1:gmao-postgres
```

### Error: "Secret not found"
```powershell
# Listar secretos
gcloud secrets list

# Verificar permisos
gcloud secrets get-iam-policy secret-key
```

---

## ✅ Checklist Final

- [ ] Google Cloud SDK instalado
- [ ] Proyecto GCP creado con facturación
- [ ] Cloud SQL instance creada
- [ ] Base de datos migrada
- [ ] Secretos configurados
- [ ] App deployada exitosamente
- [ ] Health check respondiendo
- [ ] Login funcionando
- [ ] CRUD básico funcionando
- [ ] Cron jobs configurados

---

**¿Necesitas ayuda en algún paso?** Avísame y te guío.

**¡Vamos a deployar tu aplicación!** 🚀
