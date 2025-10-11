#!/bin/bash
# Script de deployment para GMAO en Google Cloud - Disfood España

set -e  # Salir si hay errores

echo "🚀 INICIANDO DEPLOYMENT GMAO - DISFOOD ESPAÑA"
echo "=============================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "app-production.yaml" ]; then
    echo "❌ Error: No se encuentra app-production.yaml"
    echo "   Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar que gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI no está instalado"
    echo "   Instala Google Cloud SDK desde: https://cloud.google.com/sdk"
    exit 1
fi

# Configurar proyecto y región europea
echo "🔧 Configurando proyecto Google Cloud para España..."
PROJECT_ID="disfood-gmao"
REGION="europe-west1"  # Región europea para cumplimiento GDPR
ZONE="europe-west1-b"

gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

echo "🇪🇸 Configuración para España:"
echo "   Proyecto: $PROJECT_ID"
echo "   Región: $REGION (Europa - GDPR compatible)"
echo "   Zona: $ZONE"

# Verificar autenticación
echo "🔑 Verificando autenticación..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "❌ No hay sesión activa de gcloud"
    echo "   Ejecuta: gcloud auth login"
    exit 1
fi

echo "✅ Autenticado como: $(gcloud auth list --filter=status:ACTIVE --format="value(account)")"

# Habilitar APIs necesarias
echo "🔌 Habilitando APIs de Google Cloud..."
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable vpcaccess.googleapis.com

# Crear instancia de Cloud SQL en región europea (si no existe)
echo "🗄️ Configurando Cloud SQL en región europea..."
if ! gcloud sql instances describe gmao-db --project=$PROJECT_ID &>/dev/null; then
    echo "📦 Creando instancia Cloud SQL en $REGION..."
    gcloud sql instances create gmao-db \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=$REGION \
        --project=$PROJECT_ID
    
    echo "👤 Creando usuario de base de datos..."
    gcloud sql users create gmao_user \
        --instance=gmao-db \
        --password=$(openssl rand -base64 32) \
        --project=$PROJECT_ID
    
    echo "🗃️ Creando base de datos..."
    gcloud sql databases create gmao_production \
        --instance=gmao-db \
        --project=$PROJECT_ID
else
    echo "✅ Instancia Cloud SQL ya existe"
fi

# Crear bucket de Storage en región europea (si no existe)
echo "📁 Configurando Cloud Storage en región europea..."
BUCKET_NAME="disfood-gmao-uploads-eu"
if ! gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
    echo "📦 Creando bucket de Storage en $REGION..."
    gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME
    
    # Configurar permisos del bucket
    gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
else
    echo "✅ Bucket de Storage ya existe"
fi

# Crear secretos necesarios
echo "🔐 Configurando secretos..."

# Secret Key para Flask
if ! gcloud secrets describe flask-secret-key --project=$PROJECT_ID &>/dev/null; then
    echo "🔑 Creando Flask secret key..."
    echo "$(openssl rand -base64 64)" | gcloud secrets create flask-secret-key \
        --data-file=- \
        --project=$PROJECT_ID
fi

# Password de base de datos
if ! gcloud secrets describe db-password --project=$PROJECT_ID &>/dev/null; then
    echo "🔑 Creando password de base de datos..."
    echo "$(openssl rand -base64 32)" | gcloud secrets create db-password \
        --data-file=- \
        --project=$PROJECT_ID
fi

# Crear VPC Connector en región europea (si no existe)
echo "🌐 Configurando VPC Connector en región europea..."
if ! gcloud compute networks vpc-access connectors describe gmao-connector \
    --region=$REGION --project=$PROJECT_ID &>/dev/null; then
    echo "📦 Creando VPC Connector en $REGION..."
    gcloud compute networks vpc-access connectors create gmao-connector \
        --region=$REGION \
        --subnet-project=$PROJECT_ID \
        --subnet=default \
        --min-instances=2 \
        --max-instances=3 \
        --project=$PROJECT_ID
else
    echo "✅ VPC Connector ya existe"
fi

# Ejecutar migraciones de base de datos
echo "🗄️ Ejecutando migraciones de base de datos..."
# Aquí agregarías el comando para ejecutar las migraciones
# Por ejemplo: python manage.py db upgrade

# Deployment a App Engine
echo "🚀 Desplegando a App Engine..."
gcloud app deploy app-production.yaml \
    --project=$PROJECT_ID \
    --version=v$(date +%Y%m%d-%H%M%S) \
    --promote \
    --stop-previous-version

# Obtener URL de la aplicación
echo ""
echo "🎉 ¡DEPLOYMENT COMPLETADO!"
echo "=========================="
APP_URL=$(gcloud app browse --project=$PROJECT_ID --no-launch-browser)
echo "🌐 URL de la aplicación: $APP_URL"
echo "📊 Panel de control: https://console.cloud.google.com/appengine?project=$PROJECT_ID"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Configurar dominio personalizado (si es necesario)"
echo "   2. Configurar certificados SSL"
echo "   3. Configurar monitoring y alertas"
echo "   4. Ejecutar pruebas de aceptación"
echo ""
echo "✅ Sistema GMAO desplegado exitosamente en Disfood"