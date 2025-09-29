@echo off
REM Script para backup automático de PostgreSQL
REM Uso: backup_postgres.bat [directorio_backup]

if "%~1"=="" (
    set BACKUP_DIR=C:\backups\postgresql
) else (
    set BACKUP_DIR=%~1
)

REM Crear directorio si no existe
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Generar nombre del archivo con timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

set BACKUP_FILE=%BACKUP_DIR%\gmao_backup_%TIMESTAMP%.sql

echo Creando backup de PostgreSQL...
echo Archivo: %BACKUP_FILE%

REM Ejecutar pg_dump
"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" -U postgres -h localhost -d gmao_db > "%BACKUP_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo Backup completado exitosamente: %BACKUP_FILE%
    REM Comprimir el archivo (requiere 7zip instalado)
    if exist "C:\Program Files\7-Zip\7z.exe" (
        "C:\Program Files\7-Zip\7z.exe" a "%BACKUP_FILE%.7z" "%BACKUP_FILE%" -mx9
        if %ERRORLEVEL% EQU 0 (
            del "%BACKUP_FILE%"
            echo Backup comprimido: %BACKUP_FILE%.7z
        )
    )
) else (
    echo ERROR: Falló la creación del backup
    exit /b 1
)

echo Backup completado.
goto :eof