# Script de Pruebas Automatizadas - Sistema GMAO
# Fecha: 2 de octubre de 2025

$baseUrl = "https://gmao-sistema-2025.ew.r.appspot.com"
$logFile = "resultados_pruebas_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

Write-Host "🧪 INICIANDO PRUEBAS AUTOMATIZADAS DEL SISTEMA GMAO" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host "URL: $baseUrl"
Write-Host "Log: $logFile"
Write-Host "=" * 70
Write-Host ""

# Función para logging
function Write-Log {
    param($message, $color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] $message"
    Write-Host $logMessage -ForegroundColor $color
    Add-Content -Path $logFile -Value $logMessage
}

# Iniciar log
Write-Log "=== INICIO DE PRUEBAS ===" "Cyan"
Write-Log "Versión: 20251002t210935"
Write-Log ""

# ====================
# TEST 1: Conectividad
# ====================
Write-Log "TEST 1: Verificando conectividad básica..." "Yellow"
try {
    $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Log "✅ PASS - Aplicación responde (HTTP 200)" "Green"
        Write-Log "   Content-Type: $($response.Headers['Content-Type'])"
        Write-Log "   Content-Length: $($response.RawContentLength) bytes"
    }
    else {
        Write-Log "❌ FAIL - Status Code: $($response.StatusCode)" "Red"
    }
}
catch {
    Write-Log "❌ FAIL - Error de conexión: $($_.Exception.Message)" "Red"
}
Write-Log ""

# ====================
# TEST 2: Tiempo de respuesta
# ====================
Write-Log "TEST 2: Midiendo tiempo de respuesta..." "Yellow"
$startTime = Get-Date
try {
    $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing
    $endTime = Get-Date
    $responseTime = ($endTime - $startTime).TotalMilliseconds
    
    if ($responseTime -lt 3000) {
        Write-Log "✅ PASS - Tiempo de respuesta: $([math]::Round($responseTime, 2))ms (< 3000ms)" "Green"
    }
    elseif ($responseTime -lt 5000) {
        Write-Log "⚠️  WARN - Tiempo de respuesta: $([math]::Round($responseTime, 2))ms (> 3000ms)" "Yellow"
    }
    else {
        Write-Log "❌ FAIL - Tiempo de respuesta: $([math]::Round($responseTime, 2))ms (> 5000ms)" "Red"
    }
}
catch {
    Write-Log "❌ FAIL - Error: $($_.Exception.Message)" "Red"
}
Write-Log ""

# ====================
# TEST 3: HTTPS y Certificado
# ====================
Write-Log "TEST 3: Verificando HTTPS y certificado SSL..." "Yellow"
try {
    $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing
    if ($baseUrl.StartsWith("https://")) {
        Write-Log "✅ PASS - HTTPS activo" "Green"
        Write-Log "   URL segura: $baseUrl"
    }
    else {
        Write-Log "❌ FAIL - No usa HTTPS" "Red"
    }
}
catch {
    Write-Log "❌ FAIL - Error SSL: $($_.Exception.Message)" "Red"
}
Write-Log ""

# ====================
# TEST 4: Cookies de Sesión
# ====================
Write-Log "TEST 4: Verificando configuración de cookies..." "Yellow"
try {
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $response = Invoke-WebRequest -Uri $baseUrl -WebSession $session -UseBasicParsing
    
    if ($session.Cookies.Count -gt 0) {
        Write-Log "✅ PASS - Cookies configuradas" "Green"
        foreach ($cookie in $session.Cookies.GetCookies($baseUrl)) {
            Write-Log "   Cookie: $($cookie.Name)"
            Write-Log "   HttpOnly: $($cookie.HttpOnly)"
            Write-Log "   Secure: $($cookie.Secure)"
            if ($cookie.Expires -eq [DateTime]::MinValue) {
                Write-Log "   Expires: Session (✅ Correcto para logout al cerrar)" "Green"
            }
            else {
                Write-Log "   Expires: $($cookie.Expires) (⚠️  Cookie persistente)" "Yellow"
            }
        }
    }
    else {
        Write-Log "⚠️  WARN - No se detectaron cookies (normal en GET inicial)" "Yellow"
    }
}
catch {
    Write-Log "❌ FAIL - Error: $($_.Exception.Message)" "Red"
}
Write-Log ""

# ====================
# TEST 5: Endpoints Críticos
# ====================
Write-Log "TEST 5: Verificando endpoints críticos..." "Yellow"

$endpoints = @(
    @{Path = "/"; Name = "Login Page"; ExpectedStatus = 200 },
    @{Path = "/dashboard"; Name = "Dashboard"; ExpectedStatus = 302 },  # Debe redirigir si no hay login
    @{Path = "/solicitudes/nueva"; Name = "Nueva Solicitud"; ExpectedStatus = 200 },  # Público
    @{Path = "/activos"; Name = "Activos"; ExpectedStatus = 302 },  # Requiere login
    @{Path = "/static/css/style.css"; Name = "CSS Principal"; ExpectedStatus = 200 }
)

foreach ($endpoint in $endpoints) {
    try {
        $url = $baseUrl + $endpoint.Path
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue
        $actualStatus = $response.StatusCode
    }
    catch {
        $actualStatus = $_.Exception.Response.StatusCode.Value__
    }
    
    if ($actualStatus -eq $endpoint.ExpectedStatus) {
        Write-Log "✅ PASS - $($endpoint.Name): HTTP $actualStatus" "Green"
    }
    else {
        Write-Log "❌ FAIL - $($endpoint.Name): Expected $($endpoint.ExpectedStatus), Got $actualStatus" "Red"
    }
}
Write-Log ""

# ====================
# TEST 6: Contenido de Login
# ====================
Write-Log "TEST 6: Verificando contenido de página de login..." "Yellow"
try {
    $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing
    $content = $response.Content
    
    # Verificar elementos clave
    $checks = @(
        @{Pattern = '<input.*name="username"'; Description = "Campo username" },
        @{Pattern = '<input.*name="password"'; Description = "Campo password" },
        @{Pattern = 'csrf_token'; Description = "CSRF token" },
        @{Pattern = 'Solicitar Servicio'; Description = "Botón solicitar servicio (NUEVO)" },
        @{Pattern = 'No necesitas iniciar sesión'; Description = "Mensaje informativo (NUEVO)" },
        @{Pattern = '<div class="divider-text">'; Description = "Divisor 'o' (NUEVO)" }
    )
    
    foreach ($check in $checks) {
        if ($content -match $check.Pattern) {
            Write-Log "✅ PASS - $($check.Description) encontrado" "Green"
        }
        else {
            Write-Log "❌ FAIL - $($check.Description) NO encontrado" "Red"
        }
    }
}
catch {
    Write-Log "❌ FAIL - Error: $($_.Exception.Message)" "Red"
}
Write-Log ""

# ====================
# TEST 7: Formulario de Solicitud
# ====================
Write-Log "TEST 7: Verificando formulario de solicitud pública..." "Yellow"
try {
    $url = "$baseUrl/solicitudes/nueva"
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing
    $content = $response.Content
    
    $checks = @(
        @{Pattern = '<input.*name="nombre"'; Description = "Campo nombre" },
        @{Pattern = '<input.*name="email"'; Description = "Campo email" },
        @{Pattern = '<input.*name="telefono"'; Description = "Campo teléfono" },
        @{Pattern = '<textarea.*name="descripcion"'; Description = "Campo descripción" },
        @{Pattern = '<input.*type="file"'; Description = "Input de archivos" }
    )
    
    $allPassed = $true
    foreach ($check in $checks) {
        if ($content -match $check.Pattern) {
            Write-Log "✅ PASS - $($check.Description) encontrado" "Green"
        }
        else {
            Write-Log "❌ FAIL - $($check.Description) NO encontrado" "Red"
            $allPassed = $false
        }
    }
    
    if ($allPassed) {
        Write-Log "✅ FORMULARIO COMPLETO - Todos los campos presentes" "Green"
    }
}
catch {
    Write-Log "❌ FAIL - Error al cargar formulario: $($_.Exception.Message)" "Red"
}
Write-Log ""

# ====================
# TEST 8: Recursos Estáticos
# ====================
Write-Log "TEST 8: Verificando carga de recursos estáticos..." "Yellow"

$resources = @(
    @{Path = "/static/css/style.css"; Type = "CSS" },
    @{Path = "/static/css/login.css"; Type = "CSS" },
    @{Path = "/static/js/main.js"; Type = "JavaScript" }
)

foreach ($resource in $resources) {
    try {
        $url = $baseUrl + $resource.Path
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $size = [math]::Round($response.RawContentLength / 1024, 2)
            Write-Log "✅ PASS - $($resource.Type): $($resource.Path) ($size KB)" "Green"
        }
    }
    catch {
        Write-Log "❌ FAIL - $($resource.Type): $($resource.Path) - $($_.Exception.Message)" "Red"
    }
}
Write-Log ""

# ====================
# TEST 9: Headers de Seguridad
# ====================
Write-Log "TEST 9: Verificando headers de seguridad..." "Yellow"
try {
    $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing
    
    $securityHeaders = @(
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Strict-Transport-Security"
    )
    
    foreach ($header in $securityHeaders) {
        if ($response.Headers[$header]) {
            Write-Log "✅ PASS - $header: $($response.Headers[$header])" "Green"
        }
        else {
            Write-Log "⚠️  WARN - $header: No presente (recomendado añadir)" "Yellow"
        }
    }
}
catch {
    Write-Log "❌ FAIL - Error: $($_.Exception.Message)" "Red"
}
Write-Log ""

# ====================
# TEST 10: Rendimiento de Múltiples Requests
# ====================
Write-Log "TEST 10: Test de rendimiento (10 requests concurrentes)..." "Yellow"
$times = @()
1..10 | ForEach-Object -Parallel {
    $start = Get-Date
    try {
        $response = Invoke-WebRequest -Uri $using:baseUrl -UseBasicParsing -TimeoutSec 10
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        $duration
    }
    catch {
        9999  # Valor alto si falla
    }
} -ThrottleLimit 10 | ForEach-Object {
    $times += $_
}

$avgTime = ($times | Measure-Object -Average).Average
$maxTime = ($times | Measure-Object -Maximum).Maximum
$minTime = ($times | Measure-Object -Minimum).Minimum

Write-Log "   Tiempo promedio: $([math]::Round($avgTime, 2))ms"
Write-Log "   Tiempo mínimo: $([math]::Round($minTime, 2))ms"
Write-Log "   Tiempo máximo: $([math]::Round($maxTime, 2))ms"

if ($avgTime -lt 2000) {
    Write-Log "✅ PASS - Rendimiento excelente (< 2000ms promedio)" "Green"
}
elseif ($avgTime -lt 5000) {
    Write-Log "⚠️  WARN - Rendimiento aceptable (< 5000ms)" "Yellow"
}
else {
    Write-Log "❌ FAIL - Rendimiento pobre (> 5000ms)" "Red"
}
Write-Log ""

# ====================
# RESUMEN FINAL
# ====================
Write-Log "=== RESUMEN DE PRUEBAS ===" "Cyan"
Write-Log "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Log "Versión: 20251002t210935"
Write-Log "URL: $baseUrl"
Write-Log ""
Write-Log "📊 Los resultados completos están en: $logFile" "Cyan"
Write-Log "=" * 70
Write-Host ""
Write-Host "✅ Pruebas automatizadas completadas" -ForegroundColor Green
Write-Host "📄 Revisa el archivo de log para detalles completos" -ForegroundColor Cyan
Write-Host ""
