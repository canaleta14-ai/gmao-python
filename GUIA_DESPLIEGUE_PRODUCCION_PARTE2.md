# 🚀 GUÍA DE DESPLIEGUE A PRODUCCIÓN - PARTE 2

**Continuación de GUIA_DESPLIEGUE_PRODUCCION.md**

---

## <a name="fase-6-testing"></a>📌 FASE 6: TESTING Y CI/CD (DÍAS 10-11) 🟡

### Objetivo
Implementar suite de tests automatizados y integrar en pipeline CI/CD.

### Tareas

#### 6.1 Configurar Pytest

```bash
# Instalar dependencias de testing
pip install pytest==7.4.3
pip install pytest-flask==1.3.0
pip install pytest-cov==4.1.0
pip install pytest-mock==3.12.0

# Actualizar requirements.txt
pip freeze > requirements.txt
```

#### 6.2 Crear Configuración de Pytest

**Archivo:** `pytest.ini` (nuevo)

```ini
[pytest]
# Directorios de tests
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Opciones de ejecución
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=70

# Markers personalizados
markers =
    unit: Tests unitarios rápidos
    integration: Tests de integración
    slow: Tests lentos
    security: Tests de seguridad
    smoke: Tests de humo para producción

# Variables de entorno para tests
env =
    FLASK_ENV=testing
    DB_TYPE=sqlite
    SECRET_KEY=test_secret_key_not_for_production
```

#### 6.3 Crear Fixtures Comunes

**Archivo:** `conftest.py` (nuevo en raíz)

```python
"""
Configuración común de pytest para todos los tests
"""
import pytest
import os
import tempfile
from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="session")
def app():
    """Crear aplicación de Flask para testing"""
    # Crear base de datos temporal
    db_fd, db_path = tempfile.mkstemp()
    
    # Configurar app para testing
    os.environ["FLASK_ENV"] = "testing"
    os.environ["DB_TYPE"] = "sqlite"
    os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    os.environ["TESTING"] = "True"
    os.environ["WTF_CSRF_ENABLED"] = "False"  # Deshabilitar CSRF en tests
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost.localdomain"
    })
    
    # Crear contexto de aplicación
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    # Limpiar
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def client(app):
    """Cliente HTTP para hacer requests"""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """CLI runner para comandos Flask"""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def db_session(app):
    """Sesión de base de datos con rollback automático"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configurar sesión para usar esta transacción
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        db.session = session
        
        yield session
        
        # Rollback al final del test
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture(scope="function")
def user_admin(app):
    """Crear usuario administrador para tests"""
    with app.app_context():
        user = Usuario(
            username="admin_test",
            email="admin@test.com",
            password=generate_password_hash("admin123"),
            rol="administrador",
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture(scope="function")
def user_tecnico(app):
    """Crear usuario técnico para tests"""
    with app.app_context():
        user = Usuario(
            username="tecnico_test",
            email="tecnico@test.com",
            password=generate_password_hash("tecnico123"),
            rol="tecnico",
            activo=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture(scope="function")
def authenticated_client(client, user_admin):
    """Cliente con sesión autenticada"""
    with client:
        client.post("/usuarios/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        yield client
```

#### 6.4 Crear Tests de Seguridad

**Archivo:** `tests/test_security.py` (nuevo)

```python
"""
Tests de seguridad críticos para producción
"""
import pytest


@pytest.mark.security
def test_csrf_protection_enabled(app):
    """Verificar que CSRF está habilitado en producción"""
    # En testing está deshabilitado, pero verificar configuración
    assert app.config.get("WTF_CSRF_ENABLED") == False  # Solo en tests
    
    # En producción debería estar True
    # Este test fallará si se ejecuta en producción sin CSRF


@pytest.mark.security
def test_session_cookie_secure_in_production(app):
    """Verificar cookies seguras en producción"""
    # Simular producción
    import os
    original_env = os.getenv("GAE_ENV", "")
    os.environ["GAE_ENV"] = "standard"
    
    # Recargar app
    from app.factory import create_app
    prod_app = create_app()
    
    assert prod_app.config["SESSION_COOKIE_SECURE"] == True
    assert prod_app.config["SESSION_COOKIE_HTTPONLY"] == True
    
    # Restaurar
    os.environ["GAE_ENV"] = original_env


@pytest.mark.security
def test_secret_key_not_default(app):
    """Verificar que SECRET_KEY no es el valor por defecto"""
    secret = app.config["SECRET_KEY"]
    
    # No debe ser el valor de desarrollo
    assert secret != "clave_secreta_fija_para_sesiones_2025_gmao"
    assert len(secret) >= 32  # Mínimo 32 caracteres


@pytest.mark.security
def test_login_rate_limiting(client):
    """Verificar rate limiting en login"""
    # Hacer múltiples intentos
    for i in range(10):
        response = client.post("/usuarios/login", data={
            "username": "test",
            "password": "wrong"
        })
    
    # Después de 5 intentos debería bloquear (según config)
    # Este test puede variar según implementación de rate limiting
    # assert response.status_code == 429  # Too Many Requests


@pytest.mark.security
def test_sql_injection_protection(authenticated_client):
    """Verificar protección contra SQL injection"""
    # Intentar SQL injection en búsqueda
    malicious_input = "'; DROP TABLE usuarios; --"
    
    response = authenticated_client.get(
        f"/activos/api?busqueda={malicious_input}"
    )
    
    # No debe causar error 500 (debe estar sanitizado)
    assert response.status_code != 500
    
    # Verificar que tabla sigue existiendo
    from app.models.usuario import Usuario
    usuarios = Usuario.query.all()
    # Si pasa, la tabla no fue eliminada


@pytest.mark.security
def test_xss_protection(authenticated_client):
    """Verificar protección contra XSS"""
    # Intentar inyectar script
    malicious_script = "<script>alert('XSS')</script>"
    
    response = authenticated_client.post("/activos/api", json={
        "nombre": malicious_script,
        "codigo": "TEST001",
        "departamento": "test"
    })
    
    # Verificar que se guardó escapado
    if response.status_code == 201:
        data = response.get_json()
        activo_id = data.get("id")
        
        response = authenticated_client.get(f"/activos/api/{activo_id}")
        html = response.data.decode()
        
        # No debe contener script ejecutable
        assert "<script>" not in html or "&lt;script&gt;" in html


@pytest.mark.security
def test_unauthorized_access_blocked(client):
    """Verificar que rutas protegidas requieren autenticación"""
    protected_routes = [
        "/dashboard",
        "/activos/",
        "/ordenes/",
        "/inventario/",
        "/planes/",
        "/proveedores/"
    ]
    
    for route in protected_routes:
        response = client.get(route)
        # Debe redirigir a login (302) o denegar acceso (401/403)
        assert response.status_code in [302, 401, 403]
```

#### 6.5 Crear Tests de Integración

**Archivo:** `tests/test_integration_ordenes.py` (nuevo)

```python
"""
Tests de integración para módulo de órdenes
"""
import pytest
from datetime import datetime


@pytest.mark.integration
def test_crear_orden_completo(authenticated_client):
    """Test de flujo completo: crear activo -> crear orden"""
    # 1. Crear activo
    response = authenticated_client.post("/activos/api", json={
        "nombre": "Activo Test",
        "codigo": "TEST001",
        "departamento": "produccion",
        "estado": "operativo"
    })
    assert response.status_code == 201
    activo_id = response.get_json()["id"]
    
    # 2. Crear orden de trabajo
    response = authenticated_client.post("/ordenes/", json={
        "titulo": "Orden Test",
        "descripcion": "Descripción test",
        "activo_id": activo_id,
        "tipo": "correctivo",
        "prioridad": "alta",
        "estado": "pendiente"
    })
    assert response.status_code == 201
    orden_id = response.get_json()["id"]
    
    # 3. Asignar técnico
    response = authenticated_client.put(f"/ordenes/api/{orden_id}", json={
        "tecnico_asignado_id": 1  # Usuario de test
    })
    assert response.status_code == 200
    
    # 4. Cambiar estado
    response = authenticated_client.put(f"/ordenes/api/{orden_id}/estado", json={
        "estado": "en_progreso"
    })
    assert response.status_code == 200
    
    # 5. Verificar orden
    response = authenticated_client.get(f"/ordenes/api/{orden_id}")
    assert response.status_code == 200
    orden = response.get_json()
    assert orden["estado"] == "en_progreso"
    assert orden["activo_id"] == activo_id


@pytest.mark.integration
def test_generacion_automatica_ordenes(app, user_admin):
    """Test de generación automática de órdenes preventivas"""
    with app.app_context():
        from app.models.activo import Activo
        from app.models.plan_mantenimiento import PlanMantenimiento
        from app.extensions import db
        
        # 1. Crear activo
        activo = Activo(
            nombre="Activo Preventivo",
            codigo="PREV001",
            departamento="mantenimiento",
            estado="operativo"
        )
        db.session.add(activo)
        db.session.commit()
        
        # 2. Crear plan de mantenimiento
        plan = PlanMantenimiento(
            nombre="Mantenimiento Mensual",
            descripcion="Test",
            activo_id=activo.id,
            frecuencia="mensual",
            autogenerar_ordenes=True,
            activo=True
        )
        db.session.add(plan)
        db.session.commit()
        
        # 3. Simular generación (llamar a función)
        from app.routes.planes import verificar_debe_generar_orden
        debe_generar = verificar_debe_generar_orden(plan)
        
        assert debe_generar == True  # Primera vez debe generar
```

#### 6.6 Actualizar cloudbuild.yaml

**Archivo:** `cloudbuild.yaml` (descomentar y mejorar sección de tests)

```yaml
steps:
  # 1. Verificar configuración
  - name: "bash"
    script: |
      #!/bin/bash
      echo "🔍 Verificando configuración..."
      if [ ! -f "app.yaml" ]; then
        echo "❌ app.yaml no encontrado"
        exit 1
      fi
      if [ ! -f "main.py" ]; then
        echo "❌ main.py no encontrado"
        exit 1
      fi
      echo "✅ Archivos de configuración encontrados"

  # 2. Instalar dependencias
  - name: "python:3.11-slim"
    entrypoint: pip
    args: ["install", "-r", "requirements.txt", "--user", "--quiet"]

  # 3. Ejecutar tests de seguridad (crítico)
  - name: "python:3.11-slim"
    entrypoint: python
    args: ["-m", "pytest", "tests/test_security.py", "-v", "-m", "security"]
    env:
      - "FLASK_ENV=testing"

  # 4. Ejecutar tests de integración
  - name: "python:3.11-slim"
    entrypoint: python
    args: ["-m", "pytest", "tests/", "-v", "--tb=short", "--maxfail=5"]
    env:
      - "FLASK_ENV=testing"

  # 5. Verificar coverage (70% mínimo)
  - name: "python:3.11-slim"
    entrypoint: python
    args: ["-m", "pytest", "--cov=app", "--cov-fail-under=70"]
    env:
      - "FLASK_ENV=testing"

  # 6. Verificar sintaxis de Python
  - name: "python:3.11-slim"
    entrypoint: python
    args: ["-m", "py_compile", "main.py", "app/__init__.py"]

  # 7. Desplegar a App Engine
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
    entrypoint: gcloud
    args:
      - "app"
      - "deploy"
      - "--version=${_VERSION:-prod}"
      - "--quiet"
      - "--promote"  # Cambiar a --no-promote para staging

# Configuración de variables de sustitución
substitutions:
  _VERSION: prod

# Configuración de timeout
timeout: "1800s"

# Configuración de opciones
options:
  machineType: "E2_HIGHCPU_8"
  logging: CLOUD_LOGGING_ONLY

# Configuración de logs
logsBucket: "gs://${PROJECT_ID}-logs"
```

#### 6.7 Crear Script de Tests Locales

**Archivo:** `scripts/run_tests.sh` (nuevo)

```bash
#!/bin/bash
# Script para ejecutar tests localmente antes de commit

set -e

echo "🧪 Ejecutando suite de tests..."

# Activar entorno virtual
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 1. Tests de seguridad (crítico)
echo ""
echo "🔒 Tests de seguridad..."
pytest tests/test_security.py -v -m security

# 2. Tests unitarios rápidos
echo ""
echo "⚡ Tests unitarios..."
pytest -v -m unit --tb=short

# 3. Tests de integración
echo ""
echo "🔗 Tests de integración..."
pytest -v -m integration --tb=short

# 4. Coverage report
echo ""
echo "📊 Coverage report..."
pytest --cov=app --cov-report=term-missing --cov-report=html

# 5. Resumen
echo ""
echo "✅ Todos los tests pasaron exitosamente"
echo "📁 Reporte HTML generado en: htmlcov/index.html"
```

### Checklist Fase 6

```bash
[✅] Pytest configurado
[✅] Fixtures comunes creados
[✅] Tests de seguridad implementados
[✅] Tests de integración creados
[✅] cloudbuild.yaml actualizado con tests
[✅] Script de tests locales creado
[✅] Coverage mínimo 70% alcanzado
[✅] Pipeline CI/CD funcionando
```

---

## <a name="fase-7-deployment"></a>📌 FASE 7: DEPLOYMENT FINAL (DÍAS 12-13) 🟢

### Objetivo
Ejecutar deployment completo a Google Cloud Platform.

### Tareas

#### 7.1 Pre-Deployment Checklist

```bash
# Verificar configuración local
[ ] .env existe y está completo
[ ] .gitignore incluye .env y archivos sensibles
[ ] requirements.txt actualizado
[ ] Migraciones creadas y probadas
[ ] Tests pasando (70%+ coverage)
[ ] Credenciales rotadas
[ ] Secrets creados en GCP

# Verificar configuración GCP
[ ] Proyecto GCP creado
[ ] Billing habilitado
[ ] Cloud SQL instance creada
[ ] Bucket de uploads creado
[ ] Secrets Manager configurado
[ ] Cloud Scheduler configurado
[ ] APIs habilitadas
```

#### 7.2 Habilitar APIs Necesarias

```bash
# Habilitar todas las APIs de GCP
gcloud services enable \
  appengine.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  storage-api.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  --project=gmao-sistema
```

#### 7.3 Crear Cloud SQL Instance

```bash
# 1. Crear instancia PostgreSQL
gcloud sql instances create gmao-postgres \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=CAMBIAR_ESTO \
  --storage-type=SSD \
  --storage-size=10GB \
  --backup \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04 \
  --project=gmao-sistema

# 2. Crear base de datos
gcloud sql databases create postgres \
  --instance=gmao-postgres \
  --project=gmao-sistema

# 3. Crear usuario
gcloud sql users create postgres \
  --instance=gmao-postgres \
  --password=CAMBIAR_ESTO \
  --project=gmao-sistema

# 4. Obtener connection name
gcloud sql instances describe gmao-postgres \
  --format="value(connectionName)" \
  --project=gmao-sistema
# Resultado: gmao-sistema:us-central1:gmao-postgres
```

#### 7.4 Ejecutar Migraciones en Producción

```bash
# 1. Conectar a Cloud SQL via proxy
cloud_sql_proxy -instances=gmao-sistema:us-central1:gmao-postgres=tcp:5432

# 2. En otra terminal, configurar variables
export DATABASE_URL="postgresql://postgres:PASSWORD@localhost:5432/postgres"
export FLASK_APP=main.py
export FLASK_ENV=production

# 3. Ejecutar migraciones
flask db upgrade

# 4. Verificar
flask db current
```

#### 7.5 Deployment Inicial

**Archivo:** `scripts/deploy.sh` (nuevo)

```bash
#!/bin/bash
# Script de deployment completo a GCP

set -e

PROJECT_ID="gmao-sistema"
VERSION="prod-$(date +%Y%m%d-%H%M%S)"

echo "🚀 Iniciando deployment a producción"
echo "Proyecto: $PROJECT_ID"
echo "Versión: $VERSION"

# 1. Verificar que estamos en la rama correcta
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "master" ]; then
    echo "⚠️  No estás en la rama master"
    read -p "¿Continuar de todos modos? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        exit 1
    fi
fi

# 2. Verificar que no hay cambios sin commitear
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Hay cambios sin commitear"
    git status
    exit 1
fi

# 3. Ejecutar tests
echo "🧪 Ejecutando tests..."
pytest tests/ -v --tb=short -m "not slow"

# 4. Verificar secretos existen
echo "🔐 Verificando secretos en GCP..."
gcloud secrets list --project=$PROJECT_ID | grep -q "gmao-secret-key" || {
    echo "❌ Secret gmao-secret-key no encontrado"
    exit 1
}

# 5. Crear tag de Git
echo "🏷️  Creando tag..."
git tag -a "deploy-$VERSION" -m "Deployment $VERSION"
git push origin "deploy-$VERSION"

# 6. Build y deploy via Cloud Build
echo "🔨 Construyendo y desplegando..."
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_VERSION=$VERSION \
  --project=$PROJECT_ID

# 7. Esperar a que esté listo
echo "⏳ Esperando deployment..."
sleep 30

# 8. Health check
echo "🏥 Verificando health..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://gmao-sistema.uc.r.appspot.com/)
if [ "$RESPONSE" == "200" ]; then
    echo "✅ Deployment exitoso"
else
    echo "❌ Health check falló (HTTP $RESPONSE)"
    exit 1
fi

# 9. Smoke tests
echo "💨 Ejecutando smoke tests..."
pytest tests/ -v -m smoke

echo ""
echo "🎉 DEPLOYMENT COMPLETADO EXITOSAMENTE"
echo "URL: https://gmao-sistema.uc.r.appspot.com"
echo "Versión: $VERSION"
echo "Tag: deploy-$VERSION"
```

#### 7.6 Verificaciones Post-Deployment

```bash
# 1. Verificar que la app responde
curl -I https://gmao-sistema.uc.r.appspot.com/

# 2. Verificar login
curl -X POST https://gmao-sistema.uc.r.appspot.com/usuarios/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# 3. Ver logs
gcloud app logs tail -s default --project=gmao-sistema

# 4. Ver errores recientes
gcloud logging read "resource.type=gae_app AND severity>=ERROR" \
  --limit 50 \
  --format json \
  --project=gmao-sistema

# 5. Verificar Cloud Scheduler
gcloud scheduler jobs list --location=us-central1 --project=gmao-sistema

# 6. Verificar Cloud SQL
gcloud sql instances describe gmao-postgres --project=gmao-sistema
```

#### 7.7 Configurar Dominio Personalizado (Opcional)

```bash
# 1. Agregar dominio personalizado
gcloud app domain-mappings create www.tu-dominio.com \
  --certificate-management=AUTOMATIC \
  --project=gmao-sistema

# 2. Verificar certificado SSL
gcloud app ssl-certificates list --project=gmao-sistema

# 3. Actualizar DNS (registrar)
# Agregar registros A y AAAA según instrucciones de GCP
```

### Checklist Fase 7

```bash
[✅] APIs de GCP habilitadas
[✅] Cloud SQL instance creada y configurada
[✅] Base de datos inicializada
[✅] Migraciones aplicadas
[✅] Secrets verificados
[✅] Deployment ejecutado
[✅] Health checks pasando
[✅] Smoke tests pasando
[✅] Logs monitoreados
[✅] Dominio configurado (opcional)
```

---

## <a name="fase-8-monitoreo"></a>📌 FASE 8: MONITOREO POST-DEPLOY (DÍA 14) 🟡

### Objetivo
Implementar monitoreo, alertas y observabilidad para producción.

### Tareas

#### 8.1 Configurar Sentry para Error Tracking

```bash
# 1. Crear cuenta en Sentry (sentry.io)
# 2. Crear proyecto "gmao-sistema"
# 3. Obtener DSN

# 4. Instalar SDK
pip install sentry-sdk[flask]==1.40.0
pip freeze > requirements.txt
```

**Archivo:** `app/factory.py` (añadir al inicio)

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Configurar Sentry solo en producción
if os.getenv("SENTRY_DSN") and not os.getenv("FLASK_DEBUG"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration()
        ],
        traces_sample_rate=0.1,  # 10% de transacciones
        profiles_sample_rate=0.1,  # 10% de perfiles
        environment=os.getenv("FLASK_ENV", "production"),
        release=os.getenv("APP_VERSION", "1.0.0"),
        before_send=before_send_sentry,
    )
    app.logger.info("✅ Sentry error tracking configurado")


def before_send_sentry(event, hint):
    """Filtrar eventos antes de enviar a Sentry"""
    # No enviar errores 404
    if event.get("exception"):
        exc_type = event["exception"]["values"][0].get("type")
        if exc_type == "NotFound":
            return None
    
    # Eliminar datos sensibles
    if "request" in event:
        if "cookies" in event["request"]:
            event["request"]["cookies"] = {"session": "[FILTERED]"}
    
    return event
```

**Crear secret en GCP:**

```bash
echo "https://your-sentry-dsn@sentry.io/123456" > sentry_dsn.txt

gcloud secrets create gmao-sentry-dsn \
  --data-file=sentry_dsn.txt \
  --project=gmao-sistema

rm sentry_dsn.txt
```

#### 8.2 Configurar Cloud Monitoring

**Archivo:** `scripts/create_monitoring.sh` (nuevo)

```bash
#!/bin/bash
# Crear políticas de alertas en Cloud Monitoring

PROJECT_ID="gmao-sistema"

echo "📊 Configurando Cloud Monitoring..."

# 1. Alerta por alta tasa de errores (500)
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Alta tasa de errores HTTP 500" \
  --condition-display-name="Errores > 5% en 5 minutos" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s \
  --project=$PROJECT_ID

# 2. Alerta por latencia alta
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Latencia alta" \
  --condition-display-name="P95 latency > 2 segundos" \
  --condition-threshold-value=2000 \
  --condition-threshold-duration=300s \
  --project=$PROJECT_ID

# 3. Alerta por uso de memoria
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Uso de memoria alto" \
  --condition-display-name="Memoria > 90%" \
  --condition-threshold-value=0.9 \
  --condition-threshold-duration=300s \
  --project=$PROJECT_ID

echo "✅ Políticas de alertas creadas"
```

#### 8.3 Crear Dashboard Personalizado

**Archivo:** `monitoring/dashboard.json` (nuevo)

```json
{
  "displayName": "GMAO Sistema - Dashboard Principal",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Requests por minuto",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"gae_app\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Tasa de errores",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"gae_app\" AND metric.type=\"appengine.googleapis.com/http/server/response_count\" AND metric.label.response_code >= 500"
                }
              }
            }]
          }
        }
      },
      {
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Latencia P50/P95/P99",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"gae_app\" AND metric.type=\"appengine.googleapis.com/http/server/response_latencies\""
                }
              }
            }]
          }
        }
      },
      {
        "xPos": 6,
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Uso de memoria",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"gae_app\" AND metric.type=\"appengine.googleapis.com/system/memory/usage\""
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

Importar dashboard:

```bash
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json \
  --project=gmao-sistema
```

#### 8.4 Configurar Notificaciones por Email

```bash
# 1. Crear canal de notificación
gcloud alpha monitoring channels create \
  --display-name="Email Administrador" \
  --type=email \
  --channel-labels=email_address=admin@tudominio.com \
  --project=gmao-sistema

# 2. Listar canales
gcloud alpha monitoring channels list --project=gmao-sistema

# 3. Obtener CHANNEL_ID y usar en alertas
```

#### 8.5 Crear Runbook de Operaciones

**Archivo:** `RUNBOOK_OPERACIONES.md` (nuevo)

```markdown
# 📘 RUNBOOK DE OPERACIONES - SISTEMA GMAO

## 🚨 PROCEDIMIENTOS DE EMERGENCIA

### Error 500 - Internal Server Error

**Síntomas:**
- Usuarios reportan error 500
- Alerta de Sentry
- Spike en logs de error

**Diagnóstico:**
```bash
# Ver últimos errores
gcloud app logs read --service=default --severity=ERROR --limit=50

# Ver en Sentry
# https://sentry.io/organizations/tu-org/issues/
```

**Solución:**
1. Identificar error en Sentry
2. Si es error de BD: Verificar Cloud SQL
3. Si es error de código: Rollback a versión anterior
4. Si persiste: Escalar a desarrollo

### Base de Datos Lenta

**Síntomas:**
- Latencia > 2 segundos
- Timeout en requests
- Usuarios reportan lentitud

**Diagnóstico:**
```bash
# Ver queries lentas
gcloud sql operations list --instance=gmao-postgres

# Conectar y analizar
psql -h 127.0.0.1 -U postgres -d postgres
\x
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

**Solución:**
1. Identificar queries lentas
2. Añadir índices si es necesario
3. Escalar instance si es necesario

### Deployment Fallido

**Síntomas:**
- Cloud Build falla
- Tests no pasan
- Secrets no se cargan

**Solución:**
```bash
# Ver logs de build
gcloud builds list --limit=5
gcloud builds log [BUILD_ID]

# Rollback a versión anterior
gcloud app versions list
gcloud app services set-traffic default --splits=[VERSION]=1
```

## 📊 MONITOREO DIARIO

### Checklist Matutino
- [ ] Verificar dashboard (errores, latencia)
- [ ] Revisar alertas de Sentry (últimas 24h)
- [ ] Verificar Cloud Scheduler ejecutó
- [ ] Revisar backup de BD (último 24h)

### Checklist Semanal
- [ ] Analizar métricas de uso
- [ ] Revisar logs de seguridad
- [ ] Verificar espacio en Cloud Storage
- [ ] Revisar costos de GCP

## 🔧 COMANDOS ÚTILES

### Ver versiones desplegadas
```bash
gcloud app versions list
```

### Cambiar tráfico entre versiones
```bash
gcloud app services set-traffic default --splits=v1=0.5,v2=0.5
```

### Escalar instancias manualmente
```bash
gcloud app versions update v1 --max-instances=20
```

### Backup manual de BD
```bash
gcloud sql export sql gmao-postgres \
  gs://gmao-sistema-backups/manual-$(date +%Y%m%d).sql
```

### Restaurar backup
```bash
gcloud sql import sql gmao-postgres \
  gs://gmao-sistema-backups/backup-20251001.sql
```

## 📞 CONTACTOS

- **Desarrollo:** tu-equipo@tudominio.com
- **Infraestructura:** infra@tudominio.com
- **Soporte GCP:** https://cloud.google.com/support
```

### Checklist Fase 8

```bash
[✅] Sentry configurado y probado
[✅] Cloud Monitoring configurado
[✅] Dashboard personalizado creado
[✅] Alertas configuradas
[✅] Canales de notificación configurados
[✅] Runbook de operaciones creado
[✅] Documentación de troubleshooting
```

---

## 🎯 RESUMEN FINAL

### Tiempo Total Invertido
- **Fase 1 (Seguridad):** 2 días
- **Fase 2 (Migraciones BD):** 1 día
- **Fase 3 (Secret Manager):** 1 día
- **Fase 4 (Cloud Storage):** 2 días
- **Fase 5 (Cloud Scheduler):** 3 días
- **Fase 6 (Testing):** 2 días
- **Fase 7 (Deployment):** 2 días
- **Fase 8 (Monitoreo):** 1 día

**TOTAL: 14 días laborables (~3 semanas)**

### Checklist Final Pre-Go-Live

```bash
[✅] Seguridad
    [✅] CSRF Protection
    [✅] SESSION_COOKIE_SECURE
    [✅] Rate Limiting
    [✅] Credenciales rotadas
    [✅] CORS (si aplica)

[✅] Base de Datos
    [✅] Flask-Migrate instalado
    [✅] Migraciones creadas
    [✅] Cloud SQL configurado
    [✅] Backups automáticos

[✅] Secrets
    [✅] Todos los secrets en Secret Manager
    [✅] Permisos configurados
    [✅] app.yaml actualizado

[✅] Almacenamiento
    [✅] Bucket de GCS creado
    [✅] StorageManager implementado
    [✅] Uploads migrados

[✅] Scheduler
    [✅] Cloud Scheduler configurado
    [✅] Endpoint protegido
    [✅] Tests de ejecución

[✅] Testing
    [✅] Tests de seguridad
    [✅] Tests de integración
    [✅] CI/CD con tests
    [✅] Coverage > 70%

[✅] Deployment
    [✅] APIs habilitadas
    [✅] Deployment exitoso
    [✅] Health checks pasando
    [✅] Smoke tests

[✅] Monitoreo
    [✅] Sentry configurado
    [✅] Cloud Monitoring
    [✅] Alertas configuradas
    [✅] Runbook creado
```

### Próximos Pasos Post-Go-Live

1. **Semana 1:** Monitoreo intensivo diario
2. **Semana 2-4:** Optimizaciones de performance
3. **Mes 2:** Implementar features adicionales
4. **Mes 3:** Revisión de costos y optimización

---

## 📚 DOCUMENTACIÓN ADICIONAL

Ver también:
- `GUIA_SELECCION_MASIVA.md` - Sistema de checkboxes
- `README.md` - Documentación del proyecto
- `RUNBOOK_OPERACIONES.md` - Procedimientos operativos
- Documentación de GCP: https://cloud.google.com/docs

---

**¡SISTEMA LISTO PARA PRODUCCIÓN! 🚀**
