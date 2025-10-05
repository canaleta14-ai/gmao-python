# ============================================================================
# Script de Auditoria Lighthouse - Sistema GMAO
# ============================================================================
# Ejecuta Google Lighthouse para analizar rendimiento, accesibilidad, 
# mejores practicas y SEO
# ============================================================================

Write-Host "`n" -NoNewline
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  LIGHTHOUSE AUDIT - SISTEMA GMAO" -ForegroundColor Cyan
Write-Host "  Analisis de Rendimiento, Accesibilidad, SEO y Mejores Practicas" -ForegroundColor Cyan
Write-Host "============================================================================`n" -ForegroundColor Cyan

# Configuracion
$URL = "https://gmao-sistema-2025.ew.r.appspot.com"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = ".\lighthouse-reports"
$reportBaseName = "gmao-lighthouse"

# Crear directorio para reportes si no existe
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
    Write-Host "[INFO] Directorio creado: $reportDir`n" -ForegroundColor Green
}

# Verificar si Lighthouse esta instalado
Write-Host "[1/5] Verificando instalacion de Lighthouse..." -ForegroundColor Yellow
try {
    $lighthouseVersion = lighthouse --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      Lighthouse instalado: $lighthouseVersion" -ForegroundColor Green
    }
    else {
        throw "Lighthouse no encontrado"
    }
}
catch {
    Write-Host "      Lighthouse NO esta instalado" -ForegroundColor Red
    Write-Host "`n[INSTALACION] Instalando Lighthouse via npm...`n" -ForegroundColor Yellow
    
    # Verificar si npm esta instalado
    try {
        npm --version | Out-Null
        Write-Host "      npm encontrado, instalando lighthouse..." -ForegroundColor Cyan
        npm install -g lighthouse
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "      Lighthouse instalado correctamente" -ForegroundColor Green
        }
        else {
            Write-Host "`n[ERROR] No se pudo instalar Lighthouse" -ForegroundColor Red
            Write-Host "Por favor, instala Node.js desde: https://nodejs.org/" -ForegroundColor Yellow
            Write-Host "Luego ejecuta: npm install -g lighthouse`n" -ForegroundColor Yellow
            exit 1
        }
    }
    catch {
        Write-Host "`n[ERROR] npm no esta instalado" -ForegroundColor Red
        Write-Host "Por favor, instala Node.js desde: https://nodejs.org/" -ForegroundColor Yellow
        Write-Host "Luego ejecuta este script nuevamente`n" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n[2/5] Configuracion del analisis..." -ForegroundColor Yellow
Write-Host "      URL: $URL" -ForegroundColor Cyan
Write-Host "      Directorio: $reportDir" -ForegroundColor Cyan
Write-Host "      Timestamp: $timestamp`n" -ForegroundColor Cyan

# ============================================================================
# ANALISIS MOBILE
# ============================================================================

Write-Host "[3/5] Ejecutando analisis MOBILE..." -ForegroundColor Yellow
Write-Host "      Esto puede tomar 1-2 minutos...`n" -ForegroundColor Cyan

$mobileReport = "$reportDir\${reportBaseName}_mobile_$timestamp"

try {
    lighthouse $URL `
        --output html `
        --output json `
        --output-path "$mobileReport" `
        --emulated-form-factor=mobile `
        --throttling-method=simulate `
        --chrome-flags="--headless --no-sandbox --disable-gpu" `
        --quiet `
        --locale=es
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      Analisis MOBILE completado" -ForegroundColor Green
        Write-Host "      Reporte: $mobileReport.html`n" -ForegroundColor Green
    }
    else {
        Write-Host "      Error en analisis MOBILE" -ForegroundColor Red
    }
}
catch {
    Write-Host "      Error ejecutando Lighthouse MOBILE: $_" -ForegroundColor Red
}

# ============================================================================
# ANALISIS DESKTOP
# ============================================================================

Write-Host "[4/5] Ejecutando analisis DESKTOP..." -ForegroundColor Yellow
Write-Host "      Esto puede tomar 1-2 minutos...`n" -ForegroundColor Cyan

$desktopReport = "$reportDir\${reportBaseName}_desktop_$timestamp"

try {
    lighthouse $URL `
        --output html `
        --output json `
        --output-path "$desktopReport" `
        --emulated-form-factor=desktop `
        --throttling-method=simulate `
        --chrome-flags="--headless --no-sandbox --disable-gpu" `
        --quiet `
        --locale=es
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      Analisis DESKTOP completado" -ForegroundColor Green
        Write-Host "      Reporte: $desktopReport.html`n" -ForegroundColor Green
    }
    else {
        Write-Host "      Error en analisis DESKTOP" -ForegroundColor Red
    }
}
catch {
    Write-Host "      Error ejecutando Lighthouse DESKTOP: $_" -ForegroundColor Red
}

# ============================================================================
# EXTRAER PUNTUACIONES
# ============================================================================

Write-Host "[5/5] Extrayendo puntuaciones..." -ForegroundColor Yellow

function Get-LighthouseScores {
    param($jsonPath)
    
    if (Test-Path $jsonPath) {
        try {
            $json = Get-Content $jsonPath -Raw | ConvertFrom-Json
            $categories = $json.categories
            
            return @{
                Performance   = [math]::Round($categories.performance.score * 100)
                Accessibility = [math]::Round($categories.accessibility.score * 100)
                BestPractices = [math]::Round($categories.'best-practices'.score * 100)
                SEO           = [math]::Round($categories.seo.score * 100)
            }
        }
        catch {
            return $null
        }
    }
    return $null
}

function Get-ScoreColor {
    param($score)
    
    if ($score -ge 90) { return "Green" }
    elseif ($score -ge 50) { return "Yellow" }
    else { return "Red" }
}

function Show-ScoreBar {
    param($score)
    
    $filled = [math]::Floor($score / 10)
    $empty = 10 - $filled
    
    $bar = ""
    for ($i = 0; $i -lt $filled; $i++) { $bar += "█" }
    for ($i = 0; $i -lt $empty; $i++) { $bar += "░" }
    
    return $bar
}

# Scores Mobile
$mobileScores = Get-LighthouseScores "$mobileReport.json"
$desktopScores = Get-LighthouseScores "$desktopReport.json"

Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "  RESULTADOS DEL ANALISIS" -ForegroundColor Cyan
Write-Host "============================================================================`n" -ForegroundColor Cyan

if ($mobileScores) {
    Write-Host "  MOBILE (Smartphone)" -ForegroundColor Magenta
    Write-Host "  ──────────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    Write-Host "  Performance:    " -NoNewline
    Write-Host "$($mobileScores.Performance)" -NoNewline -ForegroundColor (Get-ScoreColor $mobileScores.Performance)
    Write-Host "/100  $(Show-ScoreBar $mobileScores.Performance)" -ForegroundColor (Get-ScoreColor $mobileScores.Performance)
    
    Write-Host "  Accessibility:  " -NoNewline
    Write-Host "$($mobileScores.Accessibility)" -NoNewline -ForegroundColor (Get-ScoreColor $mobileScores.Accessibility)
    Write-Host "/100  $(Show-ScoreBar $mobileScores.Accessibility)" -ForegroundColor (Get-ScoreColor $mobileScores.Accessibility)
    
    Write-Host "  Best Practices: " -NoNewline
    Write-Host "$($mobileScores.BestPractices)" -NoNewline -ForegroundColor (Get-ScoreColor $mobileScores.BestPractices)
    Write-Host "/100  $(Show-ScoreBar $mobileScores.BestPractices)" -ForegroundColor (Get-ScoreColor $mobileScores.BestPractices)
    
    Write-Host "  SEO:            " -NoNewline
    Write-Host "$($mobileScores.SEO)" -NoNewline -ForegroundColor (Get-ScoreColor $mobileScores.SEO)
    Write-Host "/100  $(Show-ScoreBar $mobileScores.SEO)" -ForegroundColor (Get-ScoreColor $mobileScores.SEO)
    
    Write-Host ""
}

if ($desktopScores) {
    Write-Host "  DESKTOP (Ordenador)" -ForegroundColor Cyan
    Write-Host "  ──────────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    
    Write-Host "  Performance:    " -NoNewline
    Write-Host "$($desktopScores.Performance)" -NoNewline -ForegroundColor (Get-ScoreColor $desktopScores.Performance)
    Write-Host "/100  $(Show-ScoreBar $desktopScores.Performance)" -ForegroundColor (Get-ScoreColor $desktopScores.Performance)
    
    Write-Host "  Accessibility:  " -NoNewline
    Write-Host "$($desktopScores.Accessibility)" -NoNewline -ForegroundColor (Get-ScoreColor $desktopScores.Accessibility)
    Write-Host "/100  $(Show-ScoreBar $desktopScores.Accessibility)" -ForegroundColor (Get-ScoreColor $desktopScores.Accessibility)
    
    Write-Host "  Best Practices: " -NoNewline
    Write-Host "$($desktopScores.BestPractices)" -NoNewline -ForegroundColor (Get-ScoreColor $desktopScores.BestPractices)
    Write-Host "/100  $(Show-ScoreBar $desktopScores.BestPractices)" -ForegroundColor (Get-ScoreColor $desktopScores.BestPractices)
    
    Write-Host "  SEO:            " -NoNewline
    Write-Host "$($desktopScores.SEO)" -NoNewline -ForegroundColor (Get-ScoreColor $desktopScores.SEO)
    Write-Host "/100  $(Show-ScoreBar $desktopScores.SEO)" -ForegroundColor (Get-ScoreColor $desktopScores.SEO)
    
    Write-Host ""
}

Write-Host "============================================================================`n" -ForegroundColor Cyan

# ============================================================================
# INTERPRETACION DE RESULTADOS
# ============================================================================

Write-Host "INTERPRETACION DE PUNTUACIONES:" -ForegroundColor Yellow
Write-Host "  90-100:  " -NoNewline; Write-Host "Excelente" -ForegroundColor Green
Write-Host "  50-89:   " -NoNewline; Write-Host "Necesita mejora" -ForegroundColor Yellow
Write-Host "  0-49:    " -NoNewline; Write-Host "Pobre" -ForegroundColor Red
Write-Host ""

# Analisis y recomendaciones
if ($mobileScores) {
    $avgMobile = ($mobileScores.Performance + $mobileScores.Accessibility + $mobileScores.BestPractices + $mobileScores.SEO) / 4
    
    Write-Host "ESTADO MOBILE: " -NoNewline
    if ($avgMobile -ge 90) {
        Write-Host "EXCELENTE - Sistema optimizado" -ForegroundColor Green
    }
    elseif ($avgMobile -ge 70) {
        Write-Host "BUENO - Algunas mejoras recomendadas" -ForegroundColor Yellow
    }
    else {
        Write-Host "REQUIERE ATENCION - Optimizaciones necesarias" -ForegroundColor Red
    }
    
    # Recomendaciones especificas
    Write-Host "`nRECOMENDACIONES MOBILE:" -ForegroundColor Cyan
    if ($mobileScores.Performance -lt 80) {
        Write-Host "  - Performance: Optimizar imagenes, lazy loading, minificar CSS/JS" -ForegroundColor Yellow
    }
    if ($mobileScores.Accessibility -lt 90) {
        Write-Host "  - Accessibility: Revisar labels, contraste de colores, alt text" -ForegroundColor Yellow
    }
    if ($mobileScores.BestPractices -lt 80) {
        Write-Host "  - Best Practices: Actualizar librerias, HTTPS, security headers" -ForegroundColor Yellow
    }
    if ($mobileScores.SEO -lt 90) {
        Write-Host "  - SEO: Meta tags, structured data, robots.txt" -ForegroundColor Yellow
    }
}

Write-Host ""

# ============================================================================
# ARCHIVOS GENERADOS
# ============================================================================

Write-Host "ARCHIVOS GENERADOS:" -ForegroundColor Green
Write-Host "  Mobile:" -ForegroundColor Cyan
Write-Host "    - HTML: $mobileReport.html" -ForegroundColor White
Write-Host "    - JSON: $mobileReport.json" -ForegroundColor White
Write-Host "  Desktop:" -ForegroundColor Cyan
Write-Host "    - HTML: $desktopReport.html" -ForegroundColor White
Write-Host "    - JSON: $desktopReport.json" -ForegroundColor White

# ============================================================================
# CREAR REPORTE RESUMIDO
# ============================================================================

$summaryFile = "$reportDir\lighthouse_summary_$timestamp.txt"

$summary = @"
================================================================================
LIGHTHOUSE AUDIT SUMMARY - SISTEMA GMAO
================================================================================
Fecha: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
URL: $URL

MOBILE (Smartphone)
────────────────────────────────────────────────────────────────────────────
Performance:    $($mobileScores.Performance)/100
Accessibility:  $($mobileScores.Accessibility)/100
Best Practices: $($mobileScores.BestPractices)/100
SEO:            $($mobileScores.SEO)/100

DESKTOP (Ordenador)
────────────────────────────────────────────────────────────────────────────
Performance:    $($desktopScores.Performance)/100
Accessibility:  $($desktopScores.Accessibility)/100
Best Practices: $($desktopScores.BestPractices)/100
SEO:            $($desktopScores.SEO)/100

ARCHIVOS
────────────────────────────────────────────────────────────────────────────
Mobile HTML:    $mobileReport.html
Desktop HTML:   $desktopReport.html

INTERPRETACION
────────────────────────────────────────────────────────────────────────────
90-100:  Excelente
50-89:   Necesita mejora
0-49:    Pobre

================================================================================
"@

$summary | Out-File -FilePath $summaryFile -Encoding UTF8

Write-Host "`n  Resumen guardado en: $summaryFile`n" -ForegroundColor Green

# ============================================================================
# ABRIR REPORTES
# ============================================================================

Write-Host "ABRIR REPORTES:" -ForegroundColor Yellow
Write-Host "  Presiona [M] para abrir reporte MOBILE" -ForegroundColor Cyan
Write-Host "  Presiona [D] para abrir reporte DESKTOP" -ForegroundColor Cyan
Write-Host "  Presiona [A] para abrir AMBOS" -ForegroundColor Cyan
Write-Host "  Presiona [N] para salir sin abrir" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Tu eleccion"

switch ($choice.ToUpper()) {
    "M" {
        Write-Host "Abriendo reporte MOBILE..." -ForegroundColor Green
        Start-Process "$mobileReport.html"
    }
    "D" {
        Write-Host "Abriendo reporte DESKTOP..." -ForegroundColor Green
        Start-Process "$desktopReport.html"
    }
    "A" {
        Write-Host "Abriendo ambos reportes..." -ForegroundColor Green
        Start-Process "$mobileReport.html"
        Start-Sleep -Seconds 1
        Start-Process "$desktopReport.html"
    }
    default {
        Write-Host "Saliendo sin abrir reportes" -ForegroundColor Yellow
    }
}

Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "  AUDITORIA COMPLETADA" -ForegroundColor Green
Write-Host "============================================================================`n" -ForegroundColor Cyan

# ============================================================================
# NOTAS FINALES
# ============================================================================

Write-Host "NOTAS:" -ForegroundColor Yellow
Write-Host "  - Los reportes HTML contienen analisis detallados" -ForegroundColor White
Write-Host "  - Los archivos JSON pueden usarse para comparaciones" -ForegroundColor White
Write-Host "  - Ejecuta este script periodicamente para seguimiento" -ForegroundColor White
Write-Host "  - Compara con auditorias anteriores para ver progreso" -ForegroundColor White
Write-Host ""
