# 🚀 COMANDOS PASO 5 - Migración de Base de Datos
# Ejecutar estos comandos después del Paso 4

# ====================================
# 1. Descargar Cloud SQL Proxy
# ====================================

Write-Host "📥 Descargando Cloud SQL Proxy..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "https://dl.google.com/cloudsql/cloud_sql_proxy_x64.exe" -OutFile "cloud_sql_proxy.exe"
Write-Host "✅ Cloud SQL Proxy descargado" -ForegroundColor Green

# ====================================
# 2. Crear base de datos y usuario
# ====================================

Write-Host "🗄️ Creando base de datos 'gmao'..." -ForegroundColor Cyan
gcloud sql databases create gmao --instance=gmao-postgres

Write-Host "👤 Creando usuario 'gmao-user'..." -ForegroundColor Cyan
gcloud sql users create gmao-user `
  --instance=gmao-postgres `
  --password="NbQt4EB*3gYjhu*25wemy73yr#IBXKm!"

Write-Host "✅ Base de datos y usuario creados" -ForegroundColor Green

# ====================================
# 3. Instrucciones para ejecutar proxy
# ====================================

Write-Host ""
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "SIGUIENTE PASO - Ejecutar Cloud SQL Proxy" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Abre una NUEVA ventana de PowerShell y ejecuta:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  cd 'C:\gmao - copia'" -ForegroundColor White
Write-Host "  .\cloud_sql_proxy.exe -instances=gmao-sistema-2025:europe-west1:gmao-postgres=tcp:5432" -ForegroundColor White
Write-Host ""
Write-Host "Deja esa ventana abierta y vuelve aquí." -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Enter cuando el proxy esté corriendo..." -ForegroundColor Yellow
Read-Host

# ====================================
# 4. Configurar DATABASE_URL y migrar
# ====================================

Write-Host "🔄 Configurando DATABASE_URL..." -ForegroundColor Cyan
$env:DATABASE_URL = "postgresql://gmao-user:NbQt4EB*3gYjhu*25wemy73yr#IBXKm!@localhost:5432/gmao"

Write-Host "📊 Ejecutando migraciones..." -ForegroundColor Cyan
flask db upgrade

Write-Host "✅ Migraciones completadas" -ForegroundColor Green

# ====================================
# 5. Crear usuario administrador
# ====================================

Write-Host "👨‍💼 Creando usuario administrador..." -ForegroundColor Cyan

python -c @"
from app.factory import create_app
from app.models.usuario import Usuario
from app.extensions import db

app = create_app()
with app.app_context():
    # Verificar si ya existe
    admin_existe = Usuario.query.filter_by(username='admin').first()
    if admin_existe:
        print('✓ Usuario admin ya existe')
    else:
        admin = Usuario(
            username='admin',
            email='admin@gmao.com',
            nombre='Administrador del Sistema',
            rol='Administrador'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✓ Usuario admin creado')
        print('  Username: admin')
        print('  Password: admin123')
        print('  ⚠️ CAMBIAR PASSWORD EN PRODUCCIÓN')
"@

Write-Host ""
Write-Host "✅ Base de datos migrada y lista!" -ForegroundColor Green
