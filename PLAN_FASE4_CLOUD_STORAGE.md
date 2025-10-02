# 📦 FASE 4: Google Cloud Storage - Plan de Implementación

**Objetivo:** Migrar sistema de archivos local a Google Cloud Storage para persistencia en producción

**Tiempo estimado:** 3-4 horas  
**Prioridad:** 🔴 ALTA (evita pérdida de archivos en App Engine)

---

## 🎯 Problema a Resolver

### **Situación Actual:**
```
App Engine (filesystem efímero)
├─ /uploads/ordenes/         → 🔴 SE PIERDE en cada deploy
└─ /app/static/uploads/       → 🔴 SE PIERDE en cada deploy
    └─ manuales/
```

**Consecuencia:** Cuando App Engine redeploys (por actualización, escala, mantenimiento), todos los archivos subidos desaparecen.

### **Solución:**
```
Google Cloud Storage Bucket
├─ ordenes/                   → ✅ PERSISTENTE
│   ├─ OT001_foto1.jpg
│   └─ OT002_factura.pdf
└─ manuales/                  → ✅ PERSISTENTE
    ├─ CALDM001_manual.pdf
    └─ BOMH001_schema.pdf
```

---

## 📋 Tareas

### **1. Instalación de Dependencias** ⏱️ 5 min

```bash
pip install google-cloud-storage==2.18.2
pip freeze > requirements.txt
```

**Verificación:**
```python
from google.cloud import storage
print("✅ google-cloud-storage instalado")
```

---

### **2. Crear Utilidad de Storage** ⏱️ 30 min

**Archivo:** `app/utils/storage.py` (NUEVO)

```python
"""
Utilidades para Google Cloud Storage
"""
import os
import logging
from werkzeug.utils import secure_filename
from datetime import timedelta

logger = logging.getLogger(__name__)

# Configuración
BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'gmao-uploads')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def get_storage_client():
    """
    Obtiene cliente de Storage con lazy import
    """
    try:
        from google.cloud import storage
        return storage.Client()
    except Exception as e:
        logger.error(f"Error al crear cliente Storage: {e}")
        return None

def upload_file(file, folder, filename=None):
    """
    Sube archivo a Cloud Storage
    
    Args:
        file: FileStorage object de Flask
        folder: Carpeta destino ('ordenes', 'manuales')
        filename: Nombre opcional (si None, usa file.filename)
    
    Returns:
        str: URL pública o None si falla
    """
    # Validar tamaño
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        logger.error(f"Archivo demasiado grande: {size} bytes")
        return None
    
    # Detectar entorno
    is_gcp = os.getenv('GAE_ENV', '').startswith('standard') or \
             os.getenv('K_SERVICE') or \
             os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if is_gcp:
        # PRODUCCIÓN: Cloud Storage
        return _upload_to_gcs(file, folder, filename)
    else:
        # DESARROLLO: Sistema de archivos local
        return _upload_to_local(file, folder, filename)

def _upload_to_gcs(file, folder, filename):
    """Subida a Google Cloud Storage"""
    try:
        client = get_storage_client()
        if not client:
            return None
        
        bucket = client.bucket(BUCKET_NAME)
        
        # Nombre seguro
        if not filename:
            filename = secure_filename(file.filename)
        
        blob_path = f"{folder}/{filename}"
        blob = bucket.blob(blob_path)
        
        # Subir
        blob.upload_from_file(file, content_type=file.content_type)
        
        # URL pública (o firmada si el bucket es privado)
        logger.info(f"✅ Archivo subido a GCS: {blob_path}")
        return blob.public_url
        
    except Exception as e:
        logger.error(f"Error subiendo a GCS: {e}")
        return None

def _upload_to_local(file, folder, filename):
    """Subida a filesystem local (desarrollo)"""
    try:
        # Directorio base
        base_dir = os.path.join('uploads', folder)
        os.makedirs(base_dir, exist_ok=True)
        
        # Nombre seguro
        if not filename:
            filename = secure_filename(file.filename)
        
        filepath = os.path.join(base_dir, filename)
        file.save(filepath)
        
        logger.info(f"✅ Archivo guardado localmente: {filepath}")
        return f"/uploads/{folder}/{filename}"
        
    except Exception as e:
        logger.error(f"Error guardando localmente: {e}")
        return None

def delete_file(filepath, folder):
    """
    Elimina archivo de Storage
    
    Args:
        filepath: Ruta o nombre del archivo
        folder: Carpeta ('ordenes', 'manuales')
    
    Returns:
        bool: True si se eliminó correctamente
    """
    is_gcp = os.getenv('GAE_ENV', '').startswith('standard') or \
             os.getenv('K_SERVICE') or \
             os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if is_gcp:
        return _delete_from_gcs(filepath, folder)
    else:
        return _delete_from_local(filepath, folder)

def _delete_from_gcs(filepath, folder):
    """Eliminar de Cloud Storage"""
    try:
        client = get_storage_client()
        if not client:
            return False
        
        bucket = client.bucket(BUCKET_NAME)
        
        # Extraer nombre del archivo de la URL
        filename = os.path.basename(filepath)
        blob_path = f"{folder}/{filename}"
        
        blob = bucket.blob(blob_path)
        blob.delete()
        
        logger.info(f"✅ Archivo eliminado de GCS: {blob_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error eliminando de GCS: {e}")
        return False

def _delete_from_local(filepath, folder):
    """Eliminar de filesystem local"""
    try:
        # filepath puede ser relativo o absoluto
        if filepath.startswith('/uploads/'):
            filepath = filepath[1:]  # Quitar '/' inicial
        
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"✅ Archivo eliminado localmente: {filepath}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error eliminando localmente: {e}")
        return False

def get_signed_url(filepath, folder, expiration=3600):
    """
    Genera URL firmada para descarga segura (solo GCP)
    
    Args:
        filepath: Ruta del archivo
        folder: Carpeta
        expiration: Segundos de validez (default 1 hora)
    
    Returns:
        str: URL firmada o URL normal si es local
    """
    is_gcp = os.getenv('GAE_ENV', '').startswith('standard') or \
             os.getenv('K_SERVICE') or \
             os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if not is_gcp:
        # Local: devolver URL normal
        return filepath
    
    try:
        client = get_storage_client()
        if not client:
            return filepath
        
        bucket = client.bucket(BUCKET_NAME)
        filename = os.path.basename(filepath)
        blob_path = f"{folder}/{filename}"
        blob = bucket.blob(blob_path)
        
        # URL firmada válida por 1 hora
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration),
            method="GET"
        )
        
        return url
        
    except Exception as e:
        logger.error(f"Error generando URL firmada: {e}")
        return filepath

def list_files(folder, prefix=''):
    """
    Lista archivos en una carpeta
    
    Args:
        folder: Carpeta ('ordenes', 'manuales')
        prefix: Filtro opcional de prefijo
    
    Returns:
        list: Lista de nombres de archivo
    """
    is_gcp = os.getenv('GAE_ENV', '').startswith('standard') or \
             os.getenv('K_SERVICE') or \
             os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if is_gcp:
        return _list_from_gcs(folder, prefix)
    else:
        return _list_from_local(folder, prefix)

def _list_from_gcs(folder, prefix):
    """Listar archivos de Cloud Storage"""
    try:
        client = get_storage_client()
        if not client:
            return []
        
        bucket = client.bucket(BUCKET_NAME)
        blob_prefix = f"{folder}/{prefix}" if prefix else f"{folder}/"
        
        blobs = bucket.list_blobs(prefix=blob_prefix)
        return [blob.name.split('/')[-1] for blob in blobs]
        
    except Exception as e:
        logger.error(f"Error listando de GCS: {e}")
        return []

def _list_from_local(folder, prefix):
    """Listar archivos locales"""
    try:
        base_dir = os.path.join('uploads', folder)
        if not os.path.exists(base_dir):
            return []
        
        files = os.listdir(base_dir)
        if prefix:
            files = [f for f in files if f.startswith(prefix)]
        
        return files
        
    except Exception as e:
        logger.error(f"Error listando localmente: {e}")
        return []
```

**Características:**
- ✅ Detección automática de entorno (GCP vs local)
- ✅ Validación de tamaño de archivo (10 MB max)
- ✅ URLs firmadas para seguridad
- ✅ Operaciones CRUD completas
- ✅ Logging detallado
- ✅ Manejo de errores robusto

---

### **3. Modificar Controlador de Órdenes** ⏱️ 40 min

**Archivo:** `app/controllers/ordenes_controller.py`

**Cambios necesarios:**

#### **3.1 Importar storage utility**

```python
# Añadir al inicio del archivo
from app.utils.storage import upload_file, delete_file, get_signed_url
```

#### **3.2 Modificar función de subida de archivos**

Buscar la función que maneja archivos adjuntos (probablemente en `crear_orden` o `editar_orden`):

**ANTES:**
```python
if 'archivo' in request.files:
    file = request.files['archivo']
    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', 'ordenes', filename)
        file.save(filepath)
```

**DESPUÉS:**
```python
if 'archivo' in request.files:
    file = request.files['archivo']
    if file and file.filename:
        # Generar nombre único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(file.filename)[1]
        filename = f"OT{orden.id}_{timestamp}{ext}"
        
        # Subir (automáticamente detecta GCP vs local)
        file_url = upload_file(file, 'ordenes', filename)
        
        if file_url:
            # Guardar en DB
            adjunto = ArchivoAdjunto(
                orden_id=orden.id,
                nombre_archivo=file.filename,
                ruta_archivo=file_url,
                tipo_archivo=file.content_type
            )
            db.session.add(adjunto)
        else:
            flash('Error al subir archivo', 'error')
```

#### **3.3 Modificar función de descarga/visualización**

**ANTES:**
```python
@ordenes_bp.route('/archivo/<int:archivo_id>')
def descargar_archivo(archivo_id):
    archivo = ArchivoAdjunto.query.get_or_404(archivo_id)
    return send_file(archivo.ruta_archivo)
```

**DESPUÉS:**
```python
@ordenes_bp.route('/archivo/<int:archivo_id>')
def descargar_archivo(archivo_id):
    archivo = ArchivoAdjunto.query.get_or_404(archivo_id)
    
    # Si es GCP, generar URL firmada
    url = get_signed_url(archivo.ruta_archivo, 'ordenes')
    
    # Si es URL de GCS, redirigir
    if url.startswith('http'):
        return redirect(url)
    
    # Si es local, enviar archivo
    return send_file(archivo.ruta_archivo)
```

#### **3.4 Modificar función de eliminación**

**ANTES:**
```python
if archivo.ruta_archivo and os.path.exists(archivo.ruta_archivo):
    os.remove(archivo.ruta_archivo)
```

**DESPUÉS:**
```python
if archivo.ruta_archivo:
    delete_file(archivo.ruta_archivo, 'ordenes')
```

---

### **4. Modificar Controlador de Manuales** ⏱️ 40 min

**Archivo:** `app/controllers/manuales_controller.py`

Aplicar cambios similares a los del controlador de órdenes:

#### **4.1 Importar storage utility**
```python
from app.utils.storage import upload_file, delete_file, get_signed_url
```

#### **4.2 Modificar función de subida**

**ANTES:**
```python
if 'archivo_pdf' in request.files:
    file = request.files['archivo_pdf']
    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join('app', 'static', 'uploads', 'manuales', filename)
        file.save(filepath)
        manual.ruta_archivo = f'/static/uploads/manuales/{filename}'
```

**DESPUÉS:**
```python
if 'archivo_pdf' in request.files:
    file = request.files['archivo_pdf']
    if file and file.filename:
        # Generar nombre único
        codigo_activo = manual.activo.codigo if manual.activo else 'MANUAL'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{codigo_activo}_{timestamp}.pdf"
        
        # Subir a Storage
        file_url = upload_file(file, 'manuales', filename)
        
        if file_url:
            manual.ruta_archivo = file_url
        else:
            flash('Error al subir manual', 'error')
```

#### **4.3 Modificar función de visualización**

**ANTES:**
```python
@manuales_bp.route('/manual/<int:manual_id>/ver')
def ver_manual(manual_id):
    manual = Manual.query.get_or_404(manual_id)
    return send_file(manual.ruta_archivo)
```

**DESPUÉS:**
```python
@manuales_bp.route('/manual/<int:manual_id>/ver')
def ver_manual(manual_id):
    manual = Manual.query.get_or_404(manual_id)
    
    # Generar URL firmada si es GCS
    url = get_signed_url(manual.ruta_archivo, 'manuales')
    
    if url.startswith('http'):
        return redirect(url)
    
    return send_file(manual.ruta_archivo)
```

---

### **5. Actualizar Variables de Entorno** ⏱️ 5 min

**Archivo:** `.env.example`

```env
# ====================================
# GOOGLE CLOUD STORAGE
# ====================================

# Nombre del bucket de GCS (crear en GCP Console)
GCS_BUCKET_NAME=gmao-uploads

# Nota: En producción (App Engine), el bucket debe:
# 1. Existir en el mismo proyecto GCP
# 2. Tener permisos para App Engine service account
# 3. Opcional: Configurar CORS si se accede desde frontend
#
# En desarrollo local, los archivos se guardan en /uploads/
```

---

### **6. Configurar app.yaml para App Engine** ⏱️ 10 min

**Archivo:** `app.yaml` (NUEVO si no existe)

```yaml
runtime: python311

env_variables:
  # Database
  DB_TYPE: "postgresql"
  DB_HOST: "/cloudsql/TU_PROYECTO:REGION:INSTANCIA"
  DB_NAME: "gmao_db"
  DB_USER: "gmao_user"
  
  # Storage
  GCS_BUCKET_NAME: "gmao-uploads"
  
  # App Engine detectado automáticamente vía GAE_ENV

handlers:
  # Archivos estáticos (CSS, JS)
  - url: /static
    static_dir: static
    secure: always
  
  # Todo lo demás a Flask
  - url: /.*
    script: auto
    secure: always

# No necesitamos servir /uploads porque están en GCS
# En local, Flask sirve /uploads normalmente
```

---

### **7. Script de Migración de Archivos Existentes** ⏱️ 30 min

**Archivo:** `scripts/migrate_files_to_gcs.py` (NUEVO)

```python
"""
Migra archivos existentes del filesystem local a Google Cloud Storage
EJECUTAR UNA SOLA VEZ antes del primer deploy
"""
import os
import sys
from pathlib import Path

# Añadir path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import storage
from app import create_app, db
from app.models.orden_trabajo import OrdenTrabajo
from app.models.archivo_adjunto import ArchivoAdjunto
from app.models.manual import Manual

BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'gmao-uploads')

def migrate_ordenes_files():
    """Migra archivos de órdenes de trabajo"""
    print("🔄 Migrando archivos de órdenes...")
    
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    
    local_dir = Path('uploads/ordenes')
    if not local_dir.exists():
        print("⚠️  Directorio uploads/ordenes no existe")
        return
    
    archivos = ArchivoAdjunto.query.all()
    migrated = 0
    
    for archivo in archivos:
        # Ruta local actual
        local_path = Path(archivo.ruta_archivo)
        
        if not local_path.exists():
            print(f"⚠️  Archivo no encontrado: {local_path}")
            continue
        
        # Subir a GCS
        blob_path = f"ordenes/{local_path.name}"
        blob = bucket.blob(blob_path)
        
        try:
            blob.upload_from_filename(str(local_path))
            
            # Actualizar DB con nueva URL
            archivo.ruta_archivo = blob.public_url
            migrated += 1
            
            print(f"✅ Migrado: {local_path.name}")
            
        except Exception as e:
            print(f"❌ Error migrando {local_path.name}: {e}")
    
    db.session.commit()
    print(f"✅ {migrated} archivos de órdenes migrados\n")

def migrate_manuales_files():
    """Migra archivos de manuales"""
    print("🔄 Migrando manuales...")
    
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    
    local_dir = Path('app/static/uploads/manuales')
    if not local_dir.exists():
        print("⚠️  Directorio de manuales no existe")
        return
    
    manuales = Manual.query.filter(Manual.ruta_archivo.isnot(None)).all()
    migrated = 0
    
    for manual in manuales:
        # Extraer nombre del archivo de la ruta
        filename = manual.ruta_archivo.split('/')[-1]
        local_path = local_dir / filename
        
        if not local_path.exists():
            print(f"⚠️  Manual no encontrado: {local_path}")
            continue
        
        # Subir a GCS
        blob_path = f"manuales/{filename}"
        blob = bucket.blob(blob_path)
        
        try:
            blob.upload_from_filename(str(local_path))
            
            # Actualizar DB
            manual.ruta_archivo = blob.public_url
            migrated += 1
            
            print(f"✅ Migrado: {filename}")
            
        except Exception as e:
            print(f"❌ Error migrando {filename}: {e}")
    
    db.session.commit()
    print(f"✅ {migrated} manuales migrados\n")

def main():
    """Ejecutar migración completa"""
    print("=" * 60)
    print("🚀 MIGRACIÓN DE ARCHIVOS A GOOGLE CLOUD STORAGE")
    print("=" * 60)
    print()
    
    # Verificar que estamos configurados para GCS
    if not os.getenv('GOOGLE_CLOUD_PROJECT'):
        print("❌ Error: GOOGLE_CLOUD_PROJECT no configurado")
        print("   Ejecuta: export GOOGLE_CLOUD_PROJECT=tu-proyecto")
        sys.exit(1)
    
    # Crear app context
    app = create_app()
    with app.app_context():
        migrate_ordenes_files()
        migrate_manuales_files()
    
    print("=" * 60)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Verificar archivos en GCS Console")
    print("2. Hacer backup de /uploads/ local")
    print("3. Deploy a App Engine")

if __name__ == '__main__':
    main()
```

**Uso:**
```bash
# 1. Configurar proyecto
export GOOGLE_CLOUD_PROJECT=tu-proyecto-id

# 2. Ejecutar migración
python scripts/migrate_files_to_gcs.py

# 3. Verificar en GCS Console
# https://console.cloud.google.com/storage/browser/gmao-uploads
```

---

### **8. Script de Verificación** ⏱️ 20 min

**Archivo:** `scripts/verify_fase4.py` (NUEVO)

```python
"""
Verificación de Fase 4: Cloud Storage
"""
import os
import sys
from pathlib import Path

# Colores
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check(condition, message):
    """Helper para verificar condición"""
    if condition:
        print(f"{GREEN}✓{RESET} {message}")
        return True
    else:
        print(f"{RED}✗{RESET} {message}")
        return False

def main():
    print("=" * 60)
    print("🔍 VERIFICACIÓN FASE 4: CLOUD STORAGE")
    print("=" * 60)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # 1. Dependencia instalada
    total_checks += 1
    try:
        import google.cloud.storage
        checks_passed += check(True, "google-cloud-storage instalado")
    except ImportError:
        check(False, "google-cloud-storage NO instalado")
    
    # 2. Archivo storage.py existe
    total_checks += 1
    storage_path = Path('app/utils/storage.py')
    checks_passed += check(storage_path.exists(), f"Existe {storage_path}")
    
    # 3. Funciones definidas
    if storage_path.exists():
        content = storage_path.read_text()
        
        total_checks += 1
        checks_passed += check('def upload_file' in content, "Función upload_file() definida")
        
        total_checks += 1
        checks_passed += check('def delete_file' in content, "Función delete_file() definida")
        
        total_checks += 1
        checks_passed += check('def get_signed_url' in content, "Función get_signed_url() definida")
        
        total_checks += 1
        checks_passed += check('def list_files' in content, "Función list_files() definida")
    
    # 4. Controladores modificados
    ordenes_path = Path('app/controllers/ordenes_controller.py')
    if ordenes_path.exists():
        total_checks += 1
        content = ordenes_path.read_text()
        checks_passed += check(
            'from app.utils.storage import' in content,
            "ordenes_controller importa storage"
        )
        
        total_checks += 1
        checks_passed += check(
            'upload_file' in content,
            "ordenes_controller usa upload_file()"
        )
    
    manuales_path = Path('app/controllers/manuales_controller.py')
    if manuales_path.exists():
        total_checks += 1
        content = manuales_path.read_text()
        checks_passed += check(
            'from app.utils.storage import' in content,
            "manuales_controller importa storage"
        )
        
        total_checks += 1
        checks_passed += check(
            'upload_file' in content,
            "manuales_controller usa upload_file()"
        )
    
    # 5. .env.example actualizado
    total_checks += 1
    env_example = Path('.env.example')
    if env_example.exists():
        content = env_example.read_text()
        checks_passed += check(
            'GCS_BUCKET_NAME' in content,
            ".env.example contiene GCS_BUCKET_NAME"
        )
    
    # 6. requirements.txt actualizado
    total_checks += 1
    req_path = Path('requirements.txt')
    if req_path.exists():
        content = req_path.read_text()
        checks_passed += check(
            'google-cloud-storage' in content,
            "requirements.txt contiene google-cloud-storage"
        )
    
    # 7. Script de migración existe
    total_checks += 1
    migrate_script = Path('scripts/migrate_files_to_gcs.py')
    checks_passed += check(migrate_script.exists(), f"Existe {migrate_script}")
    
    # Resultado
    print()
    print("=" * 60)
    percentage = (checks_passed / total_checks * 100) if total_checks > 0 else 0
    
    if percentage == 100:
        print(f"{GREEN}✅ FASE 4 COMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}")
    elif percentage >= 80:
        print(f"{YELLOW}⚠️  FASE 4 CASI COMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}")
    else:
        print(f"{RED}❌ FASE 4 INCOMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}")
    
    print("=" * 60)
    
    return 0 if percentage == 100 else 1

if __name__ == '__main__':
    sys.exit(main())
```

---

### **9. Configuración GCP (Consola)** ⏱️ 20 min

**Pasos en Google Cloud Console:**

#### **9.1 Crear Bucket**
```bash
# Opción A: Consola web
# https://console.cloud.google.com/storage
# > Create Bucket > "gmao-uploads"

# Opción B: CLI
gcloud storage buckets create gs://gmao-uploads \
    --project=TU_PROYECTO \
    --location=us-central1 \
    --uniform-bucket-level-access
```

**Configuración recomendada:**
- **Name:** `gmao-uploads` (debe coincidir con GCS_BUCKET_NAME)
- **Location:** `us-central1` (misma región que App Engine)
- **Storage class:** Standard
- **Access control:** Uniform
- **Public access:** NO (usar URLs firmadas)

#### **9.2 Configurar Permisos**

```bash
# Dar permisos al service account de App Engine
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud storage buckets add-iam-policy-binding gs://gmao-uploads \
    --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

#### **9.3 Configurar Lifecycle Policy (opcional)**

**Archivo:** `bucket-lifecycle.json`
```json
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
```

```bash
gcloud storage buckets update gs://gmao-uploads \
    --lifecycle-file=bucket-lifecycle.json
```

#### **9.4 Configurar CORS (si es necesario)**

**Archivo:** `cors.json`
```json
[
  {
    "origin": ["https://tu-app.appspot.com"],
    "method": ["GET", "POST", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```

```bash
gcloud storage buckets update gs://gmao-uploads \
    --cors-file=cors.json
```

---

### **10. Testing** ⏱️ 30 min

**Archivo:** `scripts/test_storage.py` (NUEVO)

```python
"""
Test de funcionalidad de Cloud Storage
"""
import os
import sys
from pathlib import Path
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent.parent))

from werkzeug.datastructures import FileStorage
from app import create_app
from app.utils.storage import upload_file, delete_file, get_signed_url, list_files

def test_upload():
    """Test de subida de archivo"""
    print("🧪 Test: upload_file()")
    
    # Crear archivo fake
    file_content = b"Test file content"
    file = FileStorage(
        stream=BytesIO(file_content),
        filename="test.txt",
        content_type="text/plain"
    )
    
    # Subir
    url = upload_file(file, 'ordenes', 'test_upload.txt')
    
    if url:
        print(f"✅ Archivo subido: {url}")
        return 'test_upload.txt'
    else:
        print("❌ Error subiendo archivo")
        return None

def test_list():
    """Test de listado"""
    print("\n🧪 Test: list_files()")
    
    files = list_files('ordenes')
    print(f"✅ Archivos encontrados: {len(files)}")
    for f in files[:5]:  # Primeros 5
        print(f"   - {f}")
    
    return len(files) > 0

def test_signed_url(filename):
    """Test de URL firmada"""
    print("\n🧪 Test: get_signed_url()")
    
    url = get_signed_url(filename, 'ordenes')
    print(f"✅ URL generada: {url[:100]}...")
    
    return url is not None

def test_delete(filename):
    """Test de eliminación"""
    print("\n🧪 Test: delete_file()")
    
    success = delete_file(filename, 'ordenes')
    
    if success:
        print(f"✅ Archivo eliminado: {filename}")
    else:
        print(f"❌ Error eliminando: {filename}")
    
    return success

def main():
    print("=" * 60)
    print("🧪 TEST DE CLOUD STORAGE")
    print("=" * 60)
    print()
    
    app = create_app()
    with app.app_context():
        # Test completo
        filename = test_upload()
        if filename:
            test_list()
            test_signed_url(filename)
            test_delete(filename)
        
        print("\n" + "=" * 60)
        print("✅ TESTS COMPLETADOS")
        print("=" * 60)

if __name__ == '__main__':
    main()
```

**Ejecutar:**
```bash
python scripts/test_storage.py
```

---

## 📊 Checklist de Implementación

### **Código:**
- [ ] Instalar `google-cloud-storage`
- [ ] Crear `app/utils/storage.py`
- [ ] Modificar `app/controllers/ordenes_controller.py`
- [ ] Modificar `app/controllers/manuales_controller.py`
- [ ] Actualizar `.env.example`
- [ ] Actualizar `requirements.txt`

### **Scripts:**
- [ ] Crear `scripts/migrate_files_to_gcs.py`
- [ ] Crear `scripts/verify_fase4.py`
- [ ] Crear `scripts/test_storage.py`

### **GCP:**
- [ ] Crear bucket `gmao-uploads`
- [ ] Configurar permisos IAM
- [ ] (Opcional) Configurar lifecycle policy
- [ ] (Opcional) Configurar CORS

### **Testing:**
- [ ] Ejecutar `scripts/test_storage.py`
- [ ] Ejecutar `scripts/verify_fase4.py`
- [ ] Probar upload en desarrollo (local)
- [ ] Migrar archivos existentes

### **Deploy:**
- [ ] Crear/actualizar `app.yaml`
- [ ] Commit cambios
- [ ] Deploy a App Engine
- [ ] Verificar uploads en producción

---

## 🎯 Resultado Esperado

### **Antes de Fase 4:**
```
App Engine Deploy → Archivos perdidos 🔴
Usuario sube PDF → Guardado en /uploads/
Redeploy → PDF desaparecido ❌
```

### **Después de Fase 4:**
```
App Engine Deploy → Archivos persistentes ✅
Usuario sube PDF → Guardado en GCS
Redeploy → PDF sigue disponible ✅
Descarga → URL firmada (segura) 🔒
```

---

## ⏱️ Timeline

| Tarea | Tiempo | Acumulado |
|-------|--------|-----------|
| Instalar dependencias | 5 min | 5 min |
| Crear storage.py | 30 min | 35 min |
| Modificar ordenes_controller | 40 min | 1h 15min |
| Modificar manuales_controller | 40 min | 1h 55min |
| Actualizar configuración | 15 min | 2h 10min |
| Scripts (migración + verificación) | 50 min | 3h |
| Configurar GCP | 20 min | 3h 20min |
| Testing | 30 min | 3h 50min |
| **TOTAL** | **3h 50min** | |

---

## 🚀 Comenzar

**Comando para empezar:**
```bash
# 1. Instalar dependencia
pip install google-cloud-storage==2.18.2

# 2. Continuar con creación de archivos...
```

**¿Listo para comenzar? 🚀**
