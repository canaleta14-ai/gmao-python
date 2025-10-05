# Script rapido de Lighthouse - Version simplificada
# Ejecuta auditoria y abre reporte automaticamente

Write-Host "`nLIGHTHOUSE AUDIT - GMAO`n" -ForegroundColor Cyan

$url = "https://gmao-sistema-2025.ew.r.appspot.com"
$output = "lighthouse-report-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

Write-Host "Ejecutando auditoria (1-2 minutos)...`n" -ForegroundColor Yellow

# Verificar si lighthouse esta instalado
try {
    lighthouse --version | Out-Null
} catch {
    Write-Host "ERROR: Lighthouse no esta instalado" -ForegroundColor Red
    Write-Host "Instalando Lighthouse...`n" -ForegroundColor Yellow
    npm install -g lighthouse
}

# Ejecutar Lighthouse
lighthouse $url `
    --output html `
    --output json `
    --output-path $output `
    --emulated-form-factor=mobile `
    --chrome-flags="--headless" `
    --locale=es

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAuditoria completada!" -ForegroundColor Green
    Write-Host "Reporte: $output.html`n" -ForegroundColor Cyan
    
    # Extraer puntuaciones
    $json = Get-Content "$output.json" -Raw | ConvertFrom-Json
    $perf = [math]::Round($json.categories.performance.score * 100)
    $a11y = [math]::Round($json.categories.accessibility.score * 100)
    $bp = [math]::Round($json.categories.'best-practices'.score * 100)
    $seo = [math]::Round($json.categories.seo.score * 100)
    
    Write-Host "PUNTUACIONES:" -ForegroundColor Yellow
    Write-Host "  Performance:    $perf/100" -ForegroundColor $(if($perf -ge 90){"Green"}elseif($perf -ge 50){"Yellow"}else{"Red"})
    Write-Host "  Accessibility:  $a11y/100" -ForegroundColor $(if($a11y -ge 90){"Green"}elseif($a11y -ge 50){"Yellow"}else{"Red"})
    Write-Host "  Best Practices: $bp/100" -ForegroundColor $(if($bp -ge 90){"Green"}elseif($bp -ge 50){"Yellow"}else{"Red"})
    Write-Host "  SEO:            $seo/100" -ForegroundColor $(if($seo -ge 90){"Green"}elseif($seo -ge 50){"Yellow"}else{"Red"})
    Write-Host ""
    
    # Abrir reporte
    Start-Process "$output.html"
} else {
    Write-Host "`nError ejecutando Lighthouse" -ForegroundColor Red
}
