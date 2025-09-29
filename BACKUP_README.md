# Sistema de Backup y Restauración PostgreSQL - GMAO

## 📋 Descripción
Sistema automatizado para crear backups diarios de la base de datos PostgreSQL del sistema GMAO y restaurarlos cuando sea necesario.

## 🗂️ Archivos del Sistema

### Scripts de Backup
- `backup_postgres.ps1` - Script principal para crear backups
- `backup_postgres.bat` - Versión batch simplificada
- `restore_postgres.ps1` - Script para restaurar backups

### Tarea Programada
- **Nombre**: `PostgreSQL_Backup_GMAO`
- **Frecuencia**: Diaria a las 2:00 AM
- **Ubicación**: Programador de tareas de Windows

## 🚀 Uso del Sistema de Backup

### Backup Manual
```powershell
# Backup básico
.\backup_postgres.ps1

# Backup con opciones personalizadas
.\backup_postgres.ps1 -BackupDir "C:\mi\directorio\backup" -KeepDays 7 -Compress:$false
```

**Parámetros:**
- `-BackupDir`: Directorio donde guardar los backups (por defecto: `C:\backups\postgresql`)
- `-KeepDays`: Días a mantener los backups antiguos (por defecto: 30)
- `-Compress`: Comprimir los backups con 7-Zip (por defecto: `$true`)

### Backup Automático
La tarea programada `PostgreSQL_Backup_GMAO` se ejecuta automáticamente todos los días a las 2:00 AM.

**Para modificar la tarea programada:**
1. Abrir "Programador de tareas"
2. Buscar "PostgreSQL_Backup_GMAO"
3. Hacer clic derecho → "Propiedades"
4. Modificar triggers o acciones según necesites

## 🔄 Restauración de Backups

### Restauración Manual
```powershell
# Restauración con confirmación
.\restore_postgres.ps1 -BackupFile "C:\backups\postgresql\gmao_backup_20250928_020000.sql"

# Restauración forzada (sin confirmación)
.\restore_postgres.ps1 -BackupFile "C:\backups\postgresql\gmao_backup_20250928_020000.sql.7z" -Force

# Restauración a base de datos específica
.\restore_postgres.ps1 -BackupFile "C:\backups\postgresql\gmao_backup_20250928_020000.sql" -Database "gmao_produccion"
```

**Parámetros:**
- `-BackupFile`: **Obligatorio**. Ruta completa al archivo de backup
- `-Database`: Nombre de la base de datos (por defecto: `gmao_db`)
- `-Force`: Saltar confirmación de sobrescritura

### Proceso de Restauración
1. **Verificación**: Confirma que el archivo existe
2. **Descompresión**: Si es .7z, lo descomprime automáticamente
3. **Backup de seguridad**: Crea un backup del estado actual
4. **Restauración**: Sobrescribe la base de datos con el backup
5. **Verificación**: Confirma que la restauración fue exitosa

## 📁 Estructura de Backups

```
C:\backups\postgresql\
├── gmao_backup_20250928_020000.sql     # Backup sin comprimir
├── gmao_backup_20250928_020000.sql.7z  # Backup comprimido
├── backup_log.txt                       # Log de operaciones
├── restore_log.txt                      # Log de restauraciones
└── safety_backup_20250928_193000.sql    # Backup de seguridad (creado antes de restaurar)
```

## ⚙️ Configuración Avanzada

### Cambiar la frecuencia del backup automático
```powershell
# Eliminar tarea actual
Unregister-ScheduledTask -TaskName "PostgreSQL_Backup_GMAO" -Confirm:$false

# Crear nueva tarea (ejemplo: cada 6 horas)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"c:\gmao - copia\backup_postgres.ps1`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 1)
Register-ScheduledTask -TaskName "PostgreSQL_Backup_GMAO" -Action $action -Trigger $trigger
```

### Configurar compresión con 7-Zip
1. Instalar 7-Zip desde https://www.7-zip.org/
2. Asegurarse de que esté en `C:\Program Files\7-Zip\7z.exe`
3. El script detectará automáticamente y comprimirá los backups

## 🔍 Monitoreo y Logs

### Logs disponibles
- `backup_log.txt`: Registra todas las operaciones de backup
- `restore_log.txt`: Registra todas las operaciones de restauración

### Verificar estado de backups
```powershell
# Ver backups recientes
Get-ChildItem "C:\backups\postgresql" -Filter "gmao_backup_*.sql*" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime, Length

# Ver log de backups
Get-Content "C:\backups\postgresql\backup_log.txt" -Tail 20
```

## 🆘 Solución de Problemas

### Error: "pg_dump: [archiver] connection to database failed"
- Verificar que PostgreSQL esté ejecutándose
- Verificar credenciales en el script

### Error: "7-Zip no encontrado"
- Instalar 7-Zip o deshabilitar compresión: `.\backup_postgres.ps1 -Compress:$false`

### Error: "Access denied" en tarea programada
- Ejecutar PowerShell como administrador al crear la tarea
- Verificar permisos de escritura en el directorio de backup

### Restauración falla
- Verificar que el archivo de backup existe y no está corrupto
- Asegurarse de que PostgreSQL tenga permisos para crear la base de datos

## 📞 Soporte

Para problemas con el sistema de backup:
1. Revisar los logs en `C:\backups\postgresql\`
2. Verificar que PostgreSQL esté funcionando
3. Probar backup manual antes de verificar el automático

## 🔒 Seguridad

- Los backups contienen datos sensibles - almacenarlos en ubicación segura
- Considerar encriptación adicional para backups en producción
- Limitar acceso al directorio de backups
- No almacenar backups en la misma máquina que la base de datos en producción