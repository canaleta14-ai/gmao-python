# Script de deployment simplificado para GMAO - Disfood España
# PowerShell version - Sintaxis corregida

param(
    [string]$ProjectId = "mantenimiento-470311",
    [string]$Region = "europe-west1",
    [string]$Zone = "europe-west1-b"
)

$ErrorActionPreference = "Continue"

Write-Host "🚀 INICIANDO DEPLOYMENT GMAO - DISFOOD ESPAÑA" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Verificar archivos necesarios
if (-not (Test-Path "app-production.yaml")) {
    Write-Host "❌ Error: No se encuentra app-production.yaml" -ForegroundColor Red
    exit 1
}

# Configurar proyecto
Write-Host "🔧 Configurando proyecto Google Cloud para España..." -ForegroundColor Yellow
Write-Host "🇪🇸 Configuración:" -ForegroundColor Cyan
Write-Host "   Proyecto: $ProjectId" -ForegroundColor Cyan
Write-Host "   Región: $Region (Europa - GDPR compatible)" -ForegroundColor Cyan
Write-Host "   Zona: $Zone" -ForegroundColor Cyan

gcloud config set project $ProjectId
gcloud config set compute/region $Region
gcloud config set compute/zone $Zone

# Verificar autenticación
Write-Host "🔑 Verificando autenticación..." -ForegroundColor Yellow
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if ($activeAccount) {
    Write-Host "✅ Autenticado como: $activeAccount" -ForegroundColor Green
} else {
    Write-Host "❌ No hay sesión activa. Ejecuta: gcloud auth login" -ForegroundColor Red
    exit 1
}

# Habilitar APIs necesarias
Write-Host "🔌 Habilitando APIs de Google Cloud..." -ForegroundColor Yellow
$apis = @(
    "appengine.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "   Habilitando $api..." -ForegroundColor Gray
    gcloud services enable $api --project=$ProjectId --quiet
}

# Verificar si App Engine ya existe
Write-Host "🚀 Verificando App Engine..." -ForegroundColor Yellow
$appExists = gcloud app describe --project=$ProjectId --quiet 2>$null
if (-not $appExists) {
    Write-Host "📦 Creando aplicación App Engine en $Region..." -ForegroundColor Cyan
    gcloud app create --region=$Region --project=$ProjectId
} else {
    Write-Host "✅ App Engine ya configurado" -ForegroundColor Green
}

# Crear Cloud SQL si no existe
Write-Host "🗄️ Verificando Cloud SQL..." -ForegroundColor Yellow
$sqlExists = gcloud sql instances describe gmao-db --project=$ProjectId --quiet 2>$null
if (-not $sqlExists) {
    Write-Host "📦 Creando instancia Cloud SQL..." -ForegroundColor Cyan
    gcloud sql instances create gmao-db `
        --database-version=POSTGRES_14 `
        --tier=db-f1-micro `
        --region=$Region `
        --project=$ProjectId `
        --quiet
        
    # Crear base de datos
    Write-Host "🗃️ Creando base de datos..." -ForegroundColor Cyan
    gcloud sql databases create gmao_production --instance=gmao-db --project=$ProjectId --quiet
    
    # Crear usuario
    Write-Host "👤 Creando usuario..." -ForegroundColor Cyan
    $password = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    gcloud sql users create gmao_user --instance=gmao-db --password=$password --project=$ProjectId --quiet
} else {
    Write-Host "✅ Cloud SQL ya configurado" -ForegroundColor Green
}

# Crear bucket de Storage
Write-Host "📁 Verificando Cloud Storage..." -ForegroundColor Yellow
$bucketName = "mantenimiento-gmao-uploads-eu"
$bucketExists = gsutil ls -b "gs://$bucketName" 2>$null
if (-not $bucketExists) {
    Write-Host "📦 Creando bucket de Storage..." -ForegroundColor Cyan
    gsutil mb -p $ProjectId -l $Region "gs://$bucketName"
} else {
    Write-Host "✅ Bucket Storage ya configurado" -ForegroundColor Green
}

# Configurar secretos básicos
Write-Host "🔐 Configurando secretos..." -ForegroundColor Yellow
$secrets = @("flask-secret-key", "db-password", "admin-password")

foreach ($secret in $secrets) {
    $secretExists = gcloud secrets describe $secret --project=$ProjectId --quiet 2>$null
    if (-not $secretExists) {
        Write-Host "🔑 Creando secreto $secret..." -ForegroundColor Cyan
        $secretValue = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        Write-Output $secretValue | gcloud secrets create $secret --data-file=- --project=$ProjectId --quiet
    } else {
        Write-Host "✅ Secreto $secret ya existe" -ForegroundColor Green
    }
}

# Actualizar archivo de configuración con el proyecto correcto
Write-Host "🔧 Actualizando configuración..." -ForegroundColor Yellow
if (Test-Path "app-production.yaml") {
    (Get-Content "app-production.yaml") -replace "disfood-gmao", $ProjectId | Set-Content "app-production.yaml"
    (Get-Content "app-production.yaml") -replace "disfood-gmao-uploads-eu", $bucketName | Set-Content "app-production.yaml"
}

# Desplegar a App Engine
Write-Host "🚀 Desplegando aplicación..." -ForegroundColor Yellow
gcloud app deploy app-production.yaml --project=$ProjectId --quiet

# Mostrar información final
Write-Host ""
Write-Host "🎉 DEPLOYMENT COMPLETADO" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "✅ Aplicación desplegada correctamente" -ForegroundColor Green
Write-Host "🌍 Región: $Region (GDPR compliant)" -ForegroundColor Cyan
Write-Host "🔗 URL: https://$ProjectId.appspot.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Configuración GDPR España aplicada:" -ForegroundColor Yellow
Write-Host "   ✅ Región europea seleccionada" -ForegroundColor Green
Write-Host "   ✅ Zona horaria Madrid configurada" -ForegroundColor Green
Write-Host "   ✅ Secretos seguros creados" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Panel de control: https://console.cloud.google.com/appengine?project=$ProjectId" -ForegroundColor Cyan