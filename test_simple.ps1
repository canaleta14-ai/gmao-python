# Script de Pruebas Automatizadas - Sistema GMAO
# Fecha: 2 de octubre de 2025

$baseUrl = "https://gmao-sistema-2025.ew.r.appspot.com"
$logFile = "resultados_pruebas.txt"

Write-Host "INICIANDO PRUEBAS AUTOMATIZADAS DEL SISTEMA GMAO" -ForegroundColor Cyan
Write-Host "=================================================================="
Write-Host "URL: $baseUrl"
Write-Host "=================================================================="
Write-Host ""

# TEST 1: Conectividad
Write-Host "[TEST 1] Verificando conectividad basica..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "[PASS] Aplicacion responde (HTTP 200)" -ForegroundColor Green
        Write-Host "       Content-Length: $($response.RawContentLength) bytes"
    }
}
catch {
    Write-Host "[FAIL] Error de conexion" -ForegroundColor Red
}
Write-Host ""

# TEST 2: Tiempo de respuesta
Write-Host "[TEST 2] Midiendo tiempo de respuesta..." -ForegroundColor Yellow
$startTime = Get-Date
try {
    $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing
    $endTime = Get-Date
    $responseTime = ($endTime - $startTime).TotalMilliseconds
    
    if ($responseTime -lt 3000) {
        Write-Host "[PASS] Tiempo: $([math]::Round($responseTime, 2))ms (< 3000ms)" -ForegroundColor Green
    }
    else {
        Write-Host "[WARN] Tiempo: $([math]::Round($responseTime, 2))ms (> 3000ms)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[FAIL] Error" -ForegroundColor Red
}
Write-Host ""

# TEST 3: Endpoints Criticos
Write-Host "[TEST 3] Verificando endpoints criticos..." -ForegroundColor Yellow

$tests = @(
    @{Name = "Login Page"; Path = "/"; Expected = 200 },
    @{Name = "Nueva Solicitud (Publico)"; Path = "/solicitudes/nueva"; Expected = 200 },
    @{Name = "Dashboard (Protegido)"; Path = "/dashboard"; Expected = 302 },
    @{Name = "CSS Principal"; Path = "/static/css/style.css"; Expected = 200 }
)

foreach ($test in $tests) {
    try {
        $url = $baseUrl + $test.Path
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue
        $status = $resp.StatusCode
    }
    catch {
        $status = $_.Exception.Response.StatusCode.Value__
    }
    
    if ($status -eq $test.Expected) {
        Write-Host "[PASS] $($test.Name) - HTTP $status" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] $($test.Name) - Expected $($test.Expected), Got $status" -ForegroundColor Red
    }
}
Write-Host ""

# TEST 4: Contenido de Login - NUEVAS FUNCIONALIDADES
Write-Host "[TEST 4] Verificando NUEVAS funcionalidades en login..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing
    $content = $response.Content
    
    # Verificar nuevos elementos
    if ($content -match 'Solicitar Servicio') {
        Write-Host "[PASS] Boton 'Solicitar Servicio' encontrado (NUEVA FUNCIONALIDAD)" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Boton 'Solicitar Servicio' NO encontrado" -ForegroundColor Red
    }
    
    if ($content -match 'No necesitas iniciar sesi') {
        Write-Host "[PASS] Mensaje informativo encontrado (NUEVA FUNCIONALIDAD)" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Mensaje informativo NO encontrado" -ForegroundColor Red
    }
    
    if ($content -match 'divider-text') {
        Write-Host "[PASS] Divisor 'o' encontrado (NUEVO ESTILO)" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Divisor NO encontrado" -ForegroundColor Red
    }
    
    if ($content -match 'csrf_token') {
        Write-Host "[PASS] CSRF token presente (Seguridad)" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] CSRF token NO encontrado" -ForegroundColor Red
    }
}
catch {
    Write-Host "[FAIL] Error al verificar contenido" -ForegroundColor Red
}
Write-Host ""

# TEST 5: Formulario de Solicitud
Write-Host "[TEST 5] Verificando formulario de solicitud publica..." -ForegroundColor Yellow
try {
    $url = "$baseUrl/solicitudes/nueva"
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing
    $content = $response.Content
    
    $requiredFields = @("nombre", "email", "telefono", "descripcion")
    $allPresent = $true
    
    foreach ($field in $requiredFields) {
        if ($content -match "name=`"$field`"") {
            Write-Host "[PASS] Campo '$field' presente" -ForegroundColor Green
        }
        else {
            Write-Host "[FAIL] Campo '$field' NO encontrado" -ForegroundColor Red
            $allPresent = $false
        }
    }
    
    if ($content -match 'type="file"') {
        Write-Host "[PASS] Input de archivos presente" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Input de archivos NO encontrado" -ForegroundColor Red
        $allPresent = $false
    }
    
    if ($allPresent) {
        Write-Host "[PASS] FORMULARIO COMPLETO" -ForegroundColor Green
    }
}
catch {
    Write-Host "[FAIL] Error al cargar formulario" -ForegroundColor Red
}
Write-Host ""

# TEST 6: Configuracion de Sesion (Cookie)
Write-Host "[TEST 6] Verificando configuracion de sesion..." -ForegroundColor Yellow
try {
    # Intentar login para obtener cookie
    $loginUrl = "$baseUrl/login"
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    
    # Primero GET para obtener CSRF token
    $loginPage = Invoke-WebRequest -Uri $baseUrl -WebSession $session -UseBasicParsing
    
    Write-Host "[INFO] Sesion iniciada, cookies configuradas:" -ForegroundColor Cyan
    
    if ($session.Cookies.Count -gt 0) {
        foreach ($cookie in $session.Cookies.GetCookies($baseUrl)) {
            Write-Host "       Cookie: $($cookie.Name)"
            Write-Host "       HttpOnly: $($cookie.HttpOnly)"
            Write-Host "       Secure: $($cookie.Secure)"
        }
        Write-Host "[PASS] Cookies de sesion configuradas" -ForegroundColor Green
    }
    else {
        Write-Host "[INFO] No hay cookies en GET inicial (normal)" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "[WARN] No se pudo verificar cookies" -ForegroundColor Yellow
}
Write-Host ""

# TEST 7: Recursos CSS (Nuevos estilos)
Write-Host "[TEST 7] Verificando nuevos estilos CSS..." -ForegroundColor Yellow
try {
    $cssUrl = "$baseUrl/static/css/login.css"
    $response = Invoke-WebRequest -Uri $cssUrl -UseBasicParsing
    $css = $response.Content
    
    if ($css -match 'divider-text') {
        Write-Host "[PASS] Estilos del divisor presentes" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Estilos del divisor NO encontrados" -ForegroundColor Red
    }
    
    if ($css -match 'btn-outline-primary.*hover') {
        Write-Host "[PASS] Efectos hover del boton presentes" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Efectos hover NO encontrados" -ForegroundColor Red
    }
    
    $size = [math]::Round($response.RawContentLength / 1024, 2)
    Write-Host "[INFO] Tamaño CSS: $size KB" -ForegroundColor Cyan
}
catch {
    Write-Host "[FAIL] Error al cargar CSS" -ForegroundColor Red
}
Write-Host ""

# RESUMEN
Write-Host "=================================================================="  -ForegroundColor Cyan
Write-Host "PRUEBAS AUTOMATIZADAS COMPLETADAS" -ForegroundColor Green
Write-Host "=================================================================="  -ForegroundColor Cyan
Write-Host ""
Write-Host "SIGUIENTES PASOS - VERIFICACION MANUAL:" -ForegroundColor Yellow
Write-Host "1. Abre en navegador: $baseUrl"
Write-Host "2. Verifica visualmente el boton 'Solicitar Servicio'"
Write-Host "3. Prueba el efecto hover (gradiente azul)"
Write-Host "4. Haz click y verifica redireccion a /solicitudes/nueva"
Write-Host "5. Login (admin/admin123) y verifica logout al cerrar navegador"
Write-Host ""
Write-Host "Para pruebas visuales detalladas, consulta: EJECUCION_PRUEBAS_ORDEN.md"
Write-Host ""
