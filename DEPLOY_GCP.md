# 🚀 Despliegue en Google Cloud Platform

Esta guía te ayudará a desplegar la aplicación GMAO en Google Cloud Platform usando App Engine, Cloud SQL y Cloud Storage.

## 📋 Prerrequisitos

1. **Cuenta de Google Cloud Platform** con facturación habilitada
2. **Google Cloud SDK** instalado: https://cloud.google.com/sdk/docs/install
3. **Proyecto de GCP** creado
4. **API de OpenAI** (opcional, para funcionalidad de IA)

## ⚙️ Configuración Inicial

### 1. Configurar Google Cloud SDK

```bash
# Autenticarse
gcloud auth login

# Configurar proyecto
gcloud config set project TU_PROJECT_ID

# Habilitar APIs necesarias
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage-api.googleapis.com
```

### 2. Crear recursos en GCP

Ejecuta el script de despliegue automático:

```bash
chmod +x deploy_gcp.sh
./deploy_gcp.sh
```

O crea los recursos manualmente:

```bash
# Crear bucket de Cloud Storage
gsutil mb -p TU_PROJECT_ID -c STANDARD -l us-central1 gs://TU_PROJECT_ID-uploads

# Crear instancia de Cloud SQL
gcloud sql instances create gmao-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-size=10GB

# Crear base de datos
gcloud sql databases create postgres --instance=gmao-postgres

# Crear usuario
gcloud sql users create gmao_user --instance=gmao-postgres --password=TU_PASSWORD_SEGURO
```

### 3. Configurar Secret Manager

Ejecuta el script de configuración de secrets:

```bash
chmod +x setup_secrets.sh
./setup_secrets.sh
```

O configura manualmente:

```bash
# Crear secrets
echo "tu_clave_secreta_muy_segura" | gcloud secrets create gmao-secret-key --data-file=-
echo "tu_password_db_seguro" | gcloud secrets create gmao-db-password --data-file=-
echo "tu_openai_api_key" | gcloud secrets create gmao-openai-key --data-file=-

# Otorgar permisos a App Engine
SERVICE_ACCOUNT="TU_PROJECT_ID@appspot.gserviceaccount.com"
gcloud secrets add-iam-policy-binding gmao-secret-key \
    --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding gmao-db-password \
    --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding gmao-openai-key \
    --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/secretmanager.secretAccessor"
```

## 🚀 Despliegue

### Opción 1: Despliegue automático

```bash
# Desplegar aplicación
gcloud app deploy --version=prod --quiet

# Inicializar base de datos
chmod +x init_db_gcp.sh
./init_db_gcp.sh
```

### Opción 2: Despliegue con Cloud Build

```bash
# Crear trigger de build
gcloud builds triggers create github \
    --repo-name=TU_REPO \
    --repo-owner=TU_USUARIO \
    --branch-pattern="main" \
    --build-config=cloudbuild.yaml

# O ejecutar build manualmente
gcloud builds submit --config=cloudbuild.yaml
```

## 🔧 Configuración Post-Despliegue

### 1. Verificar el despliegue

```bash
# Ver logs de la aplicación
gcloud app logs tail -s default

# Ver estado de los servicios
gcloud app services list
gcloud app versions list
```

### 2. Configurar dominio personalizado (opcional)

```bash
# Verificar dominio
gcloud domains verify TU_DOMINIO.com

# Configurar dominio
gcloud app domain-mappings create TU_DOMINIO.com
```

### 3. Configurar backups de base de datos

```bash
# Crear backup automático
gcloud sql instances patch gmao-postgres \
    --backup-start-time=02:00 \
    --enable-bin-log \
    --backup
```

## 📊 Monitoreo y Mantenimiento

### Ver métricas de App Engine

```bash
# Ver instancias activas
gcloud app instances list

# Ver logs de errores
gcloud logging read "resource.type=gae_app AND severity>=ERROR" --limit=10
```

### Backup de base de datos

```bash
# Crear backup manual
gcloud sql backups create gmao-postgres-backup --instance=gmao-postgres

# Listar backups
gcloud sql backups list --instance=gmao-postgres
```

### Actualizar aplicación

```bash
# Desplegar nueva versión
gcloud app deploy --version=v2 --quiet

# Migrar tráfico gradualmente
gcloud app services set-traffic default --splits=v2=100
```

## 🔒 Seguridad

### Configuraciones de seguridad recomendadas:

1. **Firewall**: Configura reglas de firewall restrictivas
2. **IAM**: Usa el principio de menor privilegio
3. **Secret Manager**: Nunca almacenes secrets en código
4. **HTTPS**: Siempre usa HTTPS (App Engine lo hace automáticamente)
5. **Actualizaciones**: Mantén las dependencias actualizadas

### Monitoreo de seguridad:

```bash
# Ver logs de acceso
gcloud logging read "resource.type=gae_app" --filter="httpRequest.status>=400"

# Configurar alertas de seguridad
gcloud alpha monitoring policies create \
    --policy-from-file=security-policy.json
```

## 🐛 Solución de Problemas

### Problemas comunes:

1. **Error de conexión a Cloud SQL**:

   - Verifica que la instancia esté corriendo
   - Confirma las credenciales en Secret Manager
   - Revisa la configuración de red

2. **Error de memoria**:

   - Aumenta el tamaño de instancia en app.yaml
   - Optimiza el uso de memoria en la aplicación

3. **Timeouts**:
   - Aumenta los timeouts en app.yaml
   - Optimiza las consultas a la base de datos

### Logs útiles:

```bash
# Logs de App Engine
gcloud app logs read --limit=50

# Logs de Cloud SQL
gcloud sql instances list-logs gmao-postgres --limit=10

# Logs de Cloud Build
gcloud builds log --stream
```

## 📞 Soporte

Para soporte técnico:

- Documentación oficial de GCP: https://cloud.google.com/docs
- Stack Overflow: Etiqueta `google-cloud-platform`
- GitHub Issues: Reporta bugs en el repositorio

## 🎯 Checklist de Despliegue

- [ ] Proyecto de GCP creado
- [ ] APIs habilitadas
- [ ] Cloud SQL configurado
- [ ] Secret Manager configurado
- [ ] Cloud Storage configurado
- [ ] App Engine desplegado
- [ ] Base de datos inicializada
- [ ] Usuario administrador creado
- [ ] Dominio configurado (opcional)
- [ ] Backups configurados
- [ ] Monitoreo activado
- [ ] Pruebas funcionales completadas

¡Tu aplicación GMAO está lista para producción en Google Cloud Platform! 🎉
