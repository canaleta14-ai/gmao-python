# 📘 Guía Completa de Migraciones de Base de Datos

**Sistema GMAO - Flask-Migrate**

---

## 📚 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Conceptos Básicos](#conceptos-básicos)
3. [Comandos Esenciales](#comandos-esenciales)
4. [Flujos de Trabajo](#flujos-de-trabajo)
5. [Casos de Uso Reales](#casos-de-uso-reales)
6. [Troubleshooting](#troubleshooting)
7. [Mejores Prácticas](#mejores-prácticas)
8. [FAQ](#faq)

---

## 🎓 Introducción

### ¿Qué son las Migraciones?

Las **migraciones de base de datos** son cambios versionados en la estructura de tu base de datos (esquema). Piensa en ellas como "commits de Git" pero para tu base de datos.

### ¿Por qué usarlas?

**ANTES (Sin Migraciones):**
```sql
-- Cambio manual riesgoso
ALTER TABLE activos ADD COLUMN ubicacion VARCHAR(200);
-- ¿Quién lo aplicó? ¿Cuándo? ¿En qué servidor? 🤷
```

**AHORA (Con Migraciones):**
```python
# Cambio versionado y seguro
flask db migrate -m "Agregar ubicacion a activos"
flask db upgrade
# ✅ Registrado, versionado, reversible
```

---

## 🧠 Conceptos Básicos

### Terminología

- **Migración**: Archivo Python que describe cambios en la BD
- **Upgrade**: Aplicar cambios (forward migration)
- **Downgrade**: Revertir cambios (rollback)
- **Head**: Última versión disponible
- **Current**: Versión actualmente aplicada
- **Alembic**: Motor subyacente de migraciones
- **Stamp**: Marcar BD sin aplicar cambios

### Anatomía de una Migración

```python
# migrations/versions/abc123_agregar_ubicacion.py

"""Agregar ubicacion a activos

Revision ID: abc123
Revises: def456
Create Date: 2025-10-02 07:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'def456'  # Migración anterior
branch_labels = None
depends_on = None

def upgrade():
    """Cambios a aplicar (forward)"""
    op.add_column('activo', 
        sa.Column('ubicacion', sa.String(200), nullable=True))

def downgrade():
    """Cómo revertir (backward)"""
    op.drop_column('activo', 'ubicacion')
```

---

## 🛠️ Comandos Esenciales

### 1️⃣ Crear Migración

```bash
# Detecta cambios automáticamente
flask db migrate -m "Descripción del cambio"

# Ejemplos:
flask db migrate -m "Agregar campo urgente a ordenes"
flask db migrate -m "Crear tabla historial_cambios"
flask db migrate -m "Modificar tipo de dato en costo_total"
```

**Salida:**
```
INFO [alembic.runtime.migration] Generating migrations/versions/abc123_agregar_campo.py
  done
```

### 2️⃣ Aplicar Migraciones

```bash
# Aplicar todas las pendientes
flask db upgrade

# Aplicar hasta versión específica
flask db upgrade abc123

# Ver qué haría sin aplicar (dry-run)
flask db upgrade --sql > preview.sql
```

### 3️⃣ Revertir Cambios

```bash
# Rollback 1 migración
flask db downgrade -1

# Rollback 3 migraciones
flask db downgrade -3

# Rollback a versión específica
flask db downgrade def456

# Rollback total (⚠️ CUIDADO)
flask db downgrade base
```

### 4️⃣ Ver Estado

```bash
# Historial completo
flask db history

# Versión actual
flask db current

# Detalles de migración específica
flask db show abc123

# Migraciones pendientes
flask db heads
```

### 5️⃣ Comandos Avanzados

```bash
# Marcar BD sin aplicar cambios
flask db stamp head

# Merge de branches (raro, pero útil)
flask db merge abc123 def456

# Editar migración existente
flask db edit abc123
```

---

## 🔄 Flujos de Trabajo

### Flujo 1: Agregar Campo Simple

**Paso 1: Modificar Modelo**
```python
# app/models/activo.py
class Activo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    ubicacion = db.Column(db.String(200))  # ← NUEVO
```

**Paso 2: Crear Migración**
```bash
flask db migrate -m "Agregar ubicacion a activos"
```

**Paso 3: Revisar Migración**
```bash
cat migrations/versions/abc123_agregar_ubicacion.py
# Verificar que upgrade() y downgrade() sean correctos
```

**Paso 4: Aplicar**
```bash
flask db upgrade
```

**Paso 5: Verificar**
```bash
flask db current
# Debe mostrar abc123
```

**Paso 6: Commit**
```bash
git add app/models/activo.py migrations/versions/abc123_*.py
git commit -m "Agregar campo ubicacion a activos"
git push
```

---

### Flujo 2: Crear Nueva Tabla

**Paso 1: Crear Modelo**
```python
# app/models/historial.py
from app.extensions import db
from datetime import datetime

class HistorialCambios(db.Model):
    __tablename__ = 'historial_cambios'
    
    id = db.Column(db.Integer, primary_key=True)
    tabla = db.Column(db.String(50), nullable=False)
    registro_id = db.Column(db.Integer, nullable=False)
    campo = db.Column(db.String(50), nullable=False)
    valor_anterior = db.Column(db.Text)
    valor_nuevo = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
```

**Paso 2: Registrar en __init__.py**
```python
# app/models/__init__.py
from app.models.historial import HistorialCambios  # Importar
```

**Paso 3: Migrar**
```bash
flask db migrate -m "Crear tabla historial_cambios"
flask db upgrade
```

---

### Flujo 3: Modificar Tipo de Columna

**⚠️ MUY IMPORTANTE**: Cambios de tipo pueden requerir conversión de datos.

**Paso 1: Cambiar Modelo**
```python
# app/models/orden_trabajo.py
class OrdenTrabajo(db.Model):
    # ANTES: costo_total = db.Column(db.Float)
    costo_total = db.Column(db.Numeric(12, 2))  # AHORA
```

**Paso 2: Crear Migración**
```bash
flask db migrate -m "Cambiar costo_total de Float a Numeric"
```

**Paso 3: REVISAR Y EDITAR Migración**
```python
# migrations/versions/xyz789_cambiar_costo.py

def upgrade():
    # Auto-generado puede no ser suficiente
    op.alter_column('orden_trabajo', 'costo_total',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(12, 2),
                    postgresql_using='costo_total::numeric(12,2)')  # PostgreSQL
    
def downgrade():
    op.alter_column('orden_trabajo', 'costo_total',
                    existing_type=sa.Numeric(12, 2),
                    type_=sa.Float())
```

**Paso 4: Testear en Desarrollo PRIMERO**
```bash
# Backup
cp instance/database.db instance/database.db.backup

# Aplicar
flask db upgrade

# Verificar datos
python
>>> from app.models.orden_trabajo import OrdenTrabajo
>>> OrdenTrabajo.query.first().costo_total
Decimal('1234.56')  # ✅ OK
```

**Paso 5: Si OK, aplicar en producción**

---

### Flujo 4: Eliminar Columna (⚠️ PELIGROSO)

**Paso 1: BACKUP PRIMERO**
```bash
# SQLite
cp instance/database.db instance/database.db.$(date +%Y%m%d_%H%M%S)

# PostgreSQL
pg_dump -h localhost -U postgres gmao_db > backup_$(date +%Y%m%d).sql
```

**Paso 2: Eliminar del Modelo**
```python
# app/models/proveedor.py
class Proveedor(db.Model):
    # campo_antiguo = db.Column(db.String(100))  # ELIMINADO
    pass
```

**Paso 3: Migrar**
```bash
flask db migrate -m "Eliminar campo_antiguo de proveedores"
```

**Paso 4: REVISAR Migración**
```python
def upgrade():
    op.drop_column('proveedor', 'campo_antiguo')
    # ⚠️ ESTO BORRARÁ DATOS PERMANENTEMENTE

def downgrade():
    op.add_column('proveedor', 
        sa.Column('campo_antiguo', sa.String(100)))
    # ⚠️ Datos no se recuperarán
```

**Paso 5: Confirmar con Usuario**
```
¿Seguro que deseas eliminar 'campo_antiguo'?
- Se perderán todos los datos
- Downgrade NO restaurará datos
[y/N]: 
```

**Paso 6: Aplicar si confirmado**
```bash
flask db upgrade
```

---

## 💼 Casos de Uso Reales

### Caso 1: Agregar Índice para Performance

**Problema:** Consultas lentas en `ordenes_trabajo` filtradas por `estado`.

**Solución:**
```python
# Migración manual
flask db revision -m "Agregar indice a ordenes.estado"

# Editar archivo generado
def upgrade():
    op.create_index('idx_ordenes_estado', 'orden_trabajo', ['estado'])

def downgrade():
    op.drop_index('idx_ordenes_estado', 'orden_trabajo')
```

```bash
flask db upgrade
# ✅ Consultas 10x más rápidas
```

---

### Caso 2: Agregar Restricción Unique

**Problema:** Activos duplicados con mismo `codigo_interno`.

**Solución:**
```python
# 1. Limpiar duplicados primero
python
>>> from app.models.activo import Activo
>>> # Identificar y fusionar duplicados
>>> # (código de limpieza aquí)

# 2. Crear migración
flask db migrate -m "Agregar unique constraint a activo.codigo_interno"

# 3. Revisar y editar si necesario
def upgrade():
    op.create_unique_constraint('uq_activo_codigo', 
                                'activo', ['codigo_interno'])

# 4. Aplicar
flask db upgrade
```

---

### Caso 3: Renombrar Tabla

**Problema:** Nombre de tabla inconsistente.

**Solución:**
```python
# Crear migración manual
flask db revision -m "Renombrar tabla orden_trabajos a ordenes_trabajo"

def upgrade():
    op.rename_table('orden_trabajos', 'ordenes_trabajo')
    
def downgrade():
    op.rename_table('ordenes_trabajo', 'orden_trabajos')
```

---

### Caso 4: Migración de Datos

**Problema:** Cambiar formato de campo `telefono` de `123456789` a `+34-123-45-67-89`.

**Solución:**
```python
flask db revision -m "Reformatear campo telefono"

def upgrade():
    # 1. Agregar columna temporal
    op.add_column('proveedor', 
        sa.Column('telefono_nuevo', sa.String(20)))
    
    # 2. Migrar datos
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE proveedor 
        SET telefono_nuevo = CONCAT('+34-', 
            SUBSTR(telefono, 1, 3), '-',
            SUBSTR(telefono, 4, 2), '-',
            SUBSTR(telefono, 6, 2), '-',
            SUBSTR(telefono, 8, 2))
        WHERE telefono IS NOT NULL
    """))
    
    # 3. Eliminar columna vieja
    op.drop_column('proveedor', 'telefono')
    
    # 4. Renombrar nueva
    op.alter_column('proveedor', 'telefono_nuevo', 
                    new_column_name='telefono')

def downgrade():
    # Reverso (simplificado)
    op.alter_column('proveedor', 'telefono',
                    new_column_name='telefono_nuevo')
    op.add_column('proveedor', 
        sa.Column('telefono', sa.String(15)))
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE proveedor 
        SET telefono = REPLACE(REPLACE(telefono_nuevo, '+34-', ''), '-', '')
    """))
    op.drop_column('proveedor', 'telefono_nuevo')
```

---

## 🚨 Troubleshooting

### Error: "Target database is not up to date"

**Causa:** BD en versión diferente a migraciones.

**Solución:**
```bash
# Ver estado
flask db current
flask db heads

# Sincronizar
flask db upgrade  # Si BD está atrás
flask db downgrade abc123  # Si BD está adelante
```

---

### Error: "Can't locate revision identified by 'abc123'"

**Causa:** Falta archivo de migración.

**Solución:**
```bash
# Opción 1: Recuperar de Git
git checkout migrations/versions/abc123_*.py

# Opción 2: Stamp a versión anterior
flask db stamp def456  # Versión anterior que sí existe
```

---

### Error: "FOREIGN KEY constraint failed"

**Causa:** Intentando eliminar tabla con dependencias.

**Solución:**
```python
# Eliminar en orden correcto
def upgrade():
    # 1. Eliminar FK primero
    op.drop_constraint('fk_orden_activo', 'orden_trabajo')
    # 2. Ahora sí eliminar tabla
    op.drop_table('activo_viejo')
```

---

### Error: "Column already exists"

**Causa:** Migración aplicada parcialmente.

**Solución:**
```bash
# Opción 1: Downgrade y re-upgrade
flask db downgrade -1
flask db upgrade

# Opción 2: Editar migración para skip si existe
def upgrade():
    try:
        op.add_column('activo', sa.Column('ubicacion', sa.String(200)))
    except Exception as e:
        if 'already exists' not in str(e):
            raise
```

---

## ✅ Mejores Prácticas

### 1. **Siempre Revisar Migraciones Generadas**

```bash
# NO hacer ciegamente
flask db migrate -m "cambios"
flask db upgrade  # ❌ PELIGROSO

# SÍ hacer
flask db migrate -m "cambios"
cat migrations/versions/abc123_*.py  # ✅ REVISAR
# Verificar que upgrade/downgrade sean correctos
flask db upgrade
```

### 2. **Usar Nombres Descriptivos**

```bash
# ❌ MAL
flask db migrate -m "fix"
flask db migrate -m "update"
flask db migrate -m "cambios"

# ✅ BIEN
flask db migrate -m "Agregar campo urgente a ordenes"
flask db migrate -m "Crear indice en activos.codigo_interno"
flask db migrate -m "Modificar tipo de costo_total a Decimal"
```

### 3. **Testear en Desarrollo Primero**

```bash
# Flujo seguro
# 1. Desarrollo
flask db upgrade
python -m pytest tests/
# Si pasa → Continuar

# 2. Staging
flask db upgrade
./run_integration_tests.sh
# Si pasa → Continuar

# 3. Producción
flask db upgrade
```

### 4. **Backup Antes de Migraciones en Prod**

```bash
# Script de deploy seguro
#!/bin/bash
set -e

# 1. Backup
pg_dump gmao_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Migrar
flask db upgrade

# 3. Verificar
python scripts/verify_db_health.py

# 4. Si falla, rollback
if [ $? -ne 0 ]; then
    flask db downgrade -1
    echo "❌ Migración falló, rollback aplicado"
    exit 1
fi

echo "✅ Migración exitosa"
```

### 5. **Commitear Migraciones con Código**

```bash
# ❌ MAL: Commits separados
git commit -m "Cambiar modelo Activo"
git commit -m "Migración de BD"

# ✅ BIEN: Commit atómico
git add app/models/activo.py
git add migrations/versions/abc123_*.py
git commit -m "Agregar campo ubicacion a activos

- Modificar modelo Activo
- Crear migración abc123
- Tests actualizados"
```

### 6. **Documentar Migraciones Complejas**

```python
# migrations/versions/abc123_migration_compleja.py

"""
Migración compleja: Reestructurar tabla ordenes

IMPORTANTE:
- Esta migración toma ~5 minutos en BD grande
- Requiere downtime de 10 minutos
- Backup obligatorio antes de aplicar
- No usar en horario laboral

PASOS:
1. Crear tabla temporal
2. Migrar datos (puede ser lento)
3. Eliminar tabla vieja
4. Renombrar temporal

ROLLBACK:
- Posible solo si datos no modificados
- Tiempo de rollback: ~5 minutos
"""
```

---

## ❓ FAQ

### P: ¿Puedo editar una migración ya aplicada?

**R:** ❌ NO. Si ya está en producción, crea una nueva migración que corrija el problema.

```bash
# ❌ MAL
# Editar migrations/versions/abc123_*.py (ya aplicada)

# ✅ BIEN
flask db migrate -m "Corregir cambio anterior"
```

---

### P: ¿Qué hago si olvidé crear migración antes de commit?

**R:** Crear migración ahora y commitear juntas.

```bash
# 1. Crear migración
flask db migrate -m "Migración olvidada para cambios en X"

# 2. Commit juntas
git add migrations/versions/abc123_*.py
git commit -m "Agregar migración olvidada"
```

---

### P: ¿Cómo manejo migraciones en múltiples branches?

**R:** Merge de migraciones con `flask db merge`.

```bash
# Branch A crea abc123
# Branch B crea def456
# Al mergear código:

flask db merge abc123 def456 -m "Merge migraciones"
# Crea ghi789 que depende de ambas
```

---

### P: ¿Puedo usar migraciones en SQLite y PostgreSQL?

**R:** ✅ SÍ, pero cuidado con diferencias de sintaxis.

```python
# Migración compatible
def upgrade():
    op.add_column('activo', sa.Column('ubicacion', sa.String(200)))
    # ✅ Funciona en ambos

# Migración específica de PostgreSQL
def upgrade():
    # Solo PostgreSQL
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('CREATE INDEX CONCURRENTLY idx_activo_nombre ON activo(nombre)')
    else:
        op.create_index('idx_activo_nombre', 'activo', ['nombre'])
```

---

### P: ¿Cómo hago migraciones sin downtime?

**R:** Migraciones en fases.

```python
# FASE 1: Agregar columna nullable
def upgrade():
    op.add_column('activo', sa.Column('ubicacion_nueva', sa.String(200)))
# Deploy código compatible con ambas columnas

# FASE 2: Migrar datos
def upgrade():
    op.execute('UPDATE activo SET ubicacion_nueva = ubicacion WHERE ubicacion IS NOT NULL')
# Sin downtime, datos migrados

# FASE 3: Hacer NOT NULL y eliminar vieja
def upgrade():
    op.alter_column('activo', 'ubicacion_nueva', nullable=False)
    op.drop_column('activo', 'ubicacion')
    op.alter_column('activo', 'ubicacion_nueva', new_column_name='ubicacion')
```

---

## 📖 Referencias

- **Flask-Migrate Docs**: https://flask-migrate.readthedocs.io/
- **Alembic Tutorial**: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- **SQLAlchemy Core**: https://docs.sqlalchemy.org/en/20/core/
- **Zero-Downtime Migrations**: https://www.braintreepayments.com/blog/safe-operations-for-high-volume-postgresql/

---

**Última actualización:** 2 de octubre de 2025  
**Versión:** 1.0  
**Autor:** Sistema GMAO
