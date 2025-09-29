#Requires -RunAsAdministrator

# Script para configurar PostgreSQL para desarrollo local
Write-Host "Configurando PostgreSQL para desarrollo local..." -ForegroundColor Green

# Detener PostgreSQL
Write-Host "Deteniendo PostgreSQL..." -ForegroundColor Yellow
Stop-Service -Name "postgresql-x64-16" -ErrorAction SilentlyContinue

# Ruta al archivo de configuración
$pgHbaConf = "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"

# Backup del archivo original
$backupFile = "$pgHbaConf.backup"
if (!(Test-Path $backupFile)) {
    Copy-Item $pgHbaConf $backupFile
    Write-Host "Backup creado: $backupFile" -ForegroundColor Green
}

# Agregar configuración de desarrollo al final del archivo
$configLines = @"
# Configuración para desarrollo local - permite conexiones sin contraseña
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
"@

Add-Content -Path $pgHbaConf -Value $configLines
Write-Host "Configuración agregada a pg_hba.conf" -ForegroundColor Green

# Reiniciar PostgreSQL
Write-Host "Reiniciando PostgreSQL..." -ForegroundColor Yellow
Start-Service -Name "postgresql-x64-16"

Write-Host "PostgreSQL configurado exitosamente para desarrollo local!" -ForegroundColor Green
Write-Host "Ahora puedes ejecutar la migración sin necesidad de contraseña." -ForegroundColor Cyan