# 🚀 GUÍA DE DESPLIEGUE A PRODUCCIÓN - SISTEMA GMAO

**Fecha de creación:** 1 de octubre de 2025  
**Versión:** 1.0  
**Tiempo estimado total:** 12-14 días laborables

---

## 📋 ÍNDICE

1. [Fase 1: Seguridad (Días 1-2)](#fase-1-seguridad)
2. [Fase 2: Migraciones de Base de Datos (Día 3)](#fase-2-migraciones)
3. [Fase 3: Secret Manager y Variables (Día 4)](#fase-3-secret-manager)
4. [Fase 4: Google Cloud Storage (Días 5-6)](#fase-4-cloud-storage)
5. [Fase 5: Cloud Scheduler (Días 7-9)](#fase-5-cloud-scheduler)
6. [Fase 6: Testing y CI/CD (Días 10-11)](#fase-6-testing)
7. [Fase 7: Deployment Final (Días 12-13)](#fase-7-deployment)
8. [Fase 8: Monitoreo Post-Deploy (Día 14)](#fase-8-monitoreo)

---

## <a name="fase-1-seguridad"></a>📌 FASE 1: SEGURIDAD (DÍAS 1-2) 🔴

### Objetivo
Implementar protecciones críticas de seguridad antes del deployment.

### Tareas

#### 1.1 Implementar CSRF Protection

**Archivo:** `app/extensions.py`

```python
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
```

**Archivo:** `app/factory.py` (añadir después de `db.init_app(app)`)

```python
# Inicializar CSRF Protection
from app.extensions import csrf
csrf.init_app(app)

# Excluir rutas de API si es necesario
@csrf.exempt
def api_route():
    pass
```

#### 1.2 Configurar SESSION_COOKIE_SECURE Dinámicamente

**Archivo:** `app/factory.py` (reemplazar línea 82)

**ANTES:**
```python
app.config["SESSION_COOKIE_SECURE"] = False  # Deshabilitar HTTPS en desarrollo
```

**DESPUÉS:**
```python
# Activar HTTPS solo en producción
is_production = os.getenv("GAE_ENV", "").startswith("standard") or \
                os.getenv("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_SECURE"] = is_production
app.config["REMEMBER_COOKIE_SECURE"] = is_production

# Log de configuración de seguridad
if is_production:
    app.logger.info("🔒 Modo producción: Cookies seguras activadas (HTTPS)")
else:
    app.logger.info("🔓 Modo desarrollo: Cookies seguras desactivadas")
```

#### 1.3 Implementar Rate Limiting

**Instalar dependencia:**
```bash
pip install Flask-Limiter
pip freeze > requirements.txt
```

**Archivo:** `app/extensions.py`

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
```

**Archivo:** `app/factory.py` (después de csrf.init_app)

```python
from app.extensions import limiter
limiter.init_app(app)
```

**Aplicar en rutas críticas:**

**Archivo:** `app/controllers/usuarios_controller.py`

```python
from app.extensions import limiter

@usuarios_controller.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Máximo 5 intentos por minuto
def login():
    # ... código existente ...
```

#### 1.4 Limpiar Credenciales Hardcodeadas

**Archivo:** `.env.example` (URGENTE - líneas 28-30)

**ANTES:**
```bash
MAIL_USERNAME=j_hidalgo@disfood.com 
MAIL_PASSWORD=dvematimfpjjpxji
```

**DESPUÉS:**
```bash
MAIL_USERNAME=tu_email@ejemplo.com
MAIL_PASSWORD=tu_password_aqui_cambiar_en_produccion
```

**⚠️ CRÍTICO:** Si este archivo ya está en GitHub, las credenciales están comprometidas:

```bash
# Rotar contraseña inmediatamente
# Generar nueva contraseña de aplicación en Gmail
# Actualizar Secret Manager en GCP

# Eliminar del historial de Git (opcional)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.example" \
  --prune-empty --tag-name-filter cat -- --all
```

#### 1.5 Implementar CORS (Si aplica)

**Solo si la API se consume desde otro dominio:**

```bash
pip install flask-cors
```

**Archivo:** `app/factory.py`

```python
from flask_cors import CORS

# Configurar CORS restrictivo
if os.getenv("ENABLE_CORS", "False").lower() == "true":
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv("CORS_ORIGINS", "https://tu-frontend.com").split(","),
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
```

### Checklist Fase 1

```bash
[✅] CSRF Protection implementado y probado
[✅] SESSION_COOKIE_SECURE dinámico configurado
[✅] Rate Limiting en /login y APIs críticas
[✅] Credenciales eliminadas de .env.example
[✅] Contraseñas rotadas en producción
[✅] CORS configurado (si aplica)
[✅] Tests de seguridad ejecutados
```

### Tests de Validación

```bash
# Test 1: CSRF Protection
curl -X POST https://tu-app.com/api/test \
  -H "Content-Type: application/json" \
  --fail
# Debe retornar 400 (CSRF token missing)

# Test 2: Rate Limiting
for i in {1..10}; do curl https://tu-app.com/login; done
# Debe bloquear después de 5 intentos

# Test 3: HTTPS
curl http://tu-app.com
# Debe redirigir a https://
```

---

## <a name="fase-2-migraciones"></a>📌 FASE 2: MIGRACIONES DE BASE DE DATOS (DÍA 3) 🔴

### Objetivo
Implementar sistema de migraciones para gestionar cambios en la base de datos sin pérdida de datos.

### Tareas

#### 2.1 Instalar Flask-Migrate

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Instalar Flask-Migrate
pip install Flask-Migrate==4.0.7

# Actualizar requirements.txt
pip freeze > requirements.txt
```

#### 2.2 Configurar Flask-Migrate

**Archivo:** `app/extensions.py`

```python
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
```

**Archivo:** `app/factory.py` (después de `db.init_app(app)`)

```python
# Inicializar migraciones
from app.extensions import migrate
migrate.init_app(app, db)

app.logger.info("✅ Sistema de migraciones inicializado")
```

#### 2.3 Crear Migraciones Iniciales

```bash
# 1. Inicializar carpeta de migraciones
flask db init

# 2. Crear migración inicial (captura estado actual)
flask db migrate -m "Migración inicial - Sistema GMAO completo"

# 3. Revisar archivo generado en migrations/versions/
# Verificar que incluye todos los modelos

# 4. Aplicar migración a BD de desarrollo
flask db upgrade

# 5. Verificar tablas creadas
flask shell
>>> from app.extensions import db
>>> db.engine.table_names()
>>> exit()
```

#### 2.4 Crear Script de Migración Segura

**Archivo:** `scripts/migrate_db.sh` (nuevo)

```bash
#!/bin/bash
# Script de migración segura para producción

set -e  # Salir en caso de error

echo "🔄 Iniciando migración de base de datos..."

# 1. Backup automático
echo "📦 Creando backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
gcloud sql export sql gmao-postgres \
  gs://gmao-sistema-backups/pre-migration-${timestamp}.sql \
  --database=postgres

# 2. Verificar estado actual
echo "🔍 Verificando estado actual..."
flask db current

# 3. Mostrar migraciones pendientes
echo "📋 Migraciones pendientes:"
flask db show

# 4. Ejecutar migraciones
echo "⚡ Aplicando migraciones..."
flask db upgrade

# 5. Verificar éxito
echo "✅ Migración completada"
flask db current

echo "🎉 Proceso finalizado con éxito"
```

#### 2.5 Crear Script de Rollback

**Archivo:** `scripts/rollback_db.sh` (nuevo)

```bash
#!/bin/bash
# Script de rollback de migraciones

set -e

echo "⚠️  ROLLBACK DE BASE DE DATOS"
echo "Esto revertirá la última migración aplicada"
read -p "¿Continuar? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Rollback cancelado"
    exit 1
fi

# Backup antes de rollback
echo "📦 Creando backup de seguridad..."
timestamp=$(date +%Y%m%d_%H%M%S)
gcloud sql export sql gmao-postgres \
  gs://gmao-sistema-backups/pre-rollback-${timestamp}.sql \
  --database=postgres

# Ejecutar rollback
echo "⏪ Revirtiendo última migración..."
flask db downgrade

echo "✅ Rollback completado"
flask db current
```

#### 2.6 Probar Flujo Completo

```bash
# 1. Modificar un modelo (ejemplo)
# app/models/activo.py - añadir campo:
# observaciones = db.Column(db.Text, nullable=True)

# 2. Crear migración
flask db migrate -m "Añadir campo observaciones a Activo"

# 3. Revisar archivo generado
# migrations/versions/xxxxx_añadir_campo_observaciones.py

# 4. Aplicar en desarrollo
flask db upgrade

# 5. Probar rollback
flask db downgrade

# 6. Re-aplicar
flask db upgrade
```

### Checklist Fase 2

```bash
[✅] Flask-Migrate instalado y configurado
[✅] Migración inicial creada
[✅] Migración aplicada en desarrollo
[✅] Scripts de migración creados
[✅] Script de rollback creado
[✅] Flujo completo probado
[✅] Documentación actualizada
```

### Comandos Útiles

```bash
# Ver estado actual
flask db current

# Ver historial
flask db history

# Crear migración
flask db migrate -m "Descripción"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade

# Revertir a versión específica
flask db downgrade <revision_id>

# Mostrar SQL sin ejecutar
flask db upgrade --sql
```

---

## <a name="fase-3-secret-manager"></a>📌 FASE 3: SECRET MANAGER Y VARIABLES (DÍA 4) 🔴

### Objetivo
Migrar todas las credenciales sensibles a Google Cloud Secret Manager.

### Tareas

#### 3.1 Generar Credenciales Seguras

```bash
# 1. Generar SECRET_KEY (64 caracteres aleatorios)
python -c "import secrets; print(secrets.token_hex(32))"

# 2. Guardar en archivo temporal
# secret_key.txt, db_password.txt, etc.
```

#### 3.2 Crear Secrets en Google Cloud

**Archivo:** `scripts/create_secrets.sh` (nuevo)

```bash
#!/bin/bash
# Script para crear todos los secrets necesarios en GCP

set -e

PROJECT_ID="gmao-sistema"
SERVICE_ACCOUNT="gmao-sistema@appspot.gserviceaccount.com"

echo "🔐 Creando secrets en Google Cloud Secret Manager"
echo "Proyecto: $PROJECT_ID"

# 1. SECRET_KEY
echo "Creando gmao-secret-key..."
if [ -f "secret_key.txt" ]; then
    gcloud secrets create gmao-secret-key \
        --data-file=secret_key.txt \
        --project=$PROJECT_ID \
        --replication-policy="automatic"
    echo "✅ gmao-secret-key creado"
else
    echo "⚠️  Archivo secret_key.txt no encontrado"
fi

# 2. DB_PASSWORD
echo "Creando gmao-db-password..."
if [ -f "db_password.txt" ]; then
    gcloud secrets create gmao-db-password \
        --data-file=db_password.txt \
        --project=$PROJECT_ID \
        --replication-policy="automatic"
    echo "✅ gmao-db-password creado"
else
    echo "⚠️  Archivo db_password.txt no encontrado"
fi

# 3. OPENAI_API_KEY (opcional)
echo "Creando gmao-openai-key..."
if [ -f "openai_key.txt" ]; then
    gcloud secrets create gmao-openai-key \
        --data-file=openai_key.txt \
        --project=$PROJECT_ID \
        --replication-policy="automatic"
    echo "✅ gmao-openai-key creado"
else
    echo "⚠️  Archivo openai_key.txt no encontrado (opcional)"
fi

# 4. MAIL_PASSWORD
echo "Creando gmao-mail-password..."
if [ -f "mail_password.txt" ]; then
    gcloud secrets create gmao-mail-password \
        --data-file=mail_password.txt \
        --project=$PROJECT_ID \
        --replication-policy="automatic"
    echo "✅ gmao-mail-password creado"
else
    echo "⚠️  Archivo mail_password.txt no encontrado"
fi

# 5. Configurar permisos
echo "Configurando permisos de acceso..."
for secret in gmao-secret-key gmao-db-password gmao-openai-key gmao-mail-password; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor" \
        --project=$PROJECT_ID 2>/dev/null || echo "Secret $secret no existe o permisos ya configurados"
done

echo "🎉 Todos los secrets creados y configurados"

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
rm -f secret_key.txt db_password.txt openai_key.txt mail_password.txt

echo "✅ Proceso completado"
```

#### 3.3 Actualizar app.yaml

**Archivo:** `app.yaml` (reemplazar sección env_variables)

```yaml
env_variables:
  FLASK_ENV: production
  DB_TYPE: postgresql
  DB_USER: postgres
  DB_NAME: postgres
  DB_HOST: "/cloudsql/gmao-sistema:us-central1:gmao-postgres"
  SERVER_URL: https://gmao-sistema.uc.r.appspot.com
  ITEMS_PER_PAGE: "25"
  MAX_CONTENT_LENGTH: "16777216"
  
  # Referencias a Secret Manager (se cargan en factory.py)
  SECRET_KEY_NAME: "gmao-secret-key"
  DB_PASSWORD_NAME: "gmao-db-password"
  OPENAI_KEY_NAME: "gmao-openai-key"
  MAIL_PASSWORD_NAME: "gmao-mail-password"
```

#### 3.4 Actualizar factory.py para Leer Secrets

**Archivo:** `app/factory.py` (reemplazar sección de Secret Manager)

```python
# Configuración de SECRET_KEY desde variables de entorno o Secret Manager
if os.getenv("GAE_ENV", "").startswith("standard"):
    # En GCP App Engine, usar Secret Manager
    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "gmao-sistema")

        def get_secret(secret_name):
            """Helper para obtener secretos de Secret Manager"""
            try:
                name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")
            except Exception as e:
                app.logger.error(f"Error accediendo a secret {secret_name}: {e}")
                return None

        # Obtener SECRET_KEY
        secret_key_name = os.getenv("SECRET_KEY_NAME", "gmao-secret-key")
        app.config["SECRET_KEY"] = get_secret(secret_key_name)
        
        # Obtener DB_PASSWORD
        db_password_name = os.getenv("DB_PASSWORD_NAME", "gmao-db-password")
        db_password = get_secret(db_password_name)
        
        # Obtener MAIL_PASSWORD
        mail_password_name = os.getenv("MAIL_PASSWORD_NAME", "gmao-mail-password")
        mail_password = get_secret(mail_password_name)
        
        # Obtener OPENAI_API_KEY (opcional)
        openai_key_name = os.getenv("OPENAI_KEY_NAME", "gmao-openai-key")
        openai_key = get_secret(openai_key_name)
        
        if not app.config["SECRET_KEY"]:
            raise ValueError("SECRET_KEY no pudo ser cargado desde Secret Manager")
        
        app.logger.info("✅ Secrets cargados desde Secret Manager")

    except Exception as e:
        app.logger.error(f"Error crítico accediendo a Secret Manager: {e}")
        raise  # No continuar sin secrets en producción
else:
    # Desarrollo local
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "clave_secreta_fija_para_sesiones_2025_gmao"
    )
    db_password = os.getenv("DB_PASSWORD", "")
    mail_password = os.getenv("MAIL_PASSWORD", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
```

#### 3.5 Crear .env.production Template

**Archivo:** `.env.production.template` (nuevo)

```bash
# Configuración de Producción para GMAO
# Este archivo es solo referencia - NO contiene valores reales
# Los valores reales están en Google Cloud Secret Manager

# Flask
FLASK_ENV=production
FLASK_DEBUG=False

# Base de Datos
DB_TYPE=postgresql
DB_USER=postgres
DB_NAME=postgres
DB_HOST=/cloudsql/gmao-sistema:us-central1:gmao-postgres

# Referencias a Secret Manager
SECRET_KEY_NAME=gmao-secret-key
DB_PASSWORD_NAME=gmao-db-password
MAIL_PASSWORD_NAME=gmao-mail-password
OPENAI_KEY_NAME=gmao-openai-key

# Google Cloud
GOOGLE_CLOUD_PROJECT=gmao-sistema
GAE_ENV=standard

# Configuración de Aplicación
SERVER_URL=https://gmao-sistema.uc.r.appspot.com
SESSION_COOKIE_SECURE=True
MAX_CONTENT_LENGTH=16777216
```

### Checklist Fase 3

```bash
[✅] Credenciales seguras generadas
[✅] Secrets creados en GCP Secret Manager
[✅] Permisos configurados correctamente
[✅] app.yaml actualizado con referencias
[✅] factory.py actualizado para leer secrets
[✅] .env.production.template creado
[✅] Prueba de acceso a secrets exitosa
```

### Tests de Validación

```bash
# Test 1: Verificar secrets en GCP
gcloud secrets list --project=gmao-sistema

# Test 2: Leer un secret
gcloud secrets versions access latest \
  --secret="gmao-secret-key" \
  --project=gmao-sistema

# Test 3: Verificar permisos
gcloud secrets get-iam-policy gmao-secret-key \
  --project=gmao-sistema

# Test 4: Probar en app local con secrets
export GAE_ENV=standard
export GOOGLE_CLOUD_PROJECT=gmao-sistema
python main.py
```

---

## <a name="fase-4-cloud-storage"></a>📌 FASE 4: GOOGLE CLOUD STORAGE (DÍAS 5-6) 🟡

### Objetivo
Migrar sistema de archivos local a Google Cloud Storage para persistencia en App Engine.

### Tareas

#### 4.1 Crear Bucket en GCP

```bash
# 1. Crear bucket
gsutil mb -p gmao-sistema -c STANDARD -l us-central1 \
  gs://gmao-sistema-uploads

# 2. Configurar CORS (si es necesario)
cat > cors-config.json <<EOF
[
  {
    "origin": ["https://gmao-sistema.uc.r.appspot.com"],
    "method": ["GET", "POST", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors-config.json gs://gmao-sistema-uploads

# 3. Configurar lifecycle (eliminar archivos antiguos)
cat > lifecycle-config.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 365,
          "matchesPrefix": ["temp/"]
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle-config.json gs://gmao-sistema-uploads

# 4. Configurar permisos (privado por defecto)
gsutil iam ch allUsers:objectViewer gs://gmao-sistema-uploads
# NOTA: Solo si necesitas archivos públicos
```

#### 4.2 Crear Helper para Cloud Storage

**Archivo:** `app/utils/storage.py` (nuevo)

```python
"""
Helper para gestionar archivos en Google Cloud Storage
"""
import os
from google.cloud import storage
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)


class StorageManager:
    """Gestor de almacenamiento compatible con local y GCS"""
    
    def __init__(self, app=None):
        self.app = app
        self.is_gcs = False
        self.bucket = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar con configuración de Flask"""
        self.app = app
        upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
        
        # Detectar si usamos GCS
        if upload_folder.startswith("gs://"):
            self.is_gcs = True
            bucket_name = upload_folder.replace("gs://", "").split("/")[0]
            self.bucket_prefix = "/".join(upload_folder.replace("gs://", "").split("/")[1:])
            
            try:
                client = storage.Client()
                self.bucket = client.bucket(bucket_name)
                logger.info(f"✅ Cloud Storage inicializado: {bucket_name}")
            except Exception as e:
                logger.error(f"❌ Error inicializando Cloud Storage: {e}")
                raise
        else:
            self.is_gcs = False
            self.local_path = upload_folder
            os.makedirs(upload_folder, exist_ok=True)
            logger.info(f"✅ Almacenamiento local inicializado: {upload_folder}")
    
    def save_file(self, file, folder="", filename=None):
        """
        Guardar archivo en GCS o localmente
        
        Args:
            file: FileStorage object de Flask
            folder: Subcarpeta dentro del bucket/uploads
            filename: Nombre personalizado (opcional)
        
        Returns:
            str: Path o URL del archivo guardado
        """
        if not filename:
            filename = secure_filename(file.filename)
        
        # Construir path completo
        if folder:
            full_path = os.path.join(folder, filename).replace("\\", "/")
        else:
            full_path = filename
        
        if self.is_gcs:
            # Guardar en GCS
            try:
                blob_name = os.path.join(self.bucket_prefix, full_path).replace("\\", "/")
                blob = self.bucket.blob(blob_name)
                blob.upload_from_file(file, content_type=file.content_type)
                
                logger.info(f"📤 Archivo subido a GCS: {blob_name}")
                return f"gs://{self.bucket.name}/{blob_name}"
            except Exception as e:
                logger.error(f"❌ Error subiendo a GCS: {e}")
                raise
        else:
            # Guardar localmente
            local_full_path = os.path.join(self.local_path, full_path)
            os.makedirs(os.path.dirname(local_full_path), exist_ok=True)
            file.save(local_full_path)
            
            logger.info(f"💾 Archivo guardado localmente: {local_full_path}")
            return local_full_path
    
    def delete_file(self, file_path):
        """Eliminar archivo de GCS o localmente"""
        if self.is_gcs and file_path.startswith("gs://"):
            # Eliminar de GCS
            try:
                blob_name = file_path.replace(f"gs://{self.bucket.name}/", "")
                blob = self.bucket.blob(blob_name)
                blob.delete()
                logger.info(f"🗑️ Archivo eliminado de GCS: {blob_name}")
                return True
            except Exception as e:
                logger.error(f"❌ Error eliminando de GCS: {e}")
                return False
        else:
            # Eliminar localmente
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"🗑️ Archivo eliminado localmente: {file_path}")
                return True
            except Exception as e:
                logger.error(f"❌ Error eliminando archivo local: {e}")
                return False
    
    def get_file_url(self, file_path, expiration=3600):
        """
        Obtener URL firmada para descargar archivo
        
        Args:
            file_path: Path del archivo en GCS o local
            expiration: Tiempo de expiración en segundos (default: 1 hora)
        
        Returns:
            str: URL firmada (GCS) o path local
        """
        if self.is_gcs and file_path.startswith("gs://"):
            # Generar URL firmada
            try:
                blob_name = file_path.replace(f"gs://{self.bucket.name}/", "")
                blob = self.bucket.blob(blob_name)
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=expiration,
                    method="GET"
                )
                return url
            except Exception as e:
                logger.error(f"❌ Error generando URL firmada: {e}")
                return None
        else:
            # Retornar path local (se sirve via Flask)
            return file_path
    
    def file_exists(self, file_path):
        """Verificar si archivo existe"""
        if self.is_gcs and file_path.startswith("gs://"):
            try:
                blob_name = file_path.replace(f"gs://{self.bucket.name}/", "")
                blob = self.bucket.blob(blob_name)
                return blob.exists()
            except Exception as e:
                logger.error(f"❌ Error verificando archivo en GCS: {e}")
                return False
        else:
            return os.path.exists(file_path)


# Instancia global
storage_manager = StorageManager()
```

#### 4.3 Integrar en factory.py

**Archivo:** `app/factory.py` (después de configurar UPLOAD_FOLDER)

```python
# Configuración para uploads de archivos
if os.getenv("GAE_ENV", "").startswith("standard"):
    # Producción: Google Cloud Storage
    app.config["UPLOAD_FOLDER"] = "gs://gmao-sistema-uploads"
else:
    # Desarrollo: filesystem local
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "uploads")

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB máximo

# Inicializar Storage Manager
from app.utils.storage import storage_manager
storage_manager.init_app(app)
```

#### 4.4 Actualizar Controladores

**Ejemplo: app/controllers/archivos_controller.py**

```python
from app.utils.storage import storage_manager

@archivos_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    try:
        # Guardar archivo (automáticamente usa GCS o local)
        file_path = storage_manager.save_file(
            file,
            folder=f"ordenes/{orden_id}",
            filename=secure_filename(file.filename)
        )
        
        # Guardar referencia en BD
        archivo = ArchivoAdjunto(
            nombre=file.filename,
            ruta=file_path,
            orden_id=orden_id
        )
        db.session.add(archivo)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "file_path": file_path
        })
    except Exception as e:
        logger.error(f"Error subiendo archivo: {e}")
        return jsonify({"error": str(e)}), 500


@archivos_bp.route("/download/<int:archivo_id>", methods=["GET"])
@login_required
def download_file(archivo_id):
    archivo = ArchivoAdjunto.query.get_or_404(archivo_id)
    
    # Generar URL firmada (GCS) o servir localmente
    url = storage_manager.get_file_url(archivo.ruta, expiration=300)  # 5 minutos
    
    if url:
        return redirect(url)
    else:
        return jsonify({"error": "File not found"}), 404
```

### Checklist Fase 4

```bash
[✅] Bucket de GCS creado y configurado
[✅] CORS y lifecycle configurados
[✅] StorageManager implementado
[✅] factory.py actualizado
[✅] Controladores migrados
[✅] Tests de upload/download exitosos
[✅] Migración de archivos existentes (si aplica)
```

---

## <a name="fase-5-cloud-scheduler"></a>📌 FASE 5: CLOUD SCHEDULER (DÍAS 7-9) 🟡

### Objetivo
Automatizar generación de órdenes de mantenimiento preventivo usando Cloud Scheduler.

### Tareas

#### 5.1 Crear Endpoint HTTP para Scheduler

**Archivo:** `app/routes/planes.py` (añadir nuevo endpoint)

```python
import hmac
import hashlib

@planes_bp.route("/api/generar-ordenes-automaticas", methods=["POST"])
def generar_ordenes_automaticas():
    """
    Endpoint para Cloud Scheduler - Genera órdenes automáticamente
    Protegido con token de autenticación
    """
    # Verificar token de autenticación
    auth_header = request.headers.get("Authorization", "")
    expected_token = os.getenv("SCHEDULER_TOKEN", "")
    
    if not expected_token:
        logger.error("SCHEDULER_TOKEN no configurado")
        return jsonify({"error": "Configuration error"}), 500
    
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Invalid authorization"}), 401
    
    provided_token = auth_header.replace("Bearer ", "")
    
    # Comparación segura de tokens
    if not hmac.compare_digest(provided_token, expected_token):
        logger.warning("Intento de acceso no autorizado a scheduler endpoint")
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Lógica de generación (copiar de scheduler_apscheduler.py)
        from datetime import datetime
        from app.models.plan_mantenimiento import PlanMantenimiento
        from app.models.orden_trabajo import OrdenTrabajo
        from app.models.control_generacion import ControlGeneracion
        from app.extensions import db
        
        logger.info("🤖 Iniciando generación automática de órdenes")
        
        # Obtener planes activos con autogeneración
        planes = PlanMantenimiento.query.filter_by(
            activo=True,
            autogenerar_ordenes=True
        ).all()
        
        ordenes_creadas = 0
        errores = []
        
        for plan in planes:
            try:
                # Verificar si debe generar orden (según frecuencia)
                debe_generar = verificar_debe_generar_orden(plan)
                
                if debe_generar:
                    # Crear orden de trabajo
                    orden = OrdenTrabajo(
                        titulo=f"Mantenimiento: {plan.nombre}",
                        descripcion=plan.descripcion,
                        activo_id=plan.activo_id,
                        plan_id=plan.id,
                        tipo="preventivo",
                        estado="pendiente",
                        prioridad=plan.prioridad or "media",
                        fecha_creacion=datetime.now()
                    )
                    db.session.add(orden)
                    
                    # Registrar control de generación
                    control = ControlGeneracion(
                        plan_id=plan.id,
                        orden_id=orden.id,
                        fecha_generacion=datetime.now()
                    )
                    db.session.add(control)
                    
                    ordenes_creadas += 1
                    logger.info(f"✅ Orden creada para plan {plan.id}: {plan.nombre}")
            
            except Exception as e:
                error_msg = f"Error en plan {plan.id}: {str(e)}"
                logger.error(error_msg)
                errores.append(error_msg)
                continue
        
        # Commit de todas las órdenes
        if ordenes_creadas > 0:
            db.session.commit()
            logger.info(f"🎉 {ordenes_creadas} órdenes creadas exitosamente")
        
        return jsonify({
            "success": True,
            "ordenes_creadas": ordenes_creadas,
            "planes_procesados": len(planes),
            "errores": errores,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Error crítico en generación automática: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def verificar_debe_generar_orden(plan):
    """
    Verificar si debe generar orden según frecuencia y última generación
    """
    from datetime import datetime, timedelta
    from app.models.control_generacion import ControlGeneracion
    
    # Obtener última generación
    ultimo_control = ControlGeneracion.query.filter_by(
        plan_id=plan.id
    ).order_by(ControlGeneracion.fecha_generacion.desc()).first()
    
    if not ultimo_control:
        # Primera vez, generar
        return True
    
    # Calcular próxima fecha según frecuencia
    ultima_fecha = ultimo_control.fecha_generacion
    hoy = datetime.now()
    
    frecuencia_dias = {
        "diaria": 1,
        "semanal": 7,
        "quincenal": 15,
        "mensual": 30,
        "trimestral": 90,
        "semestral": 180,
        "anual": 365
    }
    
    dias = frecuencia_dias.get(plan.frecuencia, 30)
    proxima_fecha = ultima_fecha + timedelta(days=dias)
    
    # Generar si ya pasó la fecha
    return hoy >= proxima_fecha
```

#### 5.2 Crear Secret para Scheduler Token

```bash
# Generar token seguro
python -c "import secrets; print(secrets.token_urlsafe(32))" > scheduler_token.txt

# Crear secret en GCP
gcloud secrets create gmao-scheduler-token \
  --data-file=scheduler_token.txt \
  --project=gmao-sistema

# Configurar permisos
gcloud secrets add-iam-policy-binding gmao-scheduler-token \
  --member="serviceAccount:gmao-sistema@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Limpiar
rm scheduler_token.txt
```

#### 5.3 Actualizar app.yaml

```yaml
env_variables:
  # ... otras variables ...
  SCHEDULER_TOKEN_NAME: "gmao-scheduler-token"
```

#### 5.4 Actualizar factory.py

```python
# En la sección de Secret Manager, añadir:
scheduler_token_name = os.getenv("SCHEDULER_TOKEN_NAME", "gmao-scheduler-token")
scheduler_token = get_secret(scheduler_token_name)
os.environ["SCHEDULER_TOKEN"] = scheduler_token or ""
```

#### 5.5 Configurar Cloud Scheduler

```bash
# 1. Habilitar API
gcloud services enable cloudscheduler.googleapis.com --project=gmao-sistema

# 2. Obtener token (guardar temporalmente)
TOKEN=$(gcloud secrets versions access latest --secret="gmao-scheduler-token")

# 3. Crear job para generación diaria (6:00 AM)
gcloud scheduler jobs create http generar-ordenes-diarias \
  --schedule="0 6 * * *" \
  --uri="https://gmao-sistema.uc.r.appspot.com/planes/api/generar-ordenes-automaticas" \
  --http-method=POST \
  --headers="Authorization=Bearer ${TOKEN},Content-Type=application/json" \
  --location=us-central1 \
  --project=gmao-sistema \
  --description="Generación diaria de órdenes de mantenimiento preventivo"

# 4. Crear job adicional para verificación (cada 12 horas)
gcloud scheduler jobs create http generar-ordenes-verificacion \
  --schedule="0 */12 * * *" \
  --uri="https://gmao-sistema.uc.r.appspot.com/planes/api/generar-ordenes-automaticas" \
  --http-method=POST \
  --headers="Authorization=Bearer ${TOKEN},Content-Type=application/json" \
  --location=us-central1 \
  --project=gmao-sistema \
  --description="Verificación cada 12 horas"

# 5. Listar jobs creados
gcloud scheduler jobs list --location=us-central1 --project=gmao-sistema

# 6. Probar manualmente
gcloud scheduler jobs run generar-ordenes-diarias \
  --location=us-central1 \
  --project=gmao-sistema

# 7. Ver logs
gcloud scheduler jobs describe generar-ordenes-diarias \
  --location=us-central1 \
  --project=gmao-sistema
```

### Checklist Fase 5

```bash
[✅] Endpoint HTTP creado y protegido
[✅] Scheduler token generado y guardado en Secret Manager
[✅] Cloud Scheduler jobs configurados
[✅] Prueba manual exitosa
[✅] Logs de ejecución verificados
[✅] Notificaciones configuradas (opcional)
```

---

## CONTINÚA EN SIGUIENTE ARCHIVO...

**Nota:** Este documento continúa con las fases 6-8 en el siguiente archivo debido a limitaciones de longitud.

Ver: `GUIA_DESPLIEGUE_PRODUCCION_PARTE2.md`
