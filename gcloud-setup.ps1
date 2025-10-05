# PowerShell Profile para GMAO - Deployment
# Agregar Google Cloud SDK al PATH automáticamente

$env:PATH += ";C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"

# Alias útiles
Set-Alias gcloud "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

# Configurar proyecto por defecto
# gcloud config set project gmao-sistema-2025

Write-Host "✅ Google Cloud SDK cargado" -ForegroundColor Green
Write-Host "📦 Proyecto: gmao-sistema-2025" -ForegroundColor Cyan
