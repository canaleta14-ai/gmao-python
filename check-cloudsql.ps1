$gcloud = "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
$estado = & $gcloud sql instances describe gmao-postgres --format="value(state)"
Write-Host "Estado actual: $estado" -ForegroundColor $(if ($estado -eq "RUNNABLE") {"Green"} else {"Yellow"})

if ($estado -eq "RUNNABLE") {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "   CLOUD SQL ESTA LISTO!            " -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    & $gcloud sql instances describe gmao-postgres --format="table(name,state,ipAddresses[0].ipAddress,region,tier)"
} else {
    Write-Host "Todavia creandose. Espera 2-3 minutos mas." -ForegroundColor Yellow
}
