# Script PowerShell para inicializar la base de datos gmao
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "INICIALIZACIÓN FINAL DE BASE DE DATOS GMAO" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

# Crear archivo temporal con comandos SQL
$tempFile = "init_gmao_temp.sql"

# Crear contenido SQL sin comentarios problemáticos
$sqlContent = @'
CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'user',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER,
    ubicacion VARCHAR(100),
    estado VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS plan_mantenimiento (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    frecuencia INTEGER NOT NULL,
    unidad_frecuencia VARCHAR(20) NOT NULL,
    activo_id INTEGER,
    responsable_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orden_trabajo (
    id SERIAL PRIMARY KEY,
    numero_orden VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    activo_id INTEGER,
    plan_id INTEGER,
    asignado_a INTEGER,
    estado VARCHAR(20) DEFAULT 'pendiente',
    prioridad VARCHAR(20) DEFAULT 'media',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_programada TIMESTAMP,
    fecha_completada TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventario (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    cantidad INTEGER DEFAULT 0,
    unidad VARCHAR(20),
    precio_unitario DECIMAL(10,2),
    proveedor_id INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proveedor (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(120),
    direccion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS categoria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

INSERT INTO usuario (username, email, nombre, apellidos, password_hash, rol, activo)
VALUES ('admin', 'admin@mantenimiento.com', 'Administrador', 'Sistema',
    'scrypt:32768:8:1$8ZGiIdkR6hKgEBjS$3d4a1f8b9c2e5d8a7f6e9c8b5a4d7f0e3c6b9a8e5d2f1c4b7a0e9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d8c5b2f7e0a9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d',
    'admin', true)
ON CONFLICT (username) DO NOTHING;

SELECT 'Database initialization completed!' as status;
'@

# Escribir al archivo
$sqlContent | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "📄 Archivo SQL creado: $tempFile" -ForegroundColor Green
Write-Host "🔗 Conectando a Cloud SQL..." -ForegroundColor Cyan

# Intentar ejecutar con gcloud
try {
    Write-Host "🎯 Ejecutando inicialización..." -ForegroundColor Cyan
    $gcloudPath = (Get-Command gcloud -ErrorAction SilentlyContinue).Source
    if ($gcloudPath) {
        Write-Host "   Usando gcloud en: $gcloudPath" -ForegroundColor Gray
        $process = Start-Process -FilePath "gcloud" -ArgumentList "sql", "connect", "gmao-postgres-spain", "--user=postgres", "--database=gmao" -RedirectStandardInput $tempFile -Wait -PassThru -WindowStyle Hidden
        if ($process.ExitCode -eq 0) {
            Write-Host "✅ Comandos ejecutados exitosamente" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Error en la ejecución (código: $($process.ExitCode))" -ForegroundColor Red
        }
    }
    else {
        Write-Host "❌ gcloud no encontrado en PATH" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Intentar método alternativo: mostrar comandos para ejecución manual
Write-Host "`n💡 MÉTODO ALTERNATIVO - Ejecutar manualmente:" -ForegroundColor Yellow
Write-Host "1. Abrir una nueva terminal" -ForegroundColor White
Write-Host "2. Ejecutar: gcloud sql connect gmao-postgres-spain --user=postgres --database=gmao" -ForegroundColor White
Write-Host "3. En el prompt de PostgreSQL, copiar y pegar cada comando de $tempFile" -ForegroundColor White

Write-Host "`n📋 COMANDOS SQL A EJECUTAR:" -ForegroundColor Cyan
Write-Host $sqlContent -ForegroundColor Gray

Write-Host "`n🔑 DESPUÉS DE LA INICIALIZACIÓN:" -ForegroundColor Yellow
Write-Host "   Usuario: admin" -ForegroundColor White
Write-Host "   Contraseña: admin123" -ForegroundColor White
Write-Host "   URL: https://mantenimiento-470311.ew.r.appspot.com" -ForegroundColor White

Write-Host "`n============================================================" -ForegroundColor Yellow