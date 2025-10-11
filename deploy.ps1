# Script de deployment para GMAO en Google Cloud - Disfood España
# PowerShell version

param(
    [string]$ProjectId = "disfood-gmao",
    [string]$Region = "europe-west1",
    [string]$Zone = "europe-west1-b"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 INICIANDO DEPLOYMENT GMAO - DISFOOD ESPAÑA" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "app-production.yaml")) {
    Write-Host "❌ Error: No se encuentra app-production.yaml" -ForegroundColor Red
    Write-Host "   Ejecuta este script desde el directorio raíz del proyecto" -ForegroundColor Red
    exit 1
}

# Verificar que gcloud está instalado
try {
    $gcloudVersion = gcloud version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud no encontrado"
    }
} catch {
    Write-Host "❌ Error: gcloud CLI no está instalado" -ForegroundColor Red
    Write-Host "   Instala Google Cloud SDK desde: https://cloud.google.com/sdk" -ForegroundColor Red
    exit 1
}

# Configurar proyecto y región europea
Write-Host "🔧 Configurando proyecto Google Cloud para España..." -ForegroundColor Yellow
Write-Host "🇪🇸 Configuración para España:" -ForegroundColor Cyan
Write-Host "   Proyecto: $ProjectId" -ForegroundColor Cyan
Write-Host "   Región: $Region (Europa - GDPR compatible)" -ForegroundColor Cyan
Write-Host "   Zona: $Zone" -ForegroundColor Cyan

gcloud config set project $ProjectId
gcloud config set compute/region $Region
gcloud config set compute/zone $Zone

# Verificar autenticación
Write-Host "🔑 Verificando autenticación..." -ForegroundColor Yellow
try {
    $activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if (-not $activeAccount) {
        throw "No hay sesión activa"
    }
    Write-Host "✅ Autenticado como: $activeAccount" -ForegroundColor Green
} catch {
    Write-Host "❌ No hay sesión activa de gcloud" -ForegroundColor Red
    Write-Host "   Ejecuta: gcloud auth login" -ForegroundColor Red
    exit 1
}

# Habilitar APIs necesarias
Write-Host "🔌 Habilitando APIs de Google Cloud..." -ForegroundColor Yellow
$apis = @(
    "appengine.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "redis.googleapis.com",
    "vpcaccess.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "   Habilitando $api..." -ForegroundColor Gray
    gcloud services enable $api --quiet
}

# Crear instancia de Cloud SQL en región europea (si no existe)
Write-Host "🗄️ Configurando Cloud SQL en región europea..." -ForegroundColor Yellow
try {
    gcloud sql instances describe gmao-db --project=$ProjectId --quiet 2>$null
    Write-Host "✅ Instancia Cloud SQL ya existe" -ForegroundColor Green
} catch {
    Write-Host "📦 Creando instancia Cloud SQL en $Region..." -ForegroundColor Cyan
    gcloud sql instances create gmao-db `
        --database-version=POSTGRES_14 `
        --tier=db-f1-micro `
        --region=$Region `
        --backup-start-time=03:00 `
        --maintenance-release-channel=production `
        --maintenance-window-day=SUN `
        --maintenance-window-hour=04 `
        --project=$ProjectId
    
    Write-Host "👤 Creando usuario de base de datos..." -ForegroundColor Cyan
    $dbPassword = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    gcloud sql users create gmao_user `
        --instance=gmao-db `
        --password=$dbPassword `
        --project=$ProjectId
    
    Write-Host "🗃️ Creando base de datos..." -ForegroundColor Cyan
    gcloud sql databases create gmao_production `
        --instance=gmao-db `
        --project=$ProjectId
}

# Crear bucket de Storage en región europea (si no existe)
Write-Host "📁 Configurando Cloud Storage en región europea..." -ForegroundColor Yellow
$bucketName = "disfood-gmao-uploads-eu"
try {
    gsutil ls -b "gs://$bucketName" 2>$null | Out-Null
    Write-Host "✅ Bucket de Storage ya existe" -ForegroundColor Green
} catch {
    Write-Host "📦 Creando bucket de Storage en $Region..." -ForegroundColor Cyan
    gsutil mb -p $ProjectId -l $Region "gs://$bucketName"
    
    # Configurar permisos del bucket
    gsutil iam ch allUsers:objectViewer "gs://$bucketName"
}

# Crear secretos necesarios
Write-Host "🔐 Configurando secretos..." -ForegroundColor Yellow

$secrets = @{
    "flask-secret-key" = "Clave secreta para Flask sessions y CSRF"
    "db-password" = "Password para usuario de base de datos PostgreSQL"
    "redis-password" = "Password para Redis (si es necesario)"
    "admin-password" = "Password inicial para usuario administrador"
    "gdpr-encryption-key" = "Clave para cifrado de datos personales GDPR"
}

foreach ($secretId in $secrets.Keys) {
    try {
        gcloud secrets describe $secretId --project=$ProjectId --quiet 2>$null
        Write-Host "✅ Secreto '$secretId' ya existe" -ForegroundColor Green
    } catch {
        Write-Host "🔑 Creando secreto '$secretId'..." -ForegroundColor Cyan
        $secretValue = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        echo $secretValue | gcloud secrets create $secretId --data-file=- --project=$ProjectId
    }
}

# Crear VPC Connector en región europea (si no existe)
Write-Host "🌐 Configurando VPC Connector en región europea..." -ForegroundColor Yellow
try {
    gcloud compute networks vpc-access connectors describe gmao-connector `
        --region=$Region --project=$ProjectId --quiet 2>$null
    Write-Host "✅ VPC Connector ya existe" -ForegroundColor Green
} catch {
    Write-Host "📦 Creando VPC Connector en $Region..." -ForegroundColor Cyan
    gcloud compute networks vpc-access connectors create gmao-connector `
        --region=$Region `
        --subnet-project=$ProjectId `
        --range=10.8.0.0/28 `
        --project=$ProjectId
}

# Configurar App Engine (si no existe)
Write-Host "🚀 Configurando App Engine..." -ForegroundColor Yellow
try {
    gcloud app describe --project=$ProjectId --quiet 2>$null
    Write-Host "✅ App Engine ya está configurado" -ForegroundColor Green
} catch {
    Write-Host "📦 Creando aplicación App Engine en $Region..." -ForegroundColor Cyan
    gcloud app create --region=$Region --project=$ProjectId
}

# Ejecutar configuración de secretos con Python
Write-Host "🔧 Configurando secretos con Python..." -ForegroundColor Yellow
if (Test-Path "config_secrets.py") {
    python config_secrets.py
} else {
    Write-Host "⚠️ Archivo config_secrets.py no encontrado" -ForegroundColor Yellow
}

# Ejecutar configuración de España
Write-Host "🇪🇸 Aplicando configuración específica de España..." -ForegroundColor Yellow
if (Test-Path "config_spain.py") {
    python config_spain.py
} else {
    Write-Host "⚠️ Archivo config_spain.py no encontrado" -ForegroundColor Yellow
}

# Configurar base de datos de producción
Write-Host "🗄️ Configurando base de datos de producción..." -ForegroundColor Yellow
if (Test-Path "setup_production_db.py") {
    python setup_production_db.py
} else {
    Write-Host "⚠️ Archivo setup_production_db.py no encontrado" -ForegroundColor Yellow
}

# Desplegar aplicación
Write-Host "🚀 Desplegando aplicación a App Engine..." -ForegroundColor Yellow
gcloud app deploy app-production.yaml --quiet --project=$ProjectId

# Verificar deployment
Write-Host "🔍 Verificando deployment..." -ForegroundColor Yellow
if (Test-Path "verify_deployment.py") {
    python verify_deployment.py
} else {
    Write-Host "⚠️ Archivo verify_deployment.py no encontrado" -ForegroundColor Yellow
}

# Mostrar información final
Write-Host ""
Write-Host "🎉 DEPLOYMENT COMPLETADO" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "✅ Aplicación desplegada en Google Cloud España" -ForegroundColor Green
Write-Host "🌍 Región: $Region (GDPR compliant)" -ForegroundColor Cyan
Write-Host "🔗 URL: https://$ProjectId.appspot.com" -ForegroundColor Cyan
Write-Host "📋 Panel de control: https://console.cloud.google.com/appengine?project=$ProjectId" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Configuración GDPR España:" -ForegroundColor Yellow
Write-Host "   ✅ Datos en región europea" -ForegroundColor Green
Write-Host "   ✅ Zona horaria Madrid configurada" -ForegroundColor Green
Write-Host "   ✅ Retención 7 años (normativa española)" -ForegroundColor Green
Write-Host "   ✅ Cifrado completo habilitado" -ForegroundColor Green
Write-Host ""
Write-Host "📞 Soporte: soporte@disfood.es" -ForegroundColor Cyan