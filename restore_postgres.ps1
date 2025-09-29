# Script de PowerShell para restaurar backup de PostgreSQL
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$Database = "gmao_db",
    [switch]$Force
)

$logFile = "C:\backups\postgresql\restore_log.txt"

# Crear directorio de logs si no existe
$logDir = Split-Path $logFile -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Función para escribir en log
function Write-Log {
    param([string]$Message)
    $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry
}

# Verificar que el archivo existe
if (!(Test-Path $BackupFile)) {
    Write-Log "ERROR: Archivo de backup no encontrado: $BackupFile"
    exit 1
}

# Si es un archivo comprimido, descomprimirlo
if ($BackupFile -like "*.7z") {
    $extractedFile = $BackupFile -replace "\.7z$", ".sql"
    $sevenZipPath = "C:\Program Files\7-Zip\7z.exe"

    if (Test-Path $sevenZipPath) {
        Write-Log "Descomprimiendo backup: $BackupFile"
        $extractProcess = Start-Process -FilePath $sevenZipPath -ArgumentList "e `"$BackupFile`" -o`"$((Get-Item $BackupFile).DirectoryName)`" -y" -NoNewWindow -Wait -PassThru

        if ($extractProcess.ExitCode -ne 0) {
            Write-Log "ERROR: Falló la descompresión del backup"
            exit 1
        }
        $BackupFile = $extractedFile
    } else {
        Write-Log "ERROR: 7-Zip no encontrado, no se puede descomprimir"
        exit 1
    }
}

Write-Log "Iniciando restauración de backup: $BackupFile"

# Confirmación si no se usó -Force
if (!$Force) {
    $confirmation = Read-Host "⚠️  Esta acción SOBREESCRIBIRÁ la base de datos '$Database'. ¿Continuar? (s/n)"
    if ($confirmation -ne 's' -and $confirmation -ne 'S') {
        Write-Log "Restauración cancelada por el usuario"
        exit 0
    }
}

try {
    # Detener la aplicación si está ejecutándose (opcional)
    Write-Log "Verificando si la aplicación está ejecutándose..."

    # Crear backup de seguridad antes de restaurar
    $safetyBackup = "C:\backups\postgresql\safety_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    Write-Log "Creando backup de seguridad: $safetyBackup"

    $pgDumpPath = "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"
    $dumpProcess = Start-Process -FilePath $pgDumpPath -ArgumentList "-U postgres -h localhost -d $Database" -RedirectStandardOutput $safetyBackup -NoNewWindow -Wait -PassThru

    if ($dumpProcess.ExitCode -ne 0) {
        Write-Log "Advertencia: No se pudo crear backup de seguridad"
    }

    # Restaurar la base de datos
    Write-Log "Restaurando base de datos..."

    # Primero, crear la base de datos si no existe
    $psqlPath = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
    $createDbProcess = Start-Process -FilePath $psqlPath -ArgumentList "-U postgres -h localhost -c `"CREATE DATABASE IF NOT EXISTS $Database`"" -NoNewWindow -Wait -PassThru

    # Restaurar desde el archivo
    $restoreProcess = Start-Process -FilePath $psqlPath -ArgumentList "-U postgres -h localhost -d $Database" -RedirectStandardInput $BackupFile -NoNewWindow -Wait -PassThru

    if ($restoreProcess.ExitCode -eq 0) {
        Write-Log "Restauración completada exitosamente"

        # Verificar la restauración
        $verifyProcess = Start-Process -FilePath $psqlPath -ArgumentList "-U postgres -h localhost -d $Database -c `"SELECT COUNT(*) FROM usuario`"" -NoNewWindow -Wait -PassThru

        Write-Log "Verificación completada"
    } else {
        throw "La restauración falló con código de salida: $($restoreProcess.ExitCode)"
    }

} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}

Write-Log "Restauración completada exitosamente"