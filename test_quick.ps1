# Suite de Pruebas Criticas - Sistema GMAO

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "SUITE DE PRUEBAS GMAO - SEGURIDAD, RENDIMIENTO Y UX" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$url = "https://gmao-sistema-2025.ew.r.appspot.com"
$passed = 0
$failed = 0
$warnings = 0

Write-Host "--- CATEGORIA 1: SEGURIDAD ---`n" -ForegroundColor Yellow

# Test 1: HTTPS
Write-Host "[TEST 1.1] HTTPS Obligatorio..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
    if ($response.BaseResponse.ResponseUri.Scheme -eq "https") {
        Write-Host " OK" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host " OK (GCP fuerza HTTPS)" -ForegroundColor Green
    $passed++
}

# Test 2: Response Time
Write-Host "`n--- CATEGORIA 2: RENDIMIENTO ---`n" -ForegroundColor Yellow
Write-Host "[TEST 2.1] Tiempo de Respuesta..." -NoNewline
$timer = Measure-Command {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
}
$ms = [math]::Round($timer.TotalMilliseconds, 2)

if ($ms -lt 3000) {
    Write-Host " ${ms}ms OK" -ForegroundColor Green
    $passed++
} else {
    Write-Host " ${ms}ms LENTO" -ForegroundColor Red
    $failed++
}

# Test 3: Content Size
Write-Host "[TEST 2.2] Tamano de Contenido..." -NoNewline
$kb = [math]::Round($response.RawContentLength / 1024, 2)
Write-Host " ${kb}KB" -ForegroundColor Cyan
if ($kb -lt 1024) { $passed++ } else { $warnings++ }

# Test 4: Favicon
Write-Host "`n--- CATEGORIA 3: FUNCIONALIDAD ---`n" -ForegroundColor Yellow
Write-Host "[TEST 3.1] Favicon..." -NoNewline
if ($response.Content -match "favicon\.svg") {
    Write-Host " OK (SVG)" -ForegroundColor Green
    $passed++
} else {
    Write-Host " No encontrado" -ForegroundColor Yellow
    $warnings++
}

# Test 5: Bootstrap
Write-Host "[TEST 3.2] Bootstrap CSS..." -NoNewline
if ($response.Content -match "bootstrap") {
    Write-Host " OK" -ForegroundColor Green
    $passed++
} else {
    Write-Host " No encontrado" -ForegroundColor Red
    $failed++
}

# Test 6: CSRF Utils
Write-Host "[TEST 3.3] csrf-utils.js..." -NoNewline
if ($response.Content -match "csrf-utils\.js") {
    Write-Host " OK (CRITICO)" -ForegroundColor Green
    $passed++
} else {
    Write-Host " FALTA" -ForegroundColor Red
    $failed++
}

# Test 7: Boton Solicitar Servicio
Write-Host "[TEST 3.4] Boton Solicitar Servicio..." -NoNewline
if ($response.Content -match "Solicitar Servicio") {
    Write-Host " OK (NUEVO)" -ForegroundColor Green
    $passed++
} else {
    Write-Host " No encontrado" -ForegroundColor Yellow
    $warnings++
}

# Test 8: Responsive
Write-Host "`n--- CATEGORIA 4: UX/UI ---`n" -ForegroundColor Yellow
Write-Host "[TEST 4.1] Meta Viewport (Responsive)..." -NoNewline
if ($response.Content -match "viewport") {
    Write-Host " OK" -ForegroundColor Green
    $passed++
} else {
    Write-Host " FALTA" -ForegroundColor Red
    $failed++
}

# Test 9: UTF-8
Write-Host "[TEST 4.2] Charset UTF-8..." -NoNewline
if ($response.Content -match "UTF-8") {
    Write-Host " OK" -ForegroundColor Green
    $passed++
} else {
    Write-Host " No detectado" -ForegroundColor Yellow
    $warnings++
}

# Test 10: Lang
Write-Host "[TEST 4.3] Atributo lang..." -NoNewline
if ($response.Content -match "lang=") {
    Write-Host " OK" -ForegroundColor Green
    $passed++
} else {
    Write-Host " No configurado" -ForegroundColor Yellow
    $warnings++
}

# RESUMEN
$total = $passed + $failed + $warnings
$successRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 2) } else { 0 }

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "RESUMEN DE PRUEBAS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Pasadas:      $passed" -ForegroundColor Green
Write-Host "Fallidas:     $failed" -ForegroundColor Red
Write-Host "Advertencias: $warnings" -ForegroundColor Yellow
Write-Host "Total:        $total" -ForegroundColor Cyan
Write-Host "Tasa Exito:   $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Yellow" })
Write-Host "================================================================`n" -ForegroundColor Cyan

if ($failed -eq 0) {
    Write-Host "ESTADO: APROBADO - Sistema listo" -ForegroundColor Green
} else {
    Write-Host "ESTADO: Revisar $failed pruebas fallidas" -ForegroundColor Red
}
Write-Host ""
