# Script de PowerShell para backup automático de PostgreSQL
param(
    [string]$BackupDir = "C:\backups\postgresql",
    [int]$KeepDays = 30,
    [switch]$Compress = $true
)

# Crear directorio si no existe
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

# Generar timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupDir "gmao_backup_$timestamp.sql"
$logFile = Join-Path $BackupDir "backup_log.txt"

# Función para escribir en log
function Write-Log {
    param([string]$Message)
    $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry
}

Write-Log "Iniciando backup de PostgreSQL..."

try {
    # Ejecutar pg_dump
    $pgDumpPath = "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"
    $arguments = "-U postgres -h localhost -d gmao_db"

    $process = Start-Process -FilePath $pgDumpPath -ArgumentList $arguments -RedirectStandardOutput $backupFile -NoNewWindow -Wait -PassThru

    if ($process.ExitCode -eq 0) {
        Write-Log "Backup creado exitosamente: $backupFile"

        # Comprimir si está habilitado
        if ($Compress) {
            $zipFile = "$backupFile.7z"
            $sevenZipPath = "C:\Program Files\7-Zip\7z.exe"

            if (Test-Path $sevenZipPath) {
                $compressProcess = Start-Process -FilePath $sevenZipPath -ArgumentList "a `"$zipFile`" `"$backupFile`" -mx9" -NoNewWindow -Wait -PassThru

                if ($compressProcess.ExitCode -eq 0) {
                    Remove-Item $backupFile -Force
                    Write-Log "Backup comprimido: $zipFile"
                    $backupFile = $zipFile
                } else {
                    Write-Log "Advertencia: No se pudo comprimir el backup"
                }
            } else {
                Write-Log "Advertencia: 7-Zip no encontrado, backup sin comprimir"
            }
        }

        # Limpiar backups antiguos
        Write-Log "Limpiando backups antiguos (manteniendo $KeepDays días)..."
        $cutoffDate = (Get-Date).AddDays(-$KeepDays)

        Get-ChildItem -Path $BackupDir -Filter "gmao_backup_*.sql*" | Where-Object {
            $_.LastWriteTime -lt $cutoffDate
        } | ForEach-Object {
            Write-Log "Eliminando backup antiguo: $($_.Name)"
            Remove-Item $_.FullName -Force
        }

        # Mostrar información del backup
        $fileSize = (Get-Item $backupFile).Length / 1MB
        Write-Log ("Backup completado. Tamaño: {0:N2} MB" -f $fileSize)

    } else {
        throw "pg_dump falló con código de salida: $($process.ExitCode)"
    }

} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}

Write-Log "Backup completado exitosamente"