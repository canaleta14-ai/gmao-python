# 📋 PLAN DE IMPLEMENTACIÓN - FASE 6: TESTING & CI/CD

**Fecha:** 2 de Octubre, 2025  
**Fase:** 6 de 8 (Testing & Integración Continua)  
**Progreso actual:** 62.5% → Objetivo: 75%  
**Tiempo estimado:** 2 horas

---

## 🎯 Objetivos de la Fase 6

1. **Implementar suite completa de tests** para el sistema GMAO
2. **Configurar pytest** con cobertura de código
3. **Crear GitHub Actions workflow** para CI/CD
4. **Establecer calidad mínima** de código (coverage >80%)
5. **Automatizar testing** en cada push/pull request

---

## 📦 Componentes a Implementar

### 1. Configuración de Testing
- [x] pytest (ya instalado)
- [ ] pytest-cov (cobertura)
- [ ] pytest-flask (helpers para Flask)
- [ ] pytest-mock (mocking)
- [ ] coverage.py (reportes)

### 2. Estructura de Tests
```
tests/
├── __init__.py
├── conftest.py                 # Fixtures compartidas
├── test_models/
│   ├── __init__.py
│   ├── test_activo.py
│   ├── test_orden_trabajo.py
│   ├── test_plan_mantenimiento.py
│   ├── test_usuario.py
│   └── test_inventario.py
├── test_controllers/
│   ├── __init__.py
│   ├── test_activos_controller.py
│   ├── test_ordenes_controller.py
│   ├── test_planes_controller.py
│   └── test_usuarios_controller.py
├── test_routes/
│   ├── __init__.py
│   ├── test_activos_routes.py
│   ├── test_ordenes_routes.py
│   ├── test_cron_routes.py          # Tests de Fase 5
│   └── test_auth_routes.py
└── test_integration/
    ├── __init__.py
    ├── test_workflow_completo.py
    └── test_cron_integration.py
```

### 3. GitHub Actions Workflow
```yaml
.github/workflows/
├── ci.yml                      # CI principal
└── coverage.yml                # Reporte de cobertura
```

---

## 📝 Tareas Detalladas

### Tarea 1: Instalar Dependencias de Testing (15 min)

**Paquetes a instalar:**
```bash
pip install pytest pytest-cov pytest-flask pytest-mock coverage
```

**Actualizar requirements.txt:**
```
pytest==8.3.3
pytest-cov==5.0.0
pytest-flask==1.3.0
pytest-mock==3.14.0
coverage==7.6.1
```

---

### Tarea 2: Configurar pytest (15 min)

**Archivo: `pytest.ini`**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    cron: Cron job tests
```

**Archivo: `.coveragerc`**
```ini
[run]
source = app
omit =
    */tests/*
    */migrations/*
    */venv/*
    */__pycache__/*
    */static/*
    */templates/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

---

### Tarea 3: Crear Fixtures Compartidas (20 min)

**Archivo: `tests/conftest.py`**
```python
import pytest
import sys
from pathlib import Path

# Agregar app al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.activo import Activo
from app.models.orden_trabajo import OrdenTrabajo
from app.models.plan_mantenimiento import PlanMantenimiento

@pytest.fixture(scope='session')
def app():
    """Crea la aplicación Flask para testing"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'FLASK_ENV': 'testing'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Cliente de testing Flask"""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Sesión de DB limpia para cada test"""
    with app.app_context():
        yield db.session
        db.session.rollback()
        db.session.remove()

@pytest.fixture
def usuario_admin(db_session):
    """Usuario administrador de prueba"""
    usuario = Usuario(
        username='admin_test',
        email='admin@test.com',
        nombre='Admin',
        apellido='Test',
        rol='Administrador'
    )
    usuario.set_password('password123')
    db_session.add(usuario)
    db_session.commit()
    return usuario

@pytest.fixture
def usuario_tecnico(db_session):
    """Usuario técnico de prueba"""
    usuario = Usuario(
        username='tecnico_test',
        email='tecnico@test.com',
        nombre='Técnico',
        apellido='Test',
        rol='Técnico'
    )
    usuario.set_password('password123')
    db_session.add(usuario)
    db_session.commit()
    return usuario

@pytest.fixture
def activo_test(db_session):
    """Activo de prueba"""
    activo = Activo(
        codigo='ACT-001',
        nombre='Compresor Test',
        tipo='Compresor',
        ubicacion='Planta 1',
        estado='Operativo',
        activo=True
    )
    db_session.add(activo)
    db_session.commit()
    return activo

@pytest.fixture
def plan_mantenimiento_test(db_session, activo_test, usuario_tecnico):
    """Plan de mantenimiento de prueba"""
    from datetime import datetime, timedelta
    
    plan = PlanMantenimiento(
        nombre='Mantenimiento Test',
        descripcion='Plan de prueba',
        activo_id=activo_test.id,
        responsable_id=usuario_tecnico.id,
        frecuencia='Mensual',
        frecuencia_dias=30,
        proxima_ejecucion=datetime.utcnow().date() - timedelta(days=1),  # Vencido
        activo=True
    )
    db_session.add(plan)
    db_session.commit()
    return plan
```

---

### Tarea 4: Tests Unitarios de Modelos (30 min)

**Archivo: `tests/test_models/test_orden_trabajo.py`**
```python
import pytest
from datetime import datetime
from app.models.orden_trabajo import OrdenTrabajo

@pytest.mark.unit
class TestOrdenTrabajoModel:
    
    def test_crear_orden_basica(self, db_session, activo_test, usuario_tecnico):
        """Test creación básica de orden"""
        orden = OrdenTrabajo(
            numero_orden='OT-2024-001',
            activo_id=activo_test.id,
            tecnico_id=usuario_tecnico.id,
            tipo='Preventivo',
            estado='Pendiente',
            descripcion='Test orden'
        )
        db_session.add(orden)
        db_session.commit()
        
        assert orden.id is not None
        assert orden.numero_orden == 'OT-2024-001'
        assert orden.estado == 'Pendiente'
    
    def test_orden_con_plan_mantenimiento(self, db_session, plan_mantenimiento_test, activo_test, usuario_tecnico):
        """Test orden vinculada a plan de mantenimiento"""
        orden = OrdenTrabajo(
            numero_orden='OT-2024-002',
            activo_id=activo_test.id,
            tecnico_id=usuario_tecnico.id,
            plan_mantenimiento_id=plan_mantenimiento_test.id,
            tipo='Preventivo'
        )
        db_session.add(orden)
        db_session.commit()
        
        assert orden.plan_mantenimiento_id == plan_mantenimiento_test.id
        assert orden.plan_mantenimiento.nombre == 'Mantenimiento Test'
    
    def test_relacion_backref_ordenes_generadas(self, db_session, plan_mantenimiento_test):
        """Test backref ordenes_generadas desde plan"""
        assert hasattr(plan_mantenimiento_test, 'ordenes_generadas')
        assert isinstance(plan_mantenimiento_test.ordenes_generadas, list)
```

---

### Tarea 5: Tests de Controllers (30 min)

**Archivo: `tests/test_controllers/test_ordenes_controller.py`**
```python
import pytest
from app.controllers.ordenes_controller import OrdenesController

@pytest.mark.unit
class TestOrdenesController:
    
    def test_listar_ordenes(self, app, db_session):
        """Test listado de órdenes"""
        with app.app_context():
            result = OrdenesController.listar_ordenes()
            assert 'ordenes' in result
            assert isinstance(result['ordenes'], list)
    
    def test_crear_orden(self, app, db_session, activo_test, usuario_tecnico):
        """Test creación de orden"""
        with app.app_context():
            datos = {
                'activo_id': activo_test.id,
                'tecnico_id': usuario_tecnico.id,
                'tipo': 'Preventivo',
                'prioridad': 'Media',
                'descripcion': 'Test orden'
            }
            result = OrdenesController.crear_orden(datos)
            assert result is not None
            assert result.tipo == 'Preventivo'
```

---

### Tarea 6: Tests de Endpoints Cron (30 min)

**Archivo: `tests/test_routes/test_cron_routes.py`**
```python
import pytest
from datetime import datetime, timedelta

@pytest.mark.cron
class TestCronRoutes:
    
    def test_generar_ordenes_preventivas_desarrollo(self, client, plan_mantenimiento_test):
        """Test generación de órdenes en modo desarrollo"""
        response = client.post('/api/cron/generar-ordenes-preventivas')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'planes_revisados' in data
        assert 'ordenes_creadas' in data
        assert data['ordenes_creadas'] >= 1  # Al menos el plan de prueba
    
    def test_generar_ordenes_seguridad_produccion(self, client, app):
        """Test seguridad en modo producción"""
        app.config['FLASK_ENV'] = 'production'
        
        # Sin header - debe fallar
        response = client.post('/api/cron/generar-ordenes-preventivas')
        assert response.status_code == 403
        
        # Con header incorrecto - debe fallar
        response = client.post(
            '/api/cron/generar-ordenes-preventivas',
            headers={'X-Appengine-Cron': 'false'}
        )
        assert response.status_code == 403
        
        # Con header correcto - debe funcionar
        response = client.post(
            '/api/cron/generar-ordenes-preventivas',
            headers={'X-Appengine-Cron': 'true'}
        )
        assert response.status_code == 200
    
    def test_verificar_alertas(self, client, activo_test):
        """Test verificación de alertas de mantenimiento"""
        response = client.post('/api/cron/verificar-alertas')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'activos_revisados' in data
        assert 'alertas_enviadas' in data
    
    def test_endpoint_test_cron(self, client):
        """Test endpoint de testing"""
        response = client.get('/api/cron/test-cron')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'mensaje' in data
        assert 'estadisticas' in data
```

---

### Tarea 7: GitHub Actions Workflow (20 min)

**Archivo: `.github/workflows/ci.yml`**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ master, develop ]
  pull_request:
    branches: [ master, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests with coverage
      env:
        FLASK_ENV: testing
        SECRET_KEY: test-secret-key-for-ci
      run: |
        pytest --cov=app --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Check coverage threshold
      run: |
        coverage report --fail-under=80

  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install linting tools
      run: |
        pip install flake8 black isort
    
    - name: Run flake8
      run: |
        flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app --count --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Check code formatting with black
      run: |
        black --check app
    
    - name: Check import sorting with isort
      run: |
        isort --check-only app
```

---

## 📊 Métricas de Éxito

### Cobertura de Código (Coverage)
- **Mínimo requerido:** 80%
- **Objetivo ideal:** 90%+
- **Áreas críticas:** Controllers, Routes, Models

### Tests por Categoría
- **Unit tests:** 30+ tests
- **Integration tests:** 10+ tests
- **Cron tests:** 5+ tests
- **Total:** 45+ tests

### CI/CD
- ✅ Workflow ejecuta en cada push
- ✅ Tests pasan en Python 3.11 y 3.12
- ✅ Cobertura >80%
- ✅ Lint checks pasando

---

## 🔄 Cronograma de Implementación

| Tarea | Tiempo | Responsable | Estado |
|-------|--------|-------------|--------|
| 1. Instalar dependencias | 15 min | - | ⏳ Pendiente |
| 2. Configurar pytest | 15 min | - | ⏳ Pendiente |
| 3. Crear fixtures | 20 min | - | ⏳ Pendiente |
| 4. Tests de modelos | 30 min | - | ⏳ Pendiente |
| 5. Tests de controllers | 30 min | - | ⏳ Pendiente |
| 6. Tests de cron | 30 min | - | ⏳ Pendiente |
| 7. GitHub Actions | 20 min | - | ⏳ Pendiente |
| **TOTAL** | **2h 40min** | - | **0%** |

---

## 📝 Comandos Útiles

### Ejecutar todos los tests:
```bash
pytest
```

### Tests con cobertura:
```bash
pytest --cov=app --cov-report=html
```

### Solo tests unitarios:
```bash
pytest -m unit
```

### Solo tests de cron:
```bash
pytest -m cron
```

### Ver reporte de cobertura:
```bash
coverage report
coverage html  # Genera htmlcov/index.html
```

### Ejecutar tests específicos:
```bash
pytest tests/test_routes/test_cron_routes.py -v
```

---

## 🎯 Próximos Pasos (Post-Fase 6)

**Fase 7: Deployment GCP**
- Cloud SQL PostgreSQL
- App Engine deployment
- **Deploy cron.yaml** ← Los tests de cron deben pasar primero
- Cloud Storage buckets

**Fase 8: Monitoring**
- Sentry.io
- GCP Logging
- Alertas de errores

---

## ✅ Checklist de Completitud

- [ ] pytest, pytest-cov, pytest-flask instalados
- [ ] pytest.ini configurado
- [ ] .coveragerc configurado
- [ ] tests/conftest.py con fixtures
- [ ] Tests de modelos (5+ archivos)
- [ ] Tests de controllers (4+ archivos)
- [ ] Tests de routes (4+ archivos)
- [ ] Tests de cron (1 archivo, 5+ tests)
- [ ] GitHub Actions workflow (.github/workflows/ci.yml)
- [ ] Coverage >80%
- [ ] CI pasando en GitHub

---

*Documento creado el 2 de Octubre, 2025*  
*Proyecto: GMAO Sistema - github.com/canaleta14-ai/gmao-sistema*
