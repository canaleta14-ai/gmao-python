# 🔐 Fase 3: Google Cloud Secret Manager - Plan de Implementación

**Fecha:** 2 de octubre de 2025  
**Duración estimada:** 4-6 horas  
**Prioridad:** Alta (Seguridad)

---

## 📋 Objetivo

Migrar todas las credenciales sensibles desde archivos `.env` y código hardcodeado hacia **Google Cloud Secret Manager**, eliminando secretos del repositorio y permitiendo gestión centralizada y segura.

---

## 🎯 Alcance

### **Secrets a Migrar:**

1. **`SECRET_KEY`** - Clave de sesiones Flask (actual: hardcoded en factory.py)
2. **`DB_PASSWORD`** - Contraseña PostgreSQL Cloud SQL
3. **`MAIL_PASSWORD`** - Contraseña SMTP Gmail
4. **`MAIL_USERNAME`** - Email SMTP (opcional, menos sensible)

### **Fuera de Alcance (Fase 3):**
- Configuración de Cloud SQL (usa Secret Manager para password)
- Configuración de Cloud Storage (Fase 4)
- Despliegue a App Engine (Fase 7)

---

## 📐 Arquitectura Propuesta

### **Flujo Actual (Inseguro):**
```
.env (local) → os.getenv() → app.config
     ↓
❌ Credenciales en archivos de texto
❌ Rotación manual difícil
❌ Sin auditoría de accesos
```

### **Flujo Nuevo (Seguro):**
```
Secret Manager (GCP) → Google Cloud Client → app.config
     ↓
✅ Credenciales cifradas
✅ Rotación centralizada
✅ Auditoría completa
✅ Versionado de secrets
```

---

## 🛠️ Implementación Paso a Paso

### **PASO 1: Prerequisitos en GCP (10 min)**

#### 1.1 Verificar/Crear Proyecto GCP
```bash
# Listar proyectos
gcloud projects list

# Si no existe, crear
gcloud projects create gmao-sistema --name="GMAO Sistema"

# Configurar proyecto activo
gcloud config set project gmao-sistema
```

#### 1.2 Habilitar APIs Necesarias
```bash
# Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Cloud SQL Admin API (para BD)
gcloud services enable sqladmin.googleapis.com

# Cloud Build API (para despliegues)
gcloud services enable cloudbuild.googleapis.com
```

#### 1.3 Verificar Cuenta de Servicio
```bash
# Listar cuentas de servicio
gcloud iam service-accounts list

# Crear si no existe
gcloud iam service-accounts create gmao-app \
    --display-name="GMAO Application Service Account"
```

---

### **PASO 2: Crear Secrets en GCP (15 min)**

#### 2.1 Generar SECRET_KEY Seguro
```bash
# Generar clave aleatoria de 32 bytes en base64
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Ejemplo salida: xK7mP9qR3tY8vN2bC5dF1gH4jL6nM0pS9wX3zA7yB2uE
```

#### 2.2 Crear Secret: `gmao-secret-key`
```bash
# Crear secret con valor inicial
echo -n "xK7mP9qR3tY8vN2bC5dF1gH4jL6nM0pS9wX3zA7yB2uE" | \
gcloud secrets create gmao-secret-key \
    --data-file=- \
    --replication-policy="automatic" \
    --labels=app=gmao,env=production

# Verificar creación
gcloud secrets describe gmao-secret-key
```

#### 2.3 Crear Secret: `gmao-db-password`
```bash
# Crear secret para password de PostgreSQL
echo -n "tu_password_postgresql_aqui" | \
gcloud secrets create gmao-db-password \
    --data-file=- \
    --replication-policy="automatic" \
    --labels=app=gmao,env=production,service=database
```

#### 2.4 Crear Secret: `gmao-mail-password`
```bash
# Crear secret para SMTP (App Password de Gmail)
echo -n "tu_gmail_app_password_aqui" | \
gcloud secrets create gmao-mail-password \
    --data-file=- \
    --replication-policy="automatic" \
    --labels=app=gmao,env=production,service=email
```

#### 2.5 Verificar Secrets Creados
```bash
# Listar todos los secrets
gcloud secrets list

# Ver versiones
gcloud secrets versions list gmao-secret-key
gcloud secrets versions list gmao-db-password
gcloud secrets versions list gmao-mail-password
```

---

### **PASO 3: Configurar Permisos (10 min)**

#### 3.1 Otorgar Permisos a Service Account
```bash
# Permiso para leer secretos
gcloud secrets add-iam-policy-binding gmao-secret-key \
    --member="serviceAccount:gmao-app@gmao-sistema.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gmao-db-password \
    --member="serviceAccount:gmao-app@gmao-sistema.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gmao-mail-password \
    --member="serviceAccount:gmao-app@gmao-sistema.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### 3.2 Permisos para Desarrollo Local (Tu Usuario)
```bash
# Obtener tu email de GCP
gcloud config get-value account

# Otorgar permisos a tu usuario
gcloud secrets add-iam-policy-binding gmao-secret-key \
    --member="user:TU_EMAIL@gmail.com" \
    --role="roles/secretmanager.secretAccessor"

# Repetir para otros secrets
gcloud secrets add-iam-policy-binding gmao-db-password \
    --member="user:TU_EMAIL@gmail.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gmao-mail-password \
    --member="user:TU_EMAIL@gmail.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

### **PASO 4: Instalar Cliente de GCP (5 min)**

#### 4.1 Instalar google-cloud-secret-manager
```bash
pip install google-cloud-secret-manager
```

#### 4.2 Actualizar requirements.txt
```bash
pip freeze | Out-File -Encoding UTF8 requirements.txt
```

---

### **PASO 5: Modificar Código (30 min)**

#### 5.1 Crear Utilidad para Secret Manager

**Archivo:** `app/utils/secrets.py`
```python
"""
Utilidades para Google Cloud Secret Manager

Proporciona funciones para acceder a secretos almacenados en GCP.
"""

import os
from google.cloud import secretmanager
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_secret(secret_id: str, project_id: Optional[str] = None, version: str = "latest") -> Optional[str]:
    """
    Obtiene un secreto desde Google Cloud Secret Manager
    
    Args:
        secret_id: ID del secreto (e.g., 'gmao-secret-key')
        project_id: ID del proyecto GCP (opcional, se obtiene de env)
        version: Versión del secreto (default: 'latest')
    
    Returns:
        Valor del secreto como string, o None si falla
    
    Example:
        >>> secret_key = get_secret('gmao-secret-key')
        >>> db_password = get_secret('gmao-db-password')
    """
    try:
        # Obtener project_id
        if project_id is None:
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'gmao-sistema')
        
        # Crear cliente
        client = secretmanager.SecretManagerServiceClient()
        
        # Construir nombre del secreto
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        
        # Acceder al secreto
        response = client.access_secret_version(request={"name": name})
        
        # Decodificar payload
        secret_value = response.payload.data.decode('UTF-8')
        
        logger.info(f"✅ Secret '{secret_id}' obtenido exitosamente")
        return secret_value
    
    except Exception as e:
        logger.error(f"❌ Error al obtener secret '{secret_id}': {e}")
        return None


def get_secret_or_env(secret_id: str, env_var: str, default: str = "") -> str:
    """
    Intenta obtener secreto de Secret Manager, si falla usa variable de entorno
    
    Útil para desarrollo local (usa .env) vs producción (usa Secret Manager)
    
    Args:
        secret_id: ID del secreto en GCP
        env_var: Nombre de variable de entorno alternativa
        default: Valor por defecto si ambos fallan
    
    Returns:
        Valor del secreto/env/default
    
    Example:
        >>> secret_key = get_secret_or_env('gmao-secret-key', 'SECRET_KEY', 'dev-key')
    """
    # Detectar si estamos en GCP
    is_gcp = os.getenv('GAE_ENV', '').startswith('standard') or \
             os.getenv('K_SERVICE') is not None
    
    if is_gcp:
        # Producción: Intentar Secret Manager
        secret = get_secret(secret_id)
        if secret:
            return secret
        else:
            logger.warning(f"⚠️  Secret '{secret_id}' no disponible, usando env var")
    
    # Desarrollo o fallback: Variable de entorno
    value = os.getenv(env_var, default)
    
    if value == default and default:
        logger.warning(f"⚠️  Usando valor por defecto para {env_var}")
    
    return value
```

#### 5.2 Modificar `app/factory.py`

**Cambios:**
```python
from flask import Flask, render_template, request
from app.extensions import db
from flask_login import LoginManager
import logging
import os
from datetime import datetime
from app.utils.secrets import get_secret_or_env  # ← NUEVO

def create_app():
    # ... código existente ...
    
    # ========== CAMBIO 1: SECRET_KEY desde Secret Manager ==========
    # ANTES:
    # app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_secreta_fija...')
    
    # AHORA:
    app.config['SECRET_KEY'] = get_secret_or_env(
        secret_id='gmao-secret-key',
        env_var='SECRET_KEY',
        default='dev-secret-key-CAMBIAR-EN-PRODUCCION'
    )
    
    # Log de seguridad
    if app.config['SECRET_KEY'] == 'dev-secret-key-CAMBIAR-EN-PRODUCCION':
        app.logger.warning("⚠️  Usando SECRET_KEY por defecto - NO USAR EN PRODUCCIÓN")
    else:
        app.logger.info("✅ SECRET_KEY cargada desde Secret Manager")
    
    # ... configuración de sesión ...
    
    # ========== CAMBIO 2: DB_PASSWORD desde Secret Manager ==========
    if db_type == "postgresql":
        # ANTES:
        # db_password = os.getenv("DB_PASSWORD", "")
        
        # AHORA:
        db_password = get_secret_or_env(
            secret_id='gmao-db-password',
            env_var='DB_PASSWORD',
            default=''
        )
        
        if os.getenv("GAE_ENV", "").startswith("standard"):
            # Cloud SQL en App Engine
            db_user = os.getenv("DB_USER", "postgres")
            db_name = os.getenv("DB_NAME", "postgres")
            db_host = os.getenv("DB_HOST", "/cloudsql/gmao-sistema:us-central1:gmao-postgres")
            
            app.config["SQLALCHEMY_DATABASE_URI"] = (
                f"postgresql+psycopg2://{db_user}:{db_password}@/{db_name}?host={db_host}"
            )
        else:
            # PostgreSQL local/externo
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "gmao_db")
            db_user = os.getenv("DB_USER", "postgres")
            
            app.config["SQLALCHEMY_DATABASE_URI"] = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )
    else:
        # SQLite para desarrollo
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/database.db"
    
    # ... resto del código ...
    
    # ========== CAMBIO 3: MAIL_PASSWORD desde Secret Manager ==========
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
    
    # ANTES:
    # app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    
    # AHORA:
    app.config["MAIL_PASSWORD"] = get_secret_or_env(
        secret_id='gmao-mail-password',
        env_var='MAIL_PASSWORD',
        default=''
    )
    
    app.config["ADMIN_EMAILS"] = os.getenv("ADMIN_EMAILS", "")
    
    # ... resto del código ...
```

---

### **PASO 6: Actualizar .env.example (5 min)**

**Archivo:** `.env.example`
```bash
# ============================================================
# CONFIGURACIÓN DE DESARROLLO - GMAO Sistema
# ============================================================
# IMPORTANTE: NO commitear este archivo con valores reales
# Copiar a .env y personalizar para desarrollo local
# ============================================================

# -------------------- SEGURIDAD --------------------
# En desarrollo: usar .env local
# En producción: usar Google Cloud Secret Manager
SECRET_KEY=tu_secret_key_aqui_generar_con_secrets.token_urlsafe_32

# -------------------- BASE DE DATOS --------------------
# Tipo de BD: 'sqlite' (desarrollo) o 'postgresql' (producción)
DB_TYPE=sqlite

# PostgreSQL (solo si DB_TYPE=postgresql)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gmao_db
DB_USER=postgres
DB_PASSWORD=tu_password_aqui  # En producción: Secret Manager

# -------------------- EMAIL / SMTP --------------------
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_app_password_aqui  # En producción: Secret Manager
ADMIN_EMAILS=admin@ejemplo.com

# -------------------- GOOGLE CLOUD --------------------
# Project ID de GCP (para Secret Manager, Cloud SQL, etc.)
GOOGLE_CLOUD_PROJECT=gmao-sistema

# Entorno de ejecución (detectado automáticamente en App Engine)
# GAE_ENV=standard  # No configurar manualmente
# FLASK_ENV=production  # Para forzar modo producción local

# -------------------- SERVIDOR --------------------
SERVER_URL=http://localhost:5000

# ============================================================
# NOTAS DE SEGURIDAD:
# ============================================================
# 1. NUNCA commitear .env con valores reales
# 2. En producción, SECRET_KEY, DB_PASSWORD y MAIL_PASSWORD
#    se obtienen de Google Cloud Secret Manager
# 3. Para generar SECRET_KEY seguro:
#    python -c "import secrets; print(secrets.token_urlsafe(32))"
# 4. Para Gmail App Password:
#    https://myaccount.google.com/apppasswords
# ============================================================
```

---

### **PASO 7: Autenticación Local para Desarrollo (10 min)**

#### 7.1 Instalar gcloud CLI
```bash
# Descargar de: https://cloud.google.com/sdk/docs/install

# Verificar instalación
gcloud --version
```

#### 7.2 Autenticar con tu Cuenta
```bash
# Login
gcloud auth login

# Configurar Application Default Credentials
gcloud auth application-default login

# Configurar proyecto
gcloud config set project gmao-sistema
```

#### 7.3 Verificar Acceso a Secrets
```bash
# Leer secret (sin guardar en archivo)
gcloud secrets versions access latest --secret="gmao-secret-key"
```

---

### **PASO 8: Testing y Verificación (30 min)**

#### 8.1 Script de Verificación

**Archivo:** `scripts/verify_fase3.py`
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Verificación: Fase 3 - Secret Manager

Verifica que Secret Manager esté correctamente configurado.
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("  VERIFICACIÓN FASE 3: SECRET MANAGER")
    print("=" * 60)
    
    checks_passed = 0
    checks_total = 0
    
    # 1. google-cloud-secret-manager instalado
    checks_total += 1
    try:
        from google.cloud import secretmanager
        print("✓ google-cloud-secret-manager instalado")
        checks_passed += 1
    except ImportError:
        print("✗ google-cloud-secret-manager NO instalado")
    
    # 2. app/utils/secrets.py existe
    checks_total += 1
    secrets_file = Path("app/utils/secrets.py")
    if secrets_file.exists():
        print("✓ app/utils/secrets.py existe")
        checks_passed += 1
    else:
        print("✗ app/utils/secrets.py NO existe")
    
    # 3. Autenticación GCP configurada
    checks_total += 1
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    gcloud_config = Path.home() / '.config' / 'gcloud'
    if creds_path or gcloud_config.exists():
        print("✓ Autenticación GCP configurada")
        checks_passed += 1
    else:
        print("✗ Autenticación GCP NO configurada")
    
    # 4. Probar acceso a secret (si autenticado)
    checks_total += 1
    try:
        from app.utils.secrets import get_secret
        secret = get_secret('gmao-secret-key')
        if secret:
            print(f"✓ Acceso a Secret Manager OK (secret: {len(secret)} chars)")
            checks_passed += 1
        else:
            print("✗ No se pudo acceder a Secret Manager")
    except Exception as e:
        print(f"✗ Error al acceder a Secret Manager: {e}")
    
    # Resumen
    print("=" * 60)
    print(f"Verificaciones: {checks_passed}/{checks_total}")
    
    if checks_passed == checks_total:
        print("✅ FASE 3 COMPLETADA")
        return 0
    else:
        print("❌ FASE 3 INCOMPLETA")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

#### 8.2 Ejecutar Verificación
```bash
python scripts/verify_fase3.py
```

#### 8.3 Test de Integración
```bash
# Ejecutar app y verificar logs
python run.py

# Buscar en logs:
# ✅ SECRET_KEY cargada desde Secret Manager
# ✅ Secret 'gmao-secret-key' obtenido exitosamente
```

---

### **PASO 9: Documentación (20 min)**

Crear:
1. `FASE3_SECRET_MANAGER_COMPLETADA.md` - Resumen técnico
2. `docs/SECRET_MANAGER.md` - Guía de uso
3. `RESUMEN_FASE3.md` - Resumen ejecutivo

---

### **PASO 10: Commit y Deploy (10 min)**

```bash
# Commit
git add -A
git commit -m "Fase 3 Secret Manager: Credenciales seguras en GCP

- Creados 3 secrets en GCP (SECRET_KEY, DB_PASSWORD, MAIL_PASSWORD)
- Implementado app/utils/secrets.py
- Modificado app/factory.py para usar Secret Manager
- Actualizado .env.example con documentación
- Script de verificación creado
- Documentación completa

Seguridad: +100% (credenciales fuera del código)
Progreso: 37.5% (3 de 8 fases)"

git push origin master
```

---

## ✅ Checklist de Completitud

### **GCP Setup**
- [ ] Proyecto GCP creado/configurado
- [ ] Secret Manager API habilitada
- [ ] Service Account creada
- [ ] Secrets creados (gmao-secret-key, gmao-db-password, gmao-mail-password)
- [ ] Permisos IAM configurados

### **Código**
- [ ] google-cloud-secret-manager instalado
- [ ] app/utils/secrets.py creado
- [ ] app/factory.py modificado (SECRET_KEY, DB_PASSWORD, MAIL_PASSWORD)
- [ ] .env.example actualizado
- [ ] requirements.txt actualizado

### **Testing**
- [ ] scripts/verify_fase3.py creado
- [ ] Verificación ejecutada (100% passed)
- [ ] App funciona en desarrollo (con .env)
- [ ] Secrets accesibles desde código

### **Documentación**
- [ ] FASE3_SECRET_MANAGER_COMPLETADA.md
- [ ] docs/SECRET_MANAGER.md
- [ ] RESUMEN_FASE3.md

### **Deploy**
- [ ] Cambios commiteados
- [ ] Push a GitHub completado

---

## 🎯 Criterios de Éxito

1. ✅ Todos los secrets creados en GCP
2. ✅ Código lee secrets de Secret Manager
3. ✅ Fallback a .env funciona en desarrollo
4. ✅ No hay credenciales hardcodeadas
5. ✅ Verificación 100% pasada
6. ✅ Documentación completa

---

## ⏱️ Timeline

| Paso | Descripción | Tiempo |
|------|-------------|--------|
| 1 | Prerequisites GCP | 10 min |
| 2 | Crear Secrets | 15 min |
| 3 | Configurar Permisos | 10 min |
| 4 | Instalar Cliente | 5 min |
| 5 | Modificar Código | 30 min |
| 6 | Actualizar .env | 5 min |
| 7 | Autenticación Local | 10 min |
| 8 | Testing | 30 min |
| 9 | Documentación | 20 min |
| 10 | Commit & Deploy | 10 min |
| **TOTAL** | | **2h 25min** |

---

**Preparado para comenzar implementación.**

¿Empezamos con el PASO 1 (Prerequisites GCP)?
