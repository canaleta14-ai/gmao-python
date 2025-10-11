# Deployment paso a paso para GMAO - Disfood España

Write-Host "🚀 DEPLOYMENT GMAO - DISFOOD ESPAÑA" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

$ProjectId = "mantenimiento-470311"
$Region = "europe-west1"

# Configurar proyecto
Write-Host "🔧 Configurando proyecto..." -ForegroundColor Yellow
gcloud config set project $ProjectId
gcloud config set compute/region $Region

Write-Host "✅ Proyecto configurado: $ProjectId" -ForegroundColor Green
Write-Host "✅ Región configurada: $Region" -ForegroundColor Green

# Habilitar APIs
Write-Host "🔌 Habilitando APIs necesarias..." -ForegroundColor Yellow
gcloud services enable appengine.googleapis.com --project=$ProjectId
gcloud services enable sqladmin.googleapis.com --project=$ProjectId  
gcloud services enable storage.googleapis.com --project=$ProjectId

Write-Host "✅ APIs habilitadas" -ForegroundColor Green

# Verificar App Engine
Write-Host "🚀 Verificando App Engine..." -ForegroundColor Yellow
$appDescribe = gcloud app describe --project=$ProjectId 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 Creando App Engine..." -ForegroundColor Cyan
    gcloud app create --region=$Region --project=$ProjectId
} else {
    Write-Host "✅ App Engine ya existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 Siguiente paso: Actualizar configuración para tu proyecto" -ForegroundColor Yellow
Write-Host "Ejecuta: python update_config.py" -ForegroundColor White