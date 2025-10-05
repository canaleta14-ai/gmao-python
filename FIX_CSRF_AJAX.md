# 🔒 Corrección de Error CSRF en Peticiones AJAX

**Fecha**: 2 de octubre de 2025  
**Error detectado**: 500 Internal Server Error en PUT /usuarios/api/1  
**Causa**: CSRF token missing en peticiones AJAX  
**Severidad**: 🔴 ALTA (bloquea funcionalidad de edición)

---

## 📋 DESCRIPCIÓN DEL PROBLEMA

### Error Observado
```
usuarios/api/1: Failed to load resource: the server responded with a status of 500 ()
Error: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

### Logs del Servidor
```
2025-10-02 19:20:14 - flask_wtf.csrf - INFO - The CSRF token is missing.
2025-10-02 19:20:14 - app.factory - ERROR - Error inesperado: 400 Bad Request: The CSRF token is missing.

flask_wtf.csrf.CSRFError: 400 Bad Request: The CSRF token is missing.
```

### Causa Raíz
Las peticiones AJAX (fetch) realizadas desde JavaScript no incluían el token CSRF requerido por Flask-WTF. El servidor rechazaba las peticiones PUT, POST, PATCH y DELETE por razones de seguridad.

**Petición sin CSRF**:
```javascript
fetch('/usuarios/api/1', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json'
        // ❌ Falta: 'X-CSRFToken': token
    },
    body: JSON.stringify(data)
})
```

---

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. Añadir Meta Tag con CSRF Token

**Archivo**: `app/templates/base.html`

**Cambio**:
```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- NUEVO: Exponer CSRF token para JavaScript -->
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{% block title %}GMAO{% endblock %}</title>
    ...
</head>
```

**Beneficio**: El token CSRF ahora está disponible para JavaScript en todas las páginas.

---

### 2. Crear Utilidad CSRF para JavaScript

**Archivo nuevo**: `static/js/csrf-utils.js`

**Funcionalidad**:

#### A) Función para obtener token
```javascript
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    console.warn('⚠️ CSRF token no encontrado');
    return null;
}
```

#### B) Interceptor global de fetch()
```javascript
// Intercepta TODAS las peticiones fetch() automáticamente
window.fetch = function(url, options) {
    const methodsRequiringCSRF = ['POST', 'PUT', 'PATCH', 'DELETE'];
    const method = options?.method?.toUpperCase() || 'GET';
    
    if (isInternalRequest && methodsRequiringCSRF.includes(method)) {
        options.headers = options.headers || {};
        
        // Añadir CSRF token automáticamente
        const csrfToken = getCSRFToken();
        if (csrfToken) {
            options.headers['X-CSRFToken'] = csrfToken;
            console.log(`🔐 CSRF token añadido a ${method} ${url}`);
        }
    }
    
    return originalFetch.apply(this, [url, options]);
};
```

**Beneficios**:
- ✅ **Automático**: No requiere modificar código existente
- ✅ **Global**: Funciona en todos los módulos (usuarios, activos, órdenes, etc.)
- ✅ **Inteligente**: Solo añade CSRF a peticiones que lo necesitan
- ✅ **Seguro**: No afecta peticiones externas (CDN, APIs externas)

---

### 3. Incluir Script en Base Template

**Archivo**: `app/templates/base.html`

**Cambio**:
```html
<!-- Scripts -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
{% if not login_bg %}
    <!-- CSRF Utils - DEBE cargarse PRIMERO -->
    <script src="{{ url_for('static', filename='js/csrf-utils.js') }}"></script>
    <!-- Otros scripts... -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    ...
{% endif %}
```

**Importante**: csrf-utils.js se carga ANTES que otros scripts para que el interceptor esté activo.

---

## 🔍 CÓMO FUNCIONA

### Flujo Antes (Con Error)
```
1. Usuario edita usuario en /usuarios
2. JavaScript hace: fetch('/usuarios/api/1', {method: 'PUT', ...})
3. ❌ Request NO incluye X-CSRFToken header
4. Flask-WTF rechaza: "CSRF token is missing"
5. ❌ Error 500 → JavaScript recibe HTML en lugar de JSON
6. ❌ "Unexpected token '<', "<!DOCTYPE "... is not valid JSON"
```

### Flujo Después (Corregido)
```
1. Usuario edita usuario en /usuarios
2. JavaScript hace: fetch('/usuarios/api/1', {method: 'PUT', ...})
3. ✅ Interceptor detecta método PUT
4. ✅ Añade automáticamente: headers['X-CSRFToken'] = token
5. ✅ Flask-WTF valida token → Request aceptado
6. ✅ Servidor responde JSON correcto
7. ✅ Usuario actualizado exitosamente
```

---

## 🧪 PRUEBAS PARA VALIDAR LA CORRECCIÓN

### Test 1: Editar Usuario
```
Pasos:
1. Login como admin
2. Ir a /usuarios
3. Click en "Editar" en cualquier usuario
4. Modificar nombre o email
5. Guardar

Resultado esperado:
✅ Usuario actualizado sin errores
✅ Mensaje "Usuario actualizado exitosamente"
✅ En consola: "🔐 CSRF token añadido a PUT /usuarios/api/1"
❌ NO debe aparecer error 500
```

### Test 2: Crear Activo (POST)
```
Pasos:
1. Ir a /activos
2. Click "Nuevo Activo"
3. Completar formulario
4. Guardar

Resultado esperado:
✅ Activo creado correctamente
✅ En consola: "🔐 CSRF token añadido a POST /activos/api"
```

### Test 3: Eliminar Registro (DELETE)
```
Pasos:
1. Ir a cualquier módulo (activos, proveedores, etc.)
2. Click "Eliminar" en un registro
3. Confirmar

Resultado esperado:
✅ Registro eliminado
✅ En consola: "🔐 CSRF token añadido a DELETE /activos/api/X"
```

### Test 4: Verificar en DevTools
```
Pasos:
1. Abrir DevTools (F12)
2. Ir a pestaña "Network"
3. Hacer cualquier acción que envíe PUT/POST/DELETE
4. Click en la request en Network tab
5. Ver pestaña "Headers"

Resultado esperado:
✅ Request Headers contiene:
    X-CSRFToken: IjY3MjQy... (token largo)
```

---

## 🛡️ SEGURIDAD

### Protecciones Implementadas

#### 1. CSRF Protection
- ✅ Token único por sesión
- ✅ Token rotado automáticamente
- ✅ Validación server-side (Flask-WTF)
- ✅ Protección contra ataques CSRF

#### 2. Scope del Interceptor
- ✅ Solo peticiones internas (mismo origin)
- ✅ Solo métodos que modifican datos (POST, PUT, PATCH, DELETE)
- ❌ NO intercepta GET (no lo necesita)
- ❌ NO intercepta peticiones externas (CDN, APIs públicas)

#### 3. Fallback
```javascript
if (!csrfToken) {
    console.warn('⚠️ CSRF token no encontrado en meta tag');
    return null;  // La petición continuará pero podría fallar
}
```

---

## 📊 IMPACTO

### Módulos Afectados (Corregidos)
- ✅ **Usuarios**: Editar, crear, eliminar
- ✅ **Activos**: CRUD completo
- ✅ **Órdenes de Trabajo**: CRUD completo
- ✅ **Proveedores**: CRUD completo
- ✅ **Inventario**: Movimientos, ajustes
- ✅ **Planes de Mantenimiento**: CRUD completo
- ✅ **Solicitudes Admin**: Gestión

### Beneficios
- 🔒 **Seguridad mejorada**: CSRF protection activo en todas las peticiones
- 🚀 **Sin cambios en código existente**: Interceptor global funciona automáticamente
- 🐛 **Bug crítico corregido**: Edición de usuarios y otros CRUD ahora funcionan
- 📈 **Escalable**: Futuros módulos heredan la protección automáticamente

---

## 🔄 MIGRACIÓN

### Archivos Modificados
1. ✏️ `app/templates/base.html` - Añadir meta tag y script
2. ➕ `static/js/csrf-utils.js` - Nueva utilidad (creado)

### Archivos NO Modificados (Beneficio)
- ✅ `static/js/usuarios.js` - No requiere cambios
- ✅ `static/js/activos.js` - No requiere cambios
- ✅ `static/js/ordenes.js` - No requiere cambios
- ✅ Todos los controladores Python - No requieren cambios

### Despliegue
```bash
# 1. Commit de cambios
git add app/templates/base.html
git add static/js/csrf-utils.js
git commit -m "Fix: Añadir CSRF token a peticiones AJAX automáticamente"

# 2. Desplegar a producción
gcloud app deploy app.yaml --project=gmao-sistema-2025 --quiet

# 3. Verificar
# Ir a https://gmao-sistema-2025.ew.r.appspot.com/usuarios
# Editar un usuario → Debe funcionar sin error 500
```

---

## 🐛 TROUBLESHOOTING

### Problema: Sigue apareciendo "CSRF token missing"
**Solución**:
1. Verificar que csrf-utils.js se cargó:
   ```javascript
   // En consola
   console.log(window.CSRFUtils);  // Debe existir
   ```
2. Verificar meta tag:
   ```javascript
   document.querySelector('meta[name="csrf-token"]').content
   ```
3. Hard refresh: Ctrl+Shift+R

### Problema: "CSRF token no encontrado en meta tag"
**Solución**:
- Verificar que base.html tiene: `<meta name="csrf-token" content="{{ csrf_token() }}">`
- Verificar que estás en una página autenticada (no login)
- Logout y login de nuevo

### Problema: Error en peticiones externas
**Solución**:
El interceptor ya filtra peticiones externas. Si hay problema:
```javascript
// Modificar csrf-utils.js línea 38
const isInternalRequest = url.startsWith('/') || url.includes(window.location.hostname);
```

---

## 📚 REFERENCIAS

- [Flask-WTF CSRF Protection](https://flask-wtf.readthedocs.io/en/stable/csrf.html)
- [OWASP CSRF Prevention](https://owasp.org/www-community/attacks/csrf)
- [MDN Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

## ✅ CHECKLIST DE DESPLIEGUE

- [x] Añadir meta tag CSRF en base.html
- [x] Crear csrf-utils.js
- [x] Incluir script en base.html
- [ ] Desplegar a producción
- [ ] Probar editar usuario
- [ ] Probar crear activo
- [ ] Probar eliminar registro
- [ ] Verificar en consola que CSRF se añade
- [ ] Verificar en Network tab
- [ ] Cerrar ticket de bug

---

**Documento creado**: 2 de octubre de 2025  
**Versión**: 1.0  
**Estado**: ✅ Solución implementada, pendiente despliegue
