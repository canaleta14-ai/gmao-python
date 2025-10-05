# Script para verificar el estado de Cloud SQL
Write-Host "Monitoreando Cloud SQL Instance: gmao-postgres" -ForegroundColor Cyan
Write-Host ""

$MaxIntentos = 10
$IntervaloSegundos = 30
$intentos = 0

while ($intentos -lt $MaxIntentos) {
    $intentos++
    $estado = gcloud sql instances describe gmao-postgres --format="value(state)"
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    Write-Host "[$timestamp] Intento $intentos/$MaxIntentos - Estado: $estado" -ForegroundColor Gray
    
    if ($estado -eq "RUNNABLE") {
        Write-Host ""
        Write-Host "CLOUD SQL ESTA LISTO!" -ForegroundColor Green
        Write-Host ""
        gcloud sql instances describe gmao-postgres --format="table(name,databaseVersion,region,tier,state)"
        Write-Host ""
        Write-Host "Proximos pasos:" -ForegroundColor Yellow
        Write-Host "  1. Ejecutar: .\scripts\paso4-secret-manager.ps1" -ForegroundColor White
        exit 0
    }
    
    if ($intentos -lt $MaxIntentos) {
        Write-Host "Esperando $IntervaloSegundos segundos..." -ForegroundColor Gray
        Start-Sleep -Seconds $IntervaloSegundos
    }
}

Write-Host ""
Write-Host "Tiempo agotado. La instancia todavia esta creandose." -ForegroundColor Yellow
exit 1
