# 🏢 Guía de Despliegue Empresarial - Sistema GMAO

**Objetivo**: Desplegar el sistema GMAO en la cuenta de Google Cloud Platform de tu empresa.

**Fecha**: 2 de octubre de 2025  
**Proyecto Actual (desarrollo)**: gmao-sistema-2025  
**Cuenta de Facturación Actual**: desarrollos_hibo (con créditos gratuitos de $300)

---

## 📋 Índice

1. [Opciones de Despliegue](#opciones-de-despliegue)
2. [Opción A: Cambiar Cuenta de Facturación (Proyecto Existente)](#opción-a-cambiar-cuenta-de-facturación)
3. [Opción B: Crear Nuevo Proyecto Empresarial](#opción-b-crear-nuevo-proyecto-empresarial)
4. [Configuración de la Organización](#configuración-de-la-organización)
5. [Costos Estimados](#costos-estimados)
6. [Checklist de Despliegue](#checklist-de-despliegue)

---

## 🔀 Opciones de Despliegue

### Opción A: Cambiar Cuenta de Facturación del Proyecto Actual
**✅ Ventajas:**
- Rápido (5-10 minutos)
- Mantiene toda la configuración actual
- Mantiene la base de datos y datos existentes
- URL no cambia

**❌ Desventajas:**
- Pierdes los créditos gratuitos de $300
- El proyecto queda en tu cuenta personal de GCP

**💰 Costo**: ~$20-50/mes (según uso)

### Opción B: Crear Nuevo Proyecto en la Organización Empresarial
**✅ Ventajas:**
- Proyecto bajo la organización de la empresa
- Mejor control de accesos (IAM)
- Políticas de seguridad centralizadas
- Separación clara entre desarrollo y producción
- Puedes mantener el proyecto actual para pruebas

**❌ Desventajas:**
- Más tiempo de configuración (30-60 minutos)
- Necesitas migrar la base de datos
- URL diferente (ej: gmao-disfood.ew.r.appspot.com)

**💰 Costo**: ~$20-50/mes (según uso)

---

## 🔧 Opción A: Cambiar Cuenta de Facturación

### Paso 1: Obtener Acceso a la Cuenta Empresarial

**Necesitas:**
- Acceso a la consola de Google Cloud de tu empresa
- Permisos de "Administrador de Facturación" o "Propietario del Proyecto"

**Si NO tienes acceso:**
1. Solicita al administrador de TI/Cloud de tu empresa
2. Pídele que te agregue como "Billing Account User" en la cuenta empresarial
3. O pídele que te haga propietario del proyecto

### Paso 2: Verificar Cuentas de Facturación Disponibles

```powershell
# Listar cuentas de facturación
gcloud billing accounts list

# Verás algo como:
# ACCOUNT_ID            NAME                    OPEN
# 0117A8-4C629F-5B1866  desarrollos_hibo        True
# XXXXXX-XXXXXX-XXXXXX  Disfood_Billing         True
```

### Paso 3: Cambiar la Cuenta de Facturación

**Desde la Consola Web (Recomendado):**

1. Ve a: https://console.cloud.google.com/
2. Selecciona el proyecto: **gmao-sistema-2025**
3. Menú (☰) > **Facturación**
4. Click en **"Cambiar cuenta de facturación"**
5. Selecciona la cuenta de tu empresa
6. Click en **"Establecer cuenta"**
7. ✅ Listo - El proyecto ahora se factura a la empresa

**Desde la línea de comandos:**

```powershell
# Reemplaza EMPRESA_BILLING_ACCOUNT_ID con el ID de la cuenta empresarial
gcloud billing projects link gmao-sistema-2025 --billing-account=EMPRESA_BILLING_ACCOUNT_ID
```

### Paso 4: Verificar el Cambio

```powershell
gcloud billing projects describe gmao-sistema-2025
```

Deberías ver:
```yaml
billingAccountName: billingAccounts/EMPRESA_BILLING_ACCOUNT_ID
billingEnabled: true
name: gmao-sistema-2025
projectId: gmao-sistema-2025
```

### ⚠️ Importante:
- Los créditos gratuitos de $300 se pierden al cambiar de cuenta
- La aplicación sigue funcionando sin interrupciones
- Los costos futuros se cobran a la empresa

---

## 🏗️ Opción B: Crear Nuevo Proyecto Empresarial

### Paso 1: Preparación

**Información necesaria:**
- Nombre del proyecto: `gmao-disfood` (o el que prefieras)
- Organización: La organización de tu empresa en GCP
- Cuenta de facturación: La cuenta empresarial
- Región: europe-west1 (Bélgica, cercano a España)

### Paso 2: Crear el Proyecto

**Desde la Consola Web:**

1. Ve a: https://console.cloud.google.com/
2. Click en el selector de proyectos (arriba)
3. Click en **"NUEVO PROYECTO"**
4. Completa:
   - **Nombre del proyecto**: GMAO - Disfood
   - **ID del proyecto**: gmao-disfood (o automático)
   - **Organización**: Selecciona tu empresa
   - **Ubicación**: Elige la carpeta/organización adecuada
5. Click en **"CREAR"**

**Desde la línea de comandos:**

```powershell
# Listar organizaciones disponibles
gcloud organizations list

# Crear proyecto en la organización
gcloud projects create gmao-disfood \
    --organization=ORGANIZATION_ID \
    --name="GMAO - Disfood"

# Vincular cuenta de facturación
gcloud billing projects link gmao-disfood \
    --billing-account=EMPRESA_BILLING_ACCOUNT_ID

# Establecer como proyecto activo
gcloud config set project gmao-disfood
```

### Paso 3: Habilitar APIs Necesarias

```powershell
# Habilitar APIs
gcloud services enable sqladmin.googleapis.com --project=gmao-disfood
gcloud services enable appengine.googleapis.com --project=gmao-disfood
gcloud services enable secretmanager.googleapis.com --project=gmao-disfood
gcloud services enable cloudscheduler.googleapis.com --project=gmao-disfood
```

### Paso 4: Crear App Engine

```powershell
# Crear aplicación en App Engine (región europa)
gcloud app create --region=europe-west1 --project=gmao-disfood
```

### Paso 5: Crear Cloud SQL (PostgreSQL)

```powershell
# Crear instancia de Cloud SQL
gcloud sql instances create gmao-postgres-prod \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=europe-west1 \
    --root-password=GENERA_PASSWORD_SEGURA_AQUI \
    --backup \
    --backup-start-time=03:00 \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --project=gmao-disfood

# Crear base de datos
gcloud sql databases create gmao \
    --instance=gmao-postgres-prod \
    --project=gmao-disfood

# Crear usuario
gcloud sql users create gmao-user \
    --instance=gmao-postgres-prod \
    --password=GENERA_PASSWORD_SEGURA_AQUI \
    --project=gmao-disfood
```

### Paso 6: Migrar/Copiar Base de Datos

**Opción A: Exportar e Importar Datos**

```powershell
# 1. Exportar desde proyecto actual
gcloud sql export sql gmao-postgres gmao-backup.sql \
    --database=gmao \
    --project=gmao-sistema-2025

# 2. Importar al nuevo proyecto
gcloud sql import sql gmao-postgres-prod gmao-backup.sql \
    --database=gmao \
    --project=gmao-disfood
```

**Opción B: Empezar Base de Datos Limpia**

```powershell
# Ejecutar migración en el nuevo proyecto
# (Modificar migrate_solicitud_archivos.py para el nuevo proyecto)
python migrate_solicitud_archivos.py
```

### Paso 7: Configurar Variables de Entorno

Edita `app.yaml` con la nueva configuración:

```yaml
runtime: python311
instance_class: F2

env_variables:
  FLASK_ENV: production
  DB_TYPE: postgresql
  DB_USER: gmao-user
  DB_PASSWORD: "TU_PASSWORD_NUEVA"
  DB_NAME: gmao
  DB_HOST: "/cloudsql/gmao-disfood:europe-west1:gmao-postgres-prod"
  SERVER_URL: https://gmao-disfood.ew.r.appspot.com
  
  # Email
  MAIL_SERVER: smtp.gmail.com
  MAIL_PORT: "587"
  MAIL_USE_TLS: "True"
  MAIL_USERNAME: j_hidalgo@disfood.com
  MAIL_PASSWORD: dvematimfpjjpxji
  ADMIN_EMAIL: j_hidalgo@disfood.com

beta_settings:
  cloud_sql_instances: gmao-disfood:europe-west1:gmao-postgres-prod
```

### Paso 8: Desplegar la Aplicación

```powershell
# Desplegar
gcloud app deploy app.yaml --project=gmao-disfood --quiet

# Verificar
gcloud app browse --project=gmao-disfood
```

### Paso 9: Ejecutar Migración de Base de Datos

```powershell
# Configurar variables para conectar a la nueva BD
$env:DB_TYPE="postgresql"
$env:DB_USER="gmao-user"
$env:DB_PASSWORD="TU_PASSWORD_NUEVA"
$env:DB_NAME="gmao"
$env:DB_HOST="IP_DE_CLOUD_SQL_NUEVO"

# Ejecutar migración
python migrate_solicitud_archivos.py
```

### Paso 10: Crear Usuario Administrador

```powershell
# Conectar a Cloud SQL
gcloud sql connect gmao-postgres-prod --user=gmao-user --database=gmao --project=gmao-disfood

# En el prompt de PostgreSQL:
INSERT INTO usuario (username, password_hash, email, nombre_completo, rol, activo, fecha_creacion)
VALUES (
    'admin',
    'scrypt:32768:8:1$PASSWORD_HASH_AQUI',
    'j_hidalgo@disfood.com',
    'Administrador',
    'Administrador',
    TRUE,
    NOW()
);
```

---

## 🏛️ Configuración de la Organización

### Estructura Recomendada en GCP

```
Organización: Disfood
├── Carpeta: Producción
│   └── Proyecto: gmao-disfood (PRODUCCIÓN)
│       ├── App Engine
│       ├── Cloud SQL
│       └── Secret Manager
│
└── Carpeta: Desarrollo
    └── Proyecto: gmao-disfood-dev (DESARROLLO)
        ├── App Engine
        └── Cloud SQL (instancia pequeña)
```

### Roles y Permisos Recomendados

| Usuario/Grupo | Rol | Acceso |
|---------------|-----|--------|
| Equipo IT | Owner | Acceso completo |
| Desarrolladores | Editor | Despliegue y edición |
| Usuarios finales | Viewer | Solo lectura logs |
| Cuenta de servicio | App Engine Admin | Solo App Engine |

### Configurar IAM

```powershell
# Agregar desarrollador
gcloud projects add-iam-policy-binding gmao-disfood \
    --member="user:desarrollador@disfood.com" \
    --role="roles/editor"

# Agregar usuario con acceso de solo lectura
gcloud projects add-iam-policy-binding gmao-disfood \
    --member="user:gerencia@disfood.com" \
    --role="roles/viewer"
```

---

## 💰 Costos Estimados

### Desglose Mensual (Uso Normal)

| Servicio | Especificación | Costo Mensual |
|----------|----------------|---------------|
| **App Engine** | F2 (2 vCPU, 2GB RAM) | $15-30 |
| **Cloud SQL** | db-f1-micro (PostgreSQL) | $7-10 |
| **Almacenamiento** | 10 GB (BD + archivos) | $2-3 |
| **Tráfico de red** | ~100 GB salida | $3-5 |
| **Logs y monitoreo** | Stackdriver Logging | $2-3 |
| **TOTAL ESTIMADO** | | **$29-51/mes** |

### Costos Reales según Uso

**Uso Bajo** (10 usuarios, 100 solicitudes/mes):
- **~$20-30/mes**

**Uso Medio** (50 usuarios, 500 solicitudes/mes):
- **~$40-60/mes**

**Uso Alto** (100+ usuarios, 1000+ solicitudes/mes):
- **~$70-100/mes**
- Considerar escalar a instancias F4 o F4_1G

### Ahorrar Costos

1. **Backups automáticos**: Solo retener 7 días (~$2/mes ahorro)
2. **Instancias bajo demanda**: Escalar a 0 en horarios no laborales
3. **Comprimir logs**: Retener solo 30 días
4. **Cloud Storage**: Usar bucket regional en lugar de multi-regional

---

## ✅ Checklist de Despliegue Empresarial

### Pre-requisitos
- [ ] Acceso a cuenta de facturación empresarial
- [ ] Permisos de Owner/Editor en GCP
- [ ] Credenciales de Gmail empresarial configuradas
- [ ] Backup de base de datos actual (si aplica)

### Configuración del Proyecto
- [ ] Proyecto creado en la organización
- [ ] Cuenta de facturación vinculada
- [ ] APIs habilitadas
- [ ] App Engine creado
- [ ] Cloud SQL creado y configurado
- [ ] Usuarios IAM configurados

### Despliegue
- [ ] Variables de entorno actualizadas en app.yaml
- [ ] Código desplegado en App Engine
- [ ] Migración de base de datos ejecutada
- [ ] Usuario administrador creado
- [ ] Emails de prueba enviados correctamente

### Seguridad
- [ ] Contraseñas seguras generadas
- [ ] Secrets almacenados en Secret Manager (opcional)
- [ ] Certificados SSL/TLS configurados (automático en App Engine)
- [ ] Políticas de backup configuradas
- [ ] Logs de auditoría habilitados

### Post-Despliegue
- [ ] Pruebas de funcionalidad completas
- [ ] Capacitación a usuarios finales
- [ ] Documentación actualizada
- [ ] Plan de respaldo y recuperación documentado
- [ ] Monitoreo de costos configurado

---

## 🔐 Seguridad y Mejores Prácticas

### 1. Usar Secret Manager

En lugar de poner contraseñas en app.yaml:

```powershell
# Crear secrets
echo -n "TU_PASSWORD_DB" | gcloud secrets create db-password --data-file=-
echo -n "TU_PASSWORD_MAIL" | gcloud secrets create mail-password --data-file=-

# Dar acceso a App Engine
gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:gmao-disfood@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

Modificar `app.yaml`:
```yaml
env_variables:
  DB_PASSWORD: ${DB_PASSWORD}  # Se obtiene de Secret Manager
  MAIL_PASSWORD: ${MAIL_PASSWORD}
```

### 2. Configurar Backups Automáticos

```powershell
# Configurar backup automático diario
gcloud sql instances patch gmao-postgres-prod \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --retained-backups-count=7 \
    --project=gmao-disfood
```

### 3. Monitoreo y Alertas

```powershell
# Crear alerta de presupuesto
gcloud billing budgets create \
    --billing-account=EMPRESA_BILLING_ACCOUNT_ID \
    --display-name="GMAO Budget Alert" \
    --budget-amount=100 \
    --threshold-rule=percent=50 \
    --threshold-rule=percent=90
```

---

## 🚀 Comandos de Despliegue Rápido

### Script Completo para Nuevo Proyecto

Guarda esto como `deploy_empresa.ps1`:

```powershell
# Configuración
$PROJECT_ID = "gmao-disfood"
$REGION = "europe-west1"
$BILLING_ACCOUNT = "EMPRESA_BILLING_ACCOUNT_ID"
$DB_PASSWORD = "GENERA_PASSWORD_SEGURA"
$MAIL_PASSWORD = "dvematimfpjjpxji"

# 1. Crear proyecto
gcloud projects create $PROJECT_ID --name="GMAO - Disfood"

# 2. Vincular facturación
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT

# 3. Establecer proyecto activo
gcloud config set project $PROJECT_ID

# 4. Habilitar APIs
gcloud services enable sqladmin.googleapis.com appengine.googleapis.com secretmanager.googleapis.com

# 5. Crear App Engine
gcloud app create --region=$REGION

# 6. Crear Cloud SQL
gcloud sql instances create gmao-postgres-prod `
    --database-version=POSTGRES_15 `
    --tier=db-f1-micro `
    --region=$REGION `
    --root-password=$DB_PASSWORD `
    --backup

# 7. Crear base de datos
gcloud sql databases create gmao --instance=gmao-postgres-prod

# 8. Crear usuario
gcloud sql users create gmao-user `
    --instance=gmao-postgres-prod `
    --password=$DB_PASSWORD

# 9. Desplegar aplicación
gcloud app deploy app.yaml --quiet

Write-Host "✅ Despliegue completado!"
Write-Host "🌐 URL: https://$PROJECT_ID.ew.r.appspot.com"
```

---

## 📞 Soporte y Contacto

### Recursos de Google Cloud

- **Documentación**: https://cloud.google.com/docs
- **Soporte**: https://cloud.google.com/support
- **Calculadora de costos**: https://cloud.google.com/products/calculator

### Próximos Pasos Después del Despliegue

1. **Configurar dominio personalizado** (opcional):
   - ej: gmao.disfood.com
   - https://cloud.google.com/appengine/docs/standard/mapping-custom-domains

2. **Configurar Cloud Storage** para archivos permanentes
3. **Implementar CI/CD** con Cloud Build
4. **Configurar monitoreo** con Cloud Monitoring
5. **Planificar estrategia de backups** y recuperación ante desastres

---

## 🎯 Recomendación Final

**Para producción empresarial, recomiendo:**

✅ **Opción B**: Crear nuevo proyecto en la organización empresarial

**Razones:**
- Mejor gobernanza y control
- Separación entre desarrollo y producción
- Políticas de seguridad centralizadas
- Mantener proyecto actual para pruebas
- Imagen profesional (URL corporativa)

**Tiempo estimado:** 1-2 horas para configuración completa

---

**¿Necesitas ayuda con algún paso específico del despliegue empresarial?**
