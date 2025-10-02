# 🛠️ Comandos Útiles - GMAO Sistema

## 📊 Testing

### Ejecutar todos los tests
```bash
pytest tests/ -v
```

### Ejecutar con cobertura
```bash
pytest tests/ --cov=app --cov-report=html
```

### Ejecutar solo tests que pasan
```bash
pytest tests/test_models/test_orden_trabajo.py -v
```

### Ejecutar test específico
```bash
pytest tests/test_models/test_activo.py::TestActivoModel::test_crear_activo_basico -v
```

### Ver reporte HTML de cobertura
```bash
# Windows
start htmlcov/index.html

# Mac
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### Ejecutar solo tests rápidos
```bash
pytest tests/ -v -m "not slow"
```

### Ejecutar solo tests unitarios
```bash
pytest tests/ -v -m unit
```

### Ejecutar solo tests de seguridad
```bash
pytest tests/ -v -m security
```

### Ejecutar con output detallado
```bash
pytest tests/ -vv --tb=long
```

### Ejecutar y parar en primer fallo
```bash
pytest tests/ -v -x
```

### Ejecutar tests en paralelo (más rápido)
```bash
pytest tests/ -v -n auto
```

---

## 🚀 Desarrollo Local

### Activar entorno virtual
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Instalar dependencias
```bash
pip install -r requirements.txt
```

### Inicializar base de datos
```bash
python init_db.py
```

### Ejecutar servidor desarrollo
```bash
python run.py
```

### Ejecutar con recarga automática
```bash
flask run --reload
```

---

## 🗄️ Base de Datos

### Crear migración
```bash
flask db migrate -m "descripción de cambios"
```

### Aplicar migraciones
```bash
flask db upgrade
```

### Revertir migración
```bash
flask db downgrade
```

### Ver historial de migraciones
```bash
flask db history
```

### Resetear base de datos (desarrollo)
```bash
python init_db.py --reset
```

---

## 🔍 Linting y Formato

### Ejecutar flake8
```bash
flake8 app/ --count --max-line-length=120
```

### Formatear código con black
```bash
black app/
```

### Verificar formato sin cambios
```bash
black --check app/
```

### Ordenar imports con isort
```bash
isort app/
```

### Verificar imports sin cambios
```bash
isort --check-only app/
```

---

## 🔒 Seguridad

### Verificar vulnerabilidades en dependencias
```bash
pip install safety
safety check
```

### Escanear código con bandit
```bash
pip install bandit
bandit -r app/
```

### Generar reporte de seguridad
```bash
bandit -r app/ -f json -o security-report.json
```

---

## 📦 Git

### Ver estado
```bash
git status
```

### Añadir todos los cambios
```bash
git add .
```

### Commit con mensaje descriptivo
```bash
git commit -m "feat: descripción del feature"
```

### Push a GitHub
```bash
git push origin master
```

### Ver últimos commits
```bash
git log --oneline -10
```

### Ver cambios no commiteados
```bash
git diff
```

### Ver cambios staged
```bash
git diff --staged
```

### Crear nueva rama
```bash
git checkout -b feature/nombre-feature
```

### Volver a rama master
```bash
git checkout master
```

---

## ☁️ Google Cloud Platform

### Autenticarse
```bash
gcloud auth login
```

### Configurar proyecto
```bash
gcloud config set project gmao-sistema
```

### Listar proyectos
```bash
gcloud projects list
```

### Crear instancia Cloud SQL
```bash
gcloud sql instances create gmao-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1
```

### Crear base de datos
```bash
gcloud sql databases create gmao --instance=gmao-db
```

### Conectar a Cloud SQL localmente
```bash
gcloud sql connect gmao-db --user=postgres
```

### Deploy a App Engine
```bash
gcloud app deploy
```

### Ver logs
```bash
gcloud app logs tail -s default
```

### Abrir app en navegador
```bash
gcloud app browse
```

---

## 🐳 Docker (si aplica)

### Construir imagen
```bash
docker build -t gmao-sistema .
```

### Ejecutar contenedor
```bash
docker run -p 5000:5000 gmao-sistema
```

### Ver contenedores activos
```bash
docker ps
```

### Detener contenedor
```bash
docker stop <container-id>
```

### Ver logs
```bash
docker logs <container-id>
```

---

## 📈 Monitoring

### Ver logs de aplicación
```bash
tail -f logs/app.log
```

### Ver logs de errores
```bash
tail -f logs/error.log
```

### Verificar procesos Python
```bash
# Windows
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Linux/Mac
ps aux | grep python
```

---

## 🧹 Limpieza

### Eliminar archivos .pyc
```bash
# Windows
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item

# Linux/Mac
find . -type f -name "*.pyc" -delete
```

### Eliminar __pycache__
```bash
# Windows
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Linux/Mac
find . -type d -name "__pycache__" -exec rm -r {} +
```

### Limpiar coverage
```bash
rm -rf htmlcov/ .coverage coverage.xml
```

---

## 🔧 Troubleshooting

### Reinstalar dependencias
```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Verificar versión de Python
```bash
python --version
```

### Verificar paquetes instalados
```bash
pip list
```

### Verificar variable de entorno
```bash
# Windows
echo $env:FLASK_APP

# Linux/Mac
echo $FLASK_APP
```

### Activar modo debug
```bash
$env:FLASK_ENV="development"  # Windows
export FLASK_ENV=development   # Linux/Mac
```

---

## 📝 Utilidades

### Contar líneas de código
```bash
# Windows PowerShell
(Get-ChildItem -Recurse -Include "*.py" -Exclude "*test*","*migration*" | Get-Content).Count

# Linux/Mac
find app/ -name "*.py" | xargs wc -l
```

### Buscar en código
```bash
# Windows
Select-String -Path "app\*.py" -Pattern "TODO" -Recurse

# Linux/Mac
grep -r "TODO" app/
```

### Ver estructura de directorios
```bash
# Windows
tree /F /A

# Linux/Mac
tree -L 3
```

---

## 🎯 Comandos de la Sesión Actual

### Ver cobertura rápida
```bash
pytest tests/ --cov=app --cov-report=term --tb=no -q
```

### Ejecutar solo tests pasando
```bash
pytest tests/test_models/test_orden_trabajo.py tests/test_models/test_activo.py -v
```

### Generar reporte completo
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing:skip-covered -v
```

---

**Tip:** Añade alias a tu perfil de PowerShell o .bashrc para comandos frecuentes:

```bash
# PowerShell (en $PROFILE)
function Test-All { pytest tests/ -v --cov=app }
function Test-Fast { pytest tests/ -v -m "not slow" }
function Test-Coverage { pytest tests/ --cov=app --cov-report=html; start htmlcov/index.html }

# Bash (en ~/.bashrc)
alias test-all='pytest tests/ -v --cov=app'
alias test-fast='pytest tests/ -v -m "not slow"'
alias test-coverage='pytest tests/ --cov=app --cov-report=html && open htmlcov/index.html'
```
