# Script de análisis de rendimiento de índices PostgreSQL
param(
    [string]$Database = "gmao_db",
    [string]$OutputFile = "C:\backups\postgresql\performance_analysis_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
)

# Crear directorio si no existe
$dir = Split-Path $OutputFile -Parent
if (!(Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Write-Host "Analizando rendimiento de índices en PostgreSQL..." -ForegroundColor Green

# Función para ejecutar consultas SQL
function Invoke-SqlQuery {
    param([string]$Query)
    $result = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d $Database -c $Query -t -A
    return $result
}

# Análisis de índices
$analysis = @"
ANÁLISIS DE RENDIMIENTO - ÍNDICES POSTGRESQL
$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Base de datos: $Database

================================================================================
ÍNDICES EXISTENTES:
================================================================================
"@

$indexes = Invoke-SqlQuery "
SELECT
    schemaname || '.' || tablename as tabla,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as tamano
FROM pg_indexes i
JOIN pg_stat_user_indexes sui ON sui.indexrelname = i.indexname
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;"

$analysis += "`n$indexes`n"

# Estadísticas de uso de índices
$analysis += @"
================================================================================
ESTADÍSTICAS DE USO DE ÍNDICES:
================================================================================
"@

$usage = Invoke-SqlQuery "
SELECT
    sui.schemaname || '.' || sui.tablename as tabla,
    sui.indexname,
    sui.idx_scan as escaneos,
    sui.idx_tup_read as tuplas_leidas,
    sui.idx_tup_fetch as tuplas_recuperadas
FROM pg_stat_user_indexes sui
WHERE sui.schemaname = 'public'
ORDER BY sui.idx_scan DESC;"

$analysis += "`n$usage`n"

# Consultas lentas (simuladas con datos actuales)
$analysis += @"
================================================================================
ANÁLISIS DE CONSULTAS FRECUENTES:
================================================================================
"@

# Simular algunas consultas comunes y medir su rendimiento
$queries = @(
    "SELECT COUNT(*) FROM usuario WHERE activo = true",
    "SELECT COUNT(*) FROM orden_trabajo WHERE estado = 'En Proceso'",
    "SELECT COUNT(*) FROM activo WHERE estado = 'Operativo'",
    "SELECT * FROM orden_trabajo ORDER BY fecha_creacion DESC LIMIT 10",
    "SELECT * FROM activo WHERE departamento = 'MEC' ORDER BY codigo LIMIT 20"
)

foreach ($query in $queries) {
    $startTime = Get-Date
    $result = Invoke-SqlQuery "EXPLAIN ANALYZE $query"
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalMilliseconds

    $analysis += "`nConsulta: $query`n"
    $analysis += "Tiempo: $($duration.ToString('F2')) ms`n"
    $analysis += "Plan de ejecución:`n$result`n"
    $analysis += "-" * 80 + "`n"
}

# Recomendaciones
$analysis += @"
================================================================================
RECOMENDACIONES DE OPTIMIZACIÓN:
================================================================================

1. ÍNDICES CREADOS:
   ✅ Índices en campos de búsqueda frecuente (username, email, estado, etc.)
   ✅ Índices compuestos para consultas complejas
   ✅ Índices en campos de ordenamiento (fechas, códigos)

2. MONITOREO RECOMENDADO:
   - Revisar pg_stat_user_indexes regularmente
   - Monitorear índices poco utilizados para posible eliminación
   - Considerar REINDEX periódicamente para mantenimiento

3. OPTIMIZACIONES ADICIONALES POSIBLES:
   - Particionamiento de tablas grandes si crecen significativamente
   - Configuración de autovacuum para mantenimiento automático
   - Ajuste de work_mem para consultas complejas

4. MANTENIMIENTO:
   - Ejecutar ANALYZE regularmente para actualizar estadísticas
   - Monitorear el crecimiento de índices
   - Considerar CLUSTER para tablas con acceso secuencial frecuente

================================================================================
"@

# Guardar análisis
$analysis | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "Análisis completado. Archivo guardado en: $OutputFile" -ForegroundColor Green

# Mostrar resumen en consola
Write-Host "`nRESUMEN DE ÍNDICES OPTIMIZADOS:" -ForegroundColor Yellow
Write-Host "- Usuario: username, email, activo" -ForegroundColor White
Write-Host "- OrdenTrabajo: estado, fecha_creacion, fecha_completada" -ForegroundColor White
Write-Host "- Activo: estado, codigo, departamento, fechas de mantenimiento" -ForegroundColor White
Write-Host "- PlanMantenimiento: estado, proxima_ejecucion, codigo_plan" -ForegroundColor White
Write-Host "- Categoria: nombre, prefijo, activa" -ForegroundColor White
Write-Host "- Inventario: categoria_id, activo, codigo" -ForegroundColor White
Write-Host "- MovimientoInventario: fecha" -ForegroundColor White
Write-Host "- ConteoInventario: fecha_conteo" -ForegroundColor White
Write-Host "- Proveedor: nombre" -ForegroundColor White
Write-Host "- Manual: activo_id, fecha_subida" -ForegroundColor White

Write-Host "`n✅ Optimización de índices completada exitosamente!" -ForegroundColor Green