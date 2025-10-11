# Script de verificación del deployment para Windows
# PowerShell version

param(
    [string]$ProjectId = "disfood-gmao",
    [string]$Region = "europe-west1"
)

Write-Host "🔍 VERIFICANDO DEPLOYMENT GMAO - DISFOOD ESPAÑA" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

$allChecks = @()

# Función para registrar checks
function Add-Check {
    param($Name, $Status, $Details = "")
    $script:allChecks += [PSCustomObject]@{
        Name = $Name
        Status = $Status
        Details = $Details
    }
}

# Verificar autenticación gcloud
Write-Host "🔑 Verificando autenticación..." -ForegroundColor Yellow
try {
    $activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if ($activeAccount) {
        Add-Check "Autenticación gcloud" "✅" $activeAccount
    } else {
        Add-Check "Autenticación gcloud" "❌" "No hay sesión activa"
    }
} catch {
    Add-Check "Autenticación gcloud" "❌" "Error al verificar"
}

# Verificar proyecto configurado
Write-Host "📋 Verificando proyecto..." -ForegroundColor Yellow
try {
    $currentProject = gcloud config get-value project 2>$null
    if ($currentProject -eq $ProjectId) {
        Add-Check "Proyecto configurado" "✅" $ProjectId
    } else {
        Add-Check "Proyecto configurado" "❌" "Proyecto actual: $currentProject"
    }
} catch {
    Add-Check "Proyecto configurado" "❌" "Error al verificar"
}

# Verificar región configurada
Write-Host "🌍 Verificando región..." -ForegroundColor Yellow
try {
    $currentRegion = gcloud config get-value compute/region 2>$null
    if ($currentRegion -eq $Region) {
        Add-Check "Región europea" "✅" $Region
    } else {
        Add-Check "Región europea" "❌" "Región actual: $currentRegion"
    }
} catch {
    Add-Check "Región europea" "❌" "Error al verificar"
}

# Verificar APIs habilitadas
Write-Host "🔌 Verificando APIs..." -ForegroundColor Yellow
$requiredApis = @(
    "appengine.googleapis.com",
    "sqladmin.googleapis.com", 
    "storage.googleapis.com",
    "secretmanager.googleapis.com"
)

foreach ($api in $requiredApis) {
    try {
        $enabled = gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>$null
        if ($enabled) {
            Add-Check "API $api" "✅" "Habilitada"
        } else {
            Add-Check "API $api" "❌" "No habilitada"
        }
    } catch {
        Add-Check "API $api" "❌" "Error al verificar"
    }
}

# Verificar App Engine
Write-Host "🚀 Verificando App Engine..." -ForegroundColor Yellow
try {
    $appInfo = gcloud app describe --format="value(locationId)" 2>$null
    if ($appInfo) {
        Add-Check "App Engine" "✅" "Región: $appInfo"
    } else {
        Add-Check "App Engine" "❌" "No configurado"
    }
} catch {
    Add-Check "App Engine" "❌" "Error al verificar"
}

# Verificar Cloud SQL
Write-Host "🗄️ Verificando Cloud SQL..." -ForegroundColor Yellow
try {
    $sqlInfo = gcloud sql instances describe gmao-db --format="value(region)" 2>$null
    if ($sqlInfo) {
        Add-Check "Cloud SQL" "✅" "Región: $sqlInfo"
    } else {
        Add-Check "Cloud SQL" "❌" "Instancia no encontrada"
    }
} catch {
    Add-Check "Cloud SQL" "❌" "Error al verificar"
}

# Verificar Storage
Write-Host "📁 Verificando Cloud Storage..." -ForegroundColor Yellow
try {
    $bucketInfo = gsutil ls -L -b "gs://disfood-gmao-uploads-eu" 2>$null | Select-String "Location constraint:"
    if ($bucketInfo) {
        Add-Check "Cloud Storage" "✅" "Bucket configurado"
    } else {
        Add-Check "Cloud Storage" "❌" "Bucket no encontrado"
    }
} catch {
    Add-Check "Cloud Storage" "❌" "Error al verificar"
}

# Verificar secretos
Write-Host "🔐 Verificando secretos..." -ForegroundColor Yellow
$requiredSecrets = @("flask-secret-key", "db-password", "admin-password")

foreach ($secret in $requiredSecrets) {
    try {
        $secretExists = gcloud secrets describe $secret --format="value(name)" 2>$null
        if ($secretExists) {
            Add-Check "Secreto $secret" "✅" "Configurado"
        } else {
            Add-Check "Secreto $secret" "❌" "No encontrado"
        }
    } catch {
        Add-Check "Secreto $secret" "❌" "Error al verificar"
    }
}

# Verificar configuración GDPR
Write-Host "🔒 Verificando configuración GDPR..." -ForegroundColor Yellow

# Verificar variables de entorno GDPR
$gdprVars = @{
    "GDPR_COMPLIANCE" = $env:GDPR_COMPLIANCE
    "GCLOUD_REGION" = $env:GCLOUD_REGION
    "TIMEZONE" = $env:TIMEZONE
    "DATA_RETENTION_YEARS" = $env:DATA_RETENTION_YEARS
}

foreach ($var in $gdprVars.Keys) {
    $value = $gdprVars[$var]
    if ($value) {
        Add-Check "Variable $var" "✅" $value
    } else {
        Add-Check "Variable $var" "❌" "No configurada"
    }
}

# Verificar archivos de configuración
Write-Host "📋 Verificando archivos de configuración..." -ForegroundColor Yellow
$requiredFiles = @(
    "app-production.yaml",
    "run_production.py", 
    "config_spain.py",
    "gdpr_compliance.py",
    "GDPR_ESPAÑA.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Add-Check "Archivo $file" "✅" "Existe"
    } else {
        Add-Check "Archivo $file" "❌" "No encontrado"
    }
}

# Mostrar resumen
Write-Host ""
Write-Host "📊 RESUMEN DE VERIFICACIÓN" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

$passed = ($allChecks | Where-Object { $_.Status -eq "✅" }).Count
$failed = ($allChecks | Where-Object { $_.Status -eq "❌" }).Count
$total = $allChecks.Count

Write-Host "✅ Checks pasados: $passed/$total" -ForegroundColor Green
Write-Host "❌ Checks fallidos: $failed/$total" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host ""
    Write-Host "🎉 ¡DEPLOYMENT VERIFICADO CORRECTAMENTE!" -ForegroundColor Green
    Write-Host "🇪🇸 Configuración España: COMPLETA" -ForegroundColor Green
    Write-Host "🔒 Cumplimiento GDPR: VERIFICADO" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ ALGUNOS CHECKS FALLARON" -ForegroundColor Yellow
    Write-Host "Revisa los detalles a continuación:" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 DETALLE DE CHECKS:" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

foreach ($check in $allChecks) {
    $color = if ($check.Status -eq "✅") { "Green" } else { "Red" }
    Write-Host "$($check.Status) $($check.Name)" -ForegroundColor $color
    if ($check.Details) {
        Write-Host "   └─ $($check.Details)" -ForegroundColor Gray
    }
}

# Verificar conectividad si la app está desplegada
Write-Host ""
Write-Host "🌐 Verificando conectividad..." -ForegroundColor Yellow
try {
    $appUrl = "https://$ProjectId.appspot.com"
    $response = Invoke-WebRequest -Uri $appUrl -Method GET -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✅ Aplicación accesible en: $appUrl" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Aplicación no accesible o no desplegada aún" -ForegroundColor Red
    Write-Host "   URL esperada: https://$ProjectId.appspot.com" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🔗 ENLACES ÚTILES:" -ForegroundColor Cyan
Write-Host "   • App Engine: https://console.cloud.google.com/appengine?project=$ProjectId" -ForegroundColor White
Write-Host "   • Cloud SQL: https://console.cloud.google.com/sql/instances?project=$ProjectId" -ForegroundColor White
Write-Host "   • Storage: https://console.cloud.google.com/storage/browser?project=$ProjectId" -ForegroundColor White
Write-Host "   • Logs: https://console.cloud.google.com/logs/query?project=$ProjectId" -ForegroundColor White