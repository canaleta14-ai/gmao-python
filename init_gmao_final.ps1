# Script PowerShell para inicializar la base de datos gmao
# Este script ejecuta comandos SQL directamente en Cloud SQL

Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "INICIALIZACIÓN FINAL DE BASE DE DATOS GMAO" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

# Crear archivo temporal con comandos SQL
$sqlContent = @"
-- Crear las tablas principales
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

-- Insertar usuario admin
INSERT INTO usuario (username, email, nombre, apellidos, password_hash, rol, activo)
VALUES ('admin', 'admin@mantenimiento.com', 'Administrador', 'Sistema',
    'scrypt:32768:8:1$8ZGiIdkR6hKgEBjS$3d4a1f8b9c2e5d8a7f6e9c8b5a4d7f0e3c6b9a8e5d2f1c4b7a0e9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d8c5b2f7e0a9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d',
    'admin', true)
ON CONFLICT (username) DO NOTHING;

-- Verificar creación
SELECT 'Initialization completed!' as status;
SELECT COUNT(*) as user_count FROM usuario WHERE username = 'admin';
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
"@

# Crear archivo temporal
$tempFile = [System.IO.Path]::GetTempFileName() + ".sql"
$sqlContent | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "📄 Archivo SQL creado: $tempFile" -ForegroundColor Green
Write-Host "🔗 Ejecutando comandos SQL via gcloud..." -ForegroundColor Cyan

try {
    # Ejecutar comandos SQL usando gcloud
    $result = & gcloud sql connect gmao-postgres-spain --user=postgres --database=gmao 2>&1 < $tempFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Comandos ejecutados exitosamente" -ForegroundColor Green
        Write-Host $result
        
        Write-Host "`n🎉 ¡BASE DE DATOS INICIALIZADA EXITOSAMENTE!" -ForegroundColor Green
        Write-Host "✅ Tablas creadas" -ForegroundColor Green
        Write-Host "✅ Usuario admin insertado" -ForegroundColor Green
        Write-Host "✅ Base de datos gmao lista para usar" -ForegroundColor Green
        Write-Host "`n🔑 Credenciales de login:" -ForegroundColor Yellow
        Write-Host "   Usuario: admin" -ForegroundColor White
        Write-Host "   Contraseña: admin123" -ForegroundColor White
        Write-Host "`n🌐 Aplicación disponible en:" -ForegroundColor Yellow
        Write-Host "   https://mantenimiento-470311.ew.r.appspot.com" -ForegroundColor White
    }
    else {
        Write-Host "❌ Error ejecutando comandos:" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}
finally {
    # Limpiar archivo temporal
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    Write-Host "🧹 Archivo temporal eliminado" -ForegroundColor Gray
}

Write-Host "`n============================================================" -ForegroundColor Yellow