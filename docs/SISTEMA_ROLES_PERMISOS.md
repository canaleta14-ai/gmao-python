# 📋 SISTEMA DE ROLES Y PERMISOS - GMAO

## 🎭 ROLES DISPONIBLES EN EL SISTEMA

El sistema GMAO cuenta con **5 roles** principales que determinan los permisos y acceso de cada usuario:

### 1. **ADMINISTRADOR** 👑
- **Nombre en BD**: `"Administrador"` o `"administrador"`
- **Color Badge**: Rojo (danger)
- **Nivel de Acceso**: COMPLETO

#### Permisos del Administrador:
- ✅ **Acceso total** a todos los módulos del sistema
- ✅ **Gestión de usuarios**: Crear, editar, eliminar, activar/desactivar
- ✅ **Gestión de roles**: Asignar y cambiar roles de otros usuarios
- ✅ **Asignación masiva de técnicos** a órdenes de trabajo
- ✅ **Acceso a solicitudes de servicio**: Visualizar, editar, asignar
- ✅ **Acceso a estadísticas** y reportes administrativos
- ✅ **Gestión de proveedores**: CRUD completo
- ✅ **Gestión de inventario**: CRUD completo, incluyendo lotes FIFO
- ✅ **Gestión de órdenes de trabajo**: CRUD completo
- ✅ **Gestión de activos**: CRUD completo
- ✅ **Gestión de planes de mantenimiento**: CRUD completo
- ✅ **Exportación de datos** (Excel, CSV)
- ✅ **Acceso a endpoints de administración**:
  - `/admin/asignar-tecnicos`
  - `/admin/asignar-tecnicos-page`
  - `/admin/solicitudes/*`

#### Limitaciones del Administrador:
- ❌ **Ninguna** - Acceso sin restricciones

---

### 2. **SUPERVISOR** 👔
- **Nombre en BD**: `"Supervisor"`
- **Color Badge**: Amarillo/Naranja (warning)
- **Nivel de Acceso**: ALTO

#### Permisos del Supervisor:
- ✅ **Gestión de usuarios**: Solo lectura
- ✅ **Supervisión de equipos**: Ver técnicos y su carga de trabajo
- ✅ **Acceso a solicitudes de servicio**: Visualizar, editar (sin asignar)
- ✅ **Gestión de activos**: Lectura completa
- ✅ **Gestión de órdenes de trabajo**: Lectura y edición
- ✅ **Operaciones de inventario**: Lectura y edición
- ✅ **Reportes y estadísticas**: Acceso completo
- ✅ **Puede ser asignado** a órdenes de trabajo como técnico
- ✅ **Exportación de datos** limitada

#### Limitaciones del Supervisor:
- ❌ **NO puede crear/eliminar usuarios**
- ❌ **NO puede cambiar roles** de otros usuarios
- ❌ **NO puede asignar solicitudes** a técnicos (solo Administrador)
- ❌ **NO puede acceder** a endpoints exclusivos de admin
- ❌ **NO puede realizar asignación masiva** de técnicos
- ❌ **Acceso limitado** a funciones administrativas

---

### 3. **TÉCNICO** 🔧
- **Nombre en BD**: `"Técnico"` o `"tecnico"`
- **Color Badge**: Azul (primary)
- **Nivel de Acceso**: MEDIO

#### Permisos del Técnico:
- ✅ **Gestión de órdenes de trabajo**: Crear, leer, editar (asignadas a él)
- ✅ **Acceso a solicitudes de servicio**: Visualizar (solo lectura)
- ✅ **Gestión de mantenimiento**: Lectura y edición
- ✅ **Gestión de activos**: Lectura completa
- ✅ **Puede ser asignado** a órdenes de trabajo
- ✅ **Registro de actividades** en órdenes asignadas
- ✅ **Actualización de estado** de órdenes asignadas
- ✅ **Consulta de inventario**: Solo lectura
- ✅ **Planes de mantenimiento**: Puede ejecutar tareas asignadas

#### Limitaciones del Técnico:
- ❌ **NO puede acceder** a gestión de usuarios
- ❌ **NO puede crear/editar/eliminar usuarios**
- ❌ **NO puede cambiar roles**
- ❌ **NO puede asignar técnicos** a órdenes
- ❌ **NO puede acceder a solicitudes de servicio** (admin)
- ❌ **NO puede acceder** a estadísticas administrativas (403 Forbidden)
- ❌ **NO puede exportar datos** completos del sistema
- ❌ **NO puede gestionar proveedores**
- ❌ **NO puede gestionar inventario** (solo consulta)
- ❌ **Solo puede ver/editar** órdenes asignadas a él
- ❌ **NO puede acceder** a endpoints `/admin/*`

---

### 4. **ANALISTA** 📊
- **Nombre en BD**: `"Analista"`
- **Color Badge**: Cyan (info)
- **Nivel de Acceso**: MEDIO-BAJO

#### Permisos del Analista:
- ✅ **Acceso a reportes** y estadísticas
- ✅ **Consulta de órdenes**: Solo lectura
- ✅ **Consulta de activos**: Solo lectura
- ✅ **Consulta de inventario**: Solo lectura
- ✅ **Generación de reportes** personalizados
- ✅ **Exportación de datos** (Excel, CSV)
- ✅ **Consulta de indicadores** de rendimiento

#### Limitaciones del Analista:
- ❌ **NO puede crear/editar/eliminar** órdenes de trabajo
- ❌ **NO puede gestionar activos**
- ❌ **NO puede gestionar inventario**
- ❌ **NO puede gestionar usuarios**
- ❌ **NO puede ser asignado** a órdenes de trabajo
- ❌ **Solo acceso de consulta** (read-only) en la mayoría de módulos
- ❌ **NO puede acceder** a funciones administrativas

---

### 5. **OPERADOR** 🏭
- **Nombre en BD**: `"Operador"`
- **Color Badge**: Verde (success)
- **Nivel de Acceso**: BAJO

#### Permisos del Operador:
- ✅ **Consulta de órdenes**: Solo lectura
- ✅ **Consulta de activos**: Solo lectura
- ✅ **Registro de movimientos** de inventario (consumos)
- ✅ **Operaciones básicas** de inventario
- ✅ **Puede reportar** problemas/solicitudes de servicio

#### Limitaciones del Operador:
- ❌ **NO puede crear órdenes de trabajo**
- ❌ **NO puede editar órdenes**
- ❌ **NO puede gestionar activos**
- ❌ **NO puede gestionar usuarios**
- ❌ **NO puede acceder** a reportes administrativos
- ❌ **NO puede exportar datos** del sistema
- ❌ **Acceso muy limitado** - principalmente consulta

---

## 🔐 MATRIZ DE PERMISOS

| Módulo/Funcionalidad | Admin | Supervisor | Técnico | Analista | Operador |
|---------------------|:-----:|:----------:|:-------:|:--------:|:--------:|
| **Usuarios - Ver** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Usuarios - Crear/Editar** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Usuarios - Eliminar** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Usuarios - Cambiar Roles** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Órdenes - Ver Todas** | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Órdenes - Ver Propias** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Órdenes - Crear** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Órdenes - Editar** | ✅ | ✅ | ✅* | ❌ | ❌ |
| **Órdenes - Eliminar** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Órdenes - Asignar Técnico** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Activos - Ver** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Activos - Crear/Editar** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Activos - Eliminar** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Inventario - Ver** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Inventario - Gestionar** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Inventario - Movimientos** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Proveedores - Ver** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Proveedores - Gestionar** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Solicitudes - Ver** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Solicitudes - Editar** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Solicitudes - Asignar** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Estadísticas Admin** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Exportar Datos** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Endpoints /admin/** | ✅ | ❌ | ❌ | ❌ | ❌ |

**Nota**: ✅ = Permitido, ❌ = Denegado, ✅* = Permitido solo en sus propias órdenes

---

## 🛡️ IMPLEMENTACIÓN DE SEGURIDAD

### Decoradores de Seguridad

El sistema utiliza principalmente:

```python
@login_required  # Requiere estar autenticado
```

### Validación de Roles en Controladores

#### Ejemplo 1: Solo Administradores
```python
@solicitudes_admin_bp.route("/<int:id>/asignar", methods=["POST"])
@login_required
def asignar_solicitud(id):
    if current_user.rol != "Administrador":
        return jsonify({"error": "No autorizado"}), 403
    # ... código ...
```

#### Ejemplo 2: Múltiples Roles Permitidos
```python
@solicitudes_admin_bp.route("/", methods=["GET"])
@login_required
def listar_solicitudes():
    if current_user.rol not in ["Administrador", "Técnico", "Supervisor"]:
        flash("No tiene permisos para acceder a esta sección.", "error")
        return redirect(url_for("web.index"))
    # ... código ...
```

#### Ejemplo 3: Validación en Consultas
```python
def obtener_tecnicos_disponibles():
    tecnicos = (
        Usuario.query.filter_by(activo=True)
        .filter(Usuario.rol.in_(["Técnico", "Supervisor", "Administrador"]))
        .order_by(Usuario.nombre)
        .all()
    )
    return tecnicos
```

---

## 🔄 COMPATIBILIDAD DE ROLES

El sistema soporta **dos formatos** de roles para compatibilidad:

### Formato con Mayúsculas (Recomendado)
- `"Administrador"`
- `"Supervisor"`
- `"Técnico"`
- `"Analista"`
- `"Operador"`

### Formato en Minúsculas (Legacy)
- `"administrador"`
- `"supervisor"`
- `"tecnico"`
- `"analista"`
- `"operador"`

**Nota**: El sistema valida ambos formatos en la mayoría de las funciones para mantener compatibilidad.

---

## 📍 ENDPOINTS PROTEGIDOS POR ROL

### Solo Administrador:
```
POST /admin/asignar-tecnicos
GET  /admin/asignar-tecnicos-page
POST /admin/hacerme-admin
POST /admin/hacerme-tecnico
POST /admin/crear-tecnico-demo
POST /admin/solicitudes/<id>/asignar
```

### Administrador, Supervisor, Técnico:
```
GET  /admin/solicitudes/
GET  /admin/solicitudes/<id>
GET  /admin/solicitudes/<id>/editar (solo Admin y Supervisor pueden editar)
```

### Administrador y Supervisor:
```
GET  /admin/solicitudes/api/estadisticas
```

### Técnicos (solo órdenes asignadas):
```
GET  /ordenes/<id> (solo si tecnico_id == current_user.id)
PUT  /ordenes/<id> (solo si tecnico_id == current_user.id)
```

---

## 🎯 CASOS DE USO POR ROL

### Caso de Uso: Administrador
**Escenario**: Gestión completa del sistema GMAO

1. ✅ Crea nuevos usuarios (técnicos, supervisores, operadores)
2. ✅ Asigna roles a usuarios existentes
3. ✅ Gestiona solicitudes de servicio externas
4. ✅ Asigna técnicos a solicitudes
5. ✅ Asigna técnicos masivamente a órdenes sin asignación
6. ✅ Accede a estadísticas administrativas
7. ✅ Exporta reportes completos del sistema
8. ✅ Gestiona proveedores y contratos
9. ✅ Configura parámetros del sistema

---

### Caso de Uso: Supervisor
**Escenario**: Supervisión de equipo de mantenimiento

1. ✅ Visualiza todas las órdenes de trabajo del equipo
2. ✅ Asigna técnicos a órdenes nuevas
3. ✅ Edita detalles de órdenes de trabajo
4. ✅ Consulta carga de trabajo de cada técnico
5. ✅ Visualiza solicitudes de servicio
6. ✅ Edita solicitudes (pero no asigna)
7. ✅ Genera reportes de rendimiento
8. ❌ NO puede crear/eliminar usuarios
9. ❌ NO puede cambiar roles

---

### Caso de Uso: Técnico
**Escenario**: Ejecución de mantenimiento

1. ✅ Ve órdenes de trabajo **asignadas a él**
2. ✅ Actualiza estado de sus órdenes
3. ✅ Registra actividades realizadas
4. ✅ Consulta información de activos
5. ✅ Consulta inventario disponible
6. ✅ Crea nuevas órdenes de trabajo
7. ❌ NO ve órdenes de otros técnicos
8. ❌ NO puede asignar/reasignar técnicos
9. ❌ NO accede a estadísticas admin (recibe 403)
10. ❌ NO puede gestionar usuarios

---

### Caso de Uso: Analista
**Escenario**: Análisis de datos y reportes

1. ✅ Consulta todas las órdenes de trabajo (solo lectura)
2. ✅ Genera reportes personalizados
3. ✅ Exporta datos a Excel/CSV
4. ✅ Visualiza estadísticas y KPIs
5. ✅ Analiza tendencias de mantenimiento
6. ❌ NO puede modificar ningún dato
7. ❌ NO puede crear órdenes
8. ❌ NO puede ser asignado como técnico

---

### Caso de Uso: Operador
**Escenario**: Operaciones básicas de producción

1. ✅ Consulta órdenes de trabajo (solo lectura)
2. ✅ Registra consumos de inventario
3. ✅ Puede crear solicitudes de servicio públicas
4. ✅ Consulta activos disponibles
5. ❌ NO puede crear/editar órdenes
6. ❌ NO puede gestionar inventario
7. ❌ Acceso muy limitado

---

## 🚨 CÓDIGOS DE ERROR POR PERMISOS

### 403 Forbidden
Cuando un usuario intenta acceder a un recurso sin permisos:

```json
{
  "error": "No autorizado"
}
```

**Ejemplo**: Técnico intentando acceder a `/admin/solicitudes/api/estadisticas`

### 302 Redirect
Cuando un usuario sin permisos accede a una página protegida:

```python
flash("No tiene permisos para acceder a esta sección.", "error")
return redirect(url_for("web.index"))
```

**Ejemplo**: Técnico intentando acceder a gestión de usuarios

---

## 🔧 FUNCIONES ESPECIALES DE DESARROLLO

### Endpoints Temporales (Solo Desarrollo)

Estos endpoints son **temporales** para facilitar el desarrollo:

```python
# Convertirse en Administrador
POST /admin/hacerme-admin

# Convertirse en Técnico
POST /admin/hacerme-tecnico

# Crear Técnico Demo
POST /admin/crear-tecnico-demo
```

⚠️ **ADVERTENCIA**: Estos endpoints deben ser **eliminados o protegidos** en producción.

---

## 📝 RECOMENDACIONES DE SEGURIDAD

### 1. Implementar Decorador de Roles
```python
from functools import wraps
from flask import abort

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.rol not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Uso:
@app.route('/admin/users')
@login_required
@role_required('Administrador')
def admin_users():
    # ...
```

### 2. Validar Permisos en Frontend
```javascript
// Ocultar botones según rol del usuario
if (currentUser.rol !== 'Administrador') {
    document.querySelector('.btn-delete-user').style.display = 'none';
}
```

### 3. Auditoría de Accesos
Registrar intentos de acceso no autorizados:

```python
import logging

if current_user.rol != 'Administrador':
    logging.warning(
        f"Usuario {current_user.username} (rol: {current_user.rol}) "
        f"intentó acceder a endpoint protegido: {request.path}"
    )
    abort(403)
```

### 4. Eliminar Endpoints de Desarrollo
En producción, **comentar o eliminar**:
- `/admin/hacerme-admin`
- `/admin/hacerme-tecnico`
- `/admin/crear-tecnico-demo`

---

## 📊 ESTADÍSTICAS DEL SISTEMA DE ROLES

- **Total de Roles**: 5 (Administrador, Supervisor, Técnico, Analista, Operador)
- **Roles con Acceso Admin**: 1 (solo Administrador)
- **Roles con Acceso Solicitudes**: 3 (Admin, Supervisor, Técnico - solo lectura)
- **Roles que pueden ser Técnicos**: 3 (Admin, Supervisor, Técnico)
- **Endpoints Protegidos**: ~15 endpoints con validación de rol
- **Compatibilidad**: Mayúsculas y minúsculas

---

## 🔍 DETECCIÓN DE ROLES EN EL CÓDIGO

### Ubicaciones donde se valida el rol:

1. **app/routes/web.py**: 
   - Líneas 154, 229: Validación de administrador
   
2. **app/controllers/solicitudes_admin_controller.py**:
   - Líneas 54, 124, 148: Validación multi-rol (Admin, Supervisor, Técnico)
   - Línea 240: Solo Administrador

3. **app/controllers/ordenes_controller.py**:
   - Línea 443: Filtrado de técnicos válidos

4. **app/routes/usuarios.py**:
   - Líneas 72, 94, 97, 234: Lógica de permisos según rol

5. **static/js/ordenes.js**:
   - Líneas 714-735: Filtrado de técnicos válidos en frontend

6. **static/js/usuarios.js**:
   - Líneas 311-330: Badges de color según rol

---

## ✅ CHECKLIST DE SEGURIDAD

Para producción, verificar:

- [ ] Eliminar/proteger endpoints de desarrollo (`/admin/hacerme-*`)
- [ ] Implementar decorador `@role_required`
- [ ] Validar permisos en todos los endpoints críticos
- [ ] Ocultar elementos de UI según rol
- [ ] Implementar logging de intentos de acceso no autorizado
- [ ] Validar rol en frontend Y backend
- [ ] Documentar permisos de cada endpoint
- [ ] Realizar pruebas de penetración por rol
- [ ] Configurar alertas de intentos de escalación de privilegios

---

**Documento generado**: 23 de Octubre de 2025  
**Sistema**: GMAO - Gestión de Mantenimiento  
**Versión**: 1.0
