#!/bin/bash
# Script de verificación pre-despliegue para GCP

set -e

echo "🔍 Verificando configuración para despliegue en GCP..."

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI no está instalado"
    exit 1
fi

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null; then
    echo "❌ No estás autenticado en gcloud"
    exit 1
fi

# Verificar proyecto
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No hay proyecto configurado"
    exit 1
fi

echo "✅ Proyecto configurado: $PROJECT_ID"

# Verificar APIs
APIs=(
    "appengine.googleapis.com"
    "sqladmin.googleapis.com"
    "secretmanager.googleapis.com"
    "storage-api.googleapis.com"
)

for api in "${APIs[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo "✅ API habilitada: $api"
    else
        echo "❌ API no habilitada: $api"
        echo "   Ejecuta: gcloud services enable $api"
    fi
done

# Verificar Cloud SQL
if gcloud sql instances describe gmao-postgres --project=$PROJECT_ID &>/dev/null; then
    echo "✅ Instancia Cloud SQL existe: gmao-postgres"
else
    echo "❌ Instancia Cloud SQL no existe: gmao-postgres"
fi

# Verificar Secret Manager
SECRETS=("gmao-secret-key" "gmao-db-password" "gmao-openai-key")
for secret in "${SECRETS[@]}"; do
    if gcloud secrets describe $secret --project=$PROJECT_ID &>/dev/null; then
        echo "✅ Secret existe: $secret"
    else
        echo "❌ Secret no existe: $secret"
    fi
done

# Verificar Cloud Storage
BUCKET="${PROJECT_ID}-uploads"
if gsutil ls -b gs://$BUCKET &>/dev/null; then
    echo "✅ Bucket existe: $BUCKET"
else
    echo "❌ Bucket no existe: $BUCKET"
fi

# Verificar archivos de configuración
CONFIG_FILES=("app.yaml" "main.py" "requirements.txt" "Dockerfile")
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Archivo existe: $file"
    else
        echo "❌ Archivo no existe: $file"
    fi
done

echo ""
echo "🎯 Verificación completada. Revisa los elementos marcados con ❌ antes de desplegar."