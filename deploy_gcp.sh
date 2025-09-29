#!/bin/bash
# Script de despliegue para Google Cloud Platform

set -e

echo "🚀 Iniciando despliegue a Google Cloud Platform..."

# Verificar que gcloud esté instalado y configurado
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI no está instalado. Instálalo desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null; then
    echo "❌ No estás autenticado en gcloud. Ejecuta: gcloud auth login"
    exit 1
fi

# Verificar proyecto configurado
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No hay proyecto configurado. Ejecuta: gcloud config set project [PROJECT_ID]"
    exit 1
fi

echo "✅ Proyecto configurado: $PROJECT_ID"

# Crear bucket de Cloud Storage para uploads (si no existe)
BUCKET_NAME="${PROJECT_ID}-uploads"
if ! gsutil ls -b gs://$BUCKET_NAME > /dev/null 2>&1; then
    echo "📦 Creando bucket de Cloud Storage: $BUCKET_NAME"
    gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$BUCKET_NAME
    gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
else
    echo "✅ Bucket ya existe: $BUCKET_NAME"
fi

# Crear instancia de Cloud SQL (si no existe)
DB_INSTANCE="gmao-postgres"
if ! gcloud sql instances describe $DB_INSTANCE > /dev/null 2>&1; then
    echo "🗄️ Creando instancia de Cloud SQL: $DB_INSTANCE"
    gcloud sql instances create $DB_INSTANCE \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=us-central1 \
        --storage-size=10GB \
        --storage-type=HDD
else
    echo "✅ Instancia de Cloud SQL ya existe: $DB_INSTANCE"
fi

# Crear base de datos
echo "📊 Creando base de datos..."
gcloud sql databases create gmao_db --instance=$DB_INSTANCE || echo "Base de datos ya existe"

# Crear usuario de base de datos
echo "👤 Creando usuario de base de datos..."
gcloud sql users create gmao_user \
    --instance=$DB_INSTANCE \
    --password=gmao_password_2025 || echo "Usuario ya existe"

# Desplegar aplicación
echo "🚀 Desplegando aplicación a App Engine..."
gcloud app deploy --version=prod --quiet

# Obtener URL de la aplicación
APP_URL=$(gcloud app describe --format="value(defaultHostname)")
echo "✅ Despliegue completado!"
echo "🌐 URL de la aplicación: https://$APP_URL"
echo ""
echo "📝 Próximos pasos:"
echo "1. Configura las variables de entorno sensibles en Secret Manager"
echo "2. Actualiza la configuración de la base de datos en app.yaml"
echo "3. Configura Cloud Storage para uploads"
echo "4. Configura el dominio personalizado si es necesario"