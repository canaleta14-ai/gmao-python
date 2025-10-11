# Script para configurar variables de entorno de España localmente
# PowerShell version

Write-Host "🇪🇸 Configurando variables de entorno para España..." -ForegroundColor Green

# Variables de región y localización
$env:GCLOUD_REGION = "europe-west1"
$env:TIMEZONE = "Europe/Madrid"
$env:LANGUAGE = "es"
$env:LOCALE = "es_ES.UTF-8"

# Variables GDPR
$env:GDPR_COMPLIANCE = "true"
$env:DATA_RETENTION_DAYS = "2555"
$env:DATA_RETENTION_YEARS = "7"

# Variables específicas de España
$env:COMPANY_COUNTRY = "ES"
$env:WORKING_HOURS_START = "08:00"
$env:WORKING_HOURS_END = "18:00"
$env:WORKING_DAYS = "0,1,2,3,4"

# Festivos nacionales españoles
$env:NATIONAL_HOLIDAYS = "01-01,01-06,05-01,08-15,10-12,11-01,12-06,12-08,12-25"

# Variables de formato
$env:DATE_FORMAT = "%d/%m/%Y"
$env:DATETIME_FORMAT = "%d/%m/%Y %H:%M"

Write-Host "✅ Variables de entorno configuradas:" -ForegroundColor Green
Write-Host "   🌍 Región: $env:GCLOUD_REGION" -ForegroundColor Cyan
Write-Host "   🕐 Zona horaria: $env:TIMEZONE" -ForegroundColor Cyan
Write-Host "   🗣️ Idioma: $env:LANGUAGE" -ForegroundColor Cyan
Write-Host "   📋 GDPR: $env:GDPR_COMPLIANCE" -ForegroundColor Cyan
Write-Host "   📅 Retención: $env:DATA_RETENTION_YEARS años" -ForegroundColor Cyan
Write-Host "   🏢 Horario: $env:WORKING_HOURS_START - $env:WORKING_HOURS_END" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 Para aplicar estas variables en tu sesión actual:" -ForegroundColor Yellow
Write-Host "   . .\configure_spain_env.ps1" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Para desplegar a Google Cloud:" -ForegroundColor Yellow
Write-Host "   .\deploy.ps1" -ForegroundColor White