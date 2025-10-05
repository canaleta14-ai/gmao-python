# 🧪 Ejecución de Pruebas en Orden - Sistema GMAO
## Sesión de Testing: 2 de octubre de 2025

**Versión desplegada**: 20251002t210935  
**URL**: https://gmao-sistema-2025.ew.r.appspot.com  
**Tester**: [Tu nombre]  
**Inicio**: [Hora]

---

## 📋 ORDEN DE EJECUCIÓN

### ✅ FASE 1: DESPLIEGUE Y VERIFICACIÓN BÁSICA (10 min)

#### ☑️ Paso 1.1: Verificar Despliegue Completado
```bash
# Comando para verificar versión activa
gcloud app versions list --project=gmao-sistema-2025 --service=default
```

**Resultado esperado**:
```
VERSION          TRAFFIC_SPLIT  SERVING_STATUS
20251002t210935  1.00           SERVING
```

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

#### ☑️ Paso 1.2: Verificar Aplicación Carga
**URL**: https://gmao-sistema-2025.ew.r.appspot.com/

**Pasos**:
1. Abrir URL en navegador
2. Verificar que carga la página de login
3. Verificar que no hay errores en consola (F12)

**Checklist**:
- [ ] Página carga en < 3 segundos
- [ ] Logo visible
- [ ] Formulario de login visible
- [ ] Sin errores JavaScript en consola
- [ ] Sin errores CSS (layout correcto)

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Screenshot**: ___________________________________________

---

### ⭐ FASE 2: TEST #22 - ENLACE DIRECTO A SOLICITUDES (5 min)

#### ☑️ Paso 2.1: Verificar Botón Visible en Login

**URL**: https://gmao-sistema-2025.ew.r.appspot.com/

**Checklist Visual**:
- [ ] Divisor con "o" visible debajo del botón de login
- [ ] Botón "Solicitar Servicio de Mantenimiento" visible
- [ ] Ícono de archivo (bi-file-earmark-plus) presente
- [ ] Texto "No necesitas iniciar sesión..." visible
- [ ] Botón tiene borde azul (outline-primary)

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Screenshot**: ___________________________________________

---

#### ☑️ Paso 2.2: Verificar Efecto Hover

**Pasos**:
1. Pasar el mouse sobre el botón "Solicitar Servicio"
2. Observar efectos visuales

**Checklist**:
- [ ] Fondo cambia a gradiente azul
- [ ] Botón se eleva ligeramente (translateY)
- [ ] Aparece sombra azul brillante
- [ ] Transición suave (0.3s)
- [ ] Cursor cambia a pointer

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

#### ☑️ Paso 2.3: Verificar Funcionalidad del Enlace

**Pasos**:
1. Click en "Solicitar Servicio de Mantenimiento"
2. Verificar redirección

**Checklist**:
- [ ] Redirige a: https://gmao-sistema-2025.ew.r.appspot.com/solicitudes/nueva
- [ ] Formulario de solicitud carga correctamente
- [ ] Campos visibles: Nombre, Email, Teléfono, Ubicación, Descripción
- [ ] Input de archivos visible
- [ ] Sin necesidad de login

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Screenshot**: ___________________________________________

---

#### ☑️ Paso 2.4: Responsive Design del Botón

**Pasos**:
1. Abrir DevTools (F12)
2. Activar "Responsive Design Mode"
3. Probar en diferentes tamaños

**Dispositivos a probar**:

**Mobile (375px)**:
- [ ] Botón ocupa todo el ancho
- [ ] Texto legible sin zoom
- [ ] Toque fácil (botón grande)
- [ ] Divisor "o" centrado

**Tablet (768px)**:
- [ ] Layout mantiene estructura
- [ ] Botón proporcionado
- [ ] Espaciado correcto

**Desktop (1920px)**:
- [ ] Botón no excesivamente ancho
- [ ] Centrado correctamente
- [ ] Hover funciona

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

### 🔒 FASE 3: TEST #3 - LOGOUT AL CERRAR NAVEGADOR (10 min)

#### ☑️ Paso 3.1: Login Normal

**URL**: https://gmao-sistema-2025.ew.r.appspot.com/

**Pasos**:
1. Ingresar usuario: `admin`
2. Ingresar contraseña: `admin123`
3. Click en "Iniciar Sesión"

**Checklist**:
- [ ] Login exitoso
- [ ] Redirección a /dashboard
- [ ] Mensaje "Login exitoso" visible
- [ ] Sidebar visible con nombre de usuario
- [ ] URL actual: https://gmao-sistema-2025.ew.r.appspot.com/dashboard

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Hora login**: ___________________________________________

---

#### ☑️ Paso 3.2: Verificar Sesión Activa

**Pasos**:
1. Navegar a diferentes secciones:
   - /activos
   - /ordenes
   - /usuarios
2. Verificar que no pide login nuevamente

**Checklist**:
- [ ] Navegación fluida sin re-login
- [ ] Usuario visible en sidebar en todas las páginas
- [ ] Sin redirecciones inesperadas

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

#### ☑️ Paso 3.3: Inspeccionar Cookie de Sesión

**Pasos**:
1. Abrir DevTools (F12)
2. Ir a Application → Cookies
3. Seleccionar https://gmao-sistema-2025.ew.r.appspot.com
4. Buscar cookie de sesión (probablemente "session" o "remember_token")

**Datos a verificar**:

| Propiedad | Valor Esperado | Valor Real | ✓ |
|-----------|----------------|------------|---|
| Name | session | __________ | ☐ |
| HttpOnly | ✅ True | __________ | ☐ |
| Secure | ✅ True (HTTPS) | __________ | ☐ |
| SameSite | Lax o Strict | __________ | ☐ |
| Expires / Max-Age | Session | __________ | ☐ |

**IMPORTANTE**: 
- Si Max-Age tiene un número (ej: 3600), la cookie es persistente
- Si dice "Session" o no tiene Max-Age, es cookie de sesión ✅

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Screenshot**: ___________________________________________

---

#### ☑️ Paso 3.4: Cerrar Navegador (Test Principal)

**Pasos CRÍTICOS**:
1. **CERRAR TODAS LAS VENTANAS DEL NAVEGADOR**
   - Chrome: Cerrar todas las ventanas (no solo pestañas)
   - Firefox: File → Exit
   - Edge: Cerrar todas las ventanas
2. Esperar 5 segundos
3. Abrir navegador de nuevo
4. Ir a: https://gmao-sistema-2025.ew.r.appspot.com/activos

**⚠️ IMPORTANTE**: 
- NO usar "Restaurar pestañas" si el navegador lo ofrece
- Escribir manualmente la URL o usar marcador
- Asegurarse de que el navegador cerró completamente (verificar en Task Manager)

**Checklist**:
- [ ] Navegador cerrado completamente
- [ ] Navegador reabierto
- [ ] URL /activos ingresada manualmente
- [ ] Resultado: ¿Redirige a /login?

**Resultado Esperado**: ✅ Redirige a /login (sesión cerrada)  
**Resultado Alternativo**: ❌ Muestra /activos (sesión persistió - BUG)

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Hora cierre navegador**: ___________________________________________  
**Hora reapertura**: ___________________________________________  
**¿Redirigió a /login?**: ⬜ SÍ | ⬜ NO

---

#### ☑️ Paso 3.5: Login Nuevamente

**Pasos**:
1. Después del test anterior, hacer login de nuevo
2. Verificar funcionamiento normal

**Checklist**:
- [ ] Login funciona correctamente
- [ ] Dashboard carga
- [ ] Todo funciona como antes

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

#### ☑️ Paso 3.6: Test Alternativo - Solo Cerrar Pestaña

**Pasos**:
1. Login nuevamente
2. Navegar a /activos
3. **Solo cerrar la pestaña** (no todo el navegador)
4. Abrir nueva pestaña
5. Ir a /activos

**Resultado Esperado**: 
- ⚠️ Sesión DEBERÍA mantenerse (porque el navegador sigue abierto)
- ✅ Muestra /activos directamente

**¿Resultado?**: ⬜ Sesión mantenida | ⬜ Sesión cerrada

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

### 🌐 FASE 4: TEST #33 - PERFORMANCE CON LIGHTHOUSE (10 min)

#### ☑️ Paso 4.1: Lighthouse - Página de Login

**Pasos**:
1. Abrir https://gmao-sistema-2025.ew.r.appspot.com/ (logout primero)
2. Abrir DevTools (F12)
3. Ir a pestaña "Lighthouse"
4. Configuración:
   - Mode: Navigation
   - Device: Desktop
   - Categories: Performance, Accessibility, Best Practices, SEO
5. Click "Generate report"

**Resultados**:

| Métrica | Objetivo | Resultado | ✓ |
|---------|----------|-----------|---|
| **Performance** | > 80 | __________ | ☐ |
| **Accessibility** | > 90 | __________ | ☐ |
| **Best Practices** | > 80 | __________ | ☐ |
| **SEO** | > 80 | __________ | ☐ |

**Core Web Vitals**:

| Métrica | Objetivo | Resultado | ✓ |
|---------|----------|-----------|---|
| First Contentful Paint | < 1.8s | __________ | ☐ |
| Largest Contentful Paint | < 2.5s | __________ | ☐ |
| Total Blocking Time | < 300ms | __________ | ☐ |
| Cumulative Layout Shift | < 0.1 | __________ | ☐ |
| Speed Index | < 3.4s | __________ | ☐ |

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Screenshot del reporte**: ___________________________________________

**Problemas encontrados** (si score < objetivo):
1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

---

#### ☑️ Paso 4.2: Lighthouse - Dashboard (Autenticado)

**Pasos**:
1. Login como admin
2. Ir a /dashboard
3. Ejecutar Lighthouse de nuevo
4. Comparar resultados

**Resultados Dashboard**:

| Métrica | Login | Dashboard | Diferencia |
|---------|-------|-----------|------------|
| Performance | _____ | _________ | __________ |
| Accessibility | _____ | _________ | __________ |
| Best Practices | _____ | _________ | __________ |

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

#### ☑️ Paso 4.3: Lighthouse Mobile

**Pasos**:
1. Ejecutar Lighthouse en página de login
2. Cambiar Device: Mobile
3. Generate report

**Resultados Mobile**:

| Métrica | Desktop | Mobile | Diferencia |
|---------|---------|--------|------------|
| Performance | _____ | ______ | __________ |

**⚠️ Nota**: Mobile suele tener score más bajo (es normal 60-70)

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Screenshot**: ___________________________________________

---

### 📧 FASE 5: TEST #41 - EMAIL Y SOLICITUDES (15 min)

#### ☑️ Paso 5.1: Crear Solicitud Completa

**URL**: https://gmao-sistema-2025.ew.r.appspot.com/solicitudes/nueva

**Pasos**:
1. Completar formulario:
   ```
   Nombre: Juan Pérez Test
   Email: [tu_email_real]@gmail.com
   Teléfono: 600123456
   Ubicación: Oficina Planta Baja
   Descripción: El aire acondicionado hace mucho ruido (ñoño)
   ```
2. Adjuntar 2-3 archivos:
   - Foto 1: [nombre archivo]
   - Foto 2: [nombre archivo]
   - PDF (opcional): [nombre archivo]
3. Click "Enviar Solicitud"

**Checklist**:
- [ ] Todos los campos completados
- [ ] Archivos seleccionados (max 5)
- [ ] Preview de imágenes visible antes de enviar
- [ ] Tamaño total < 10MB por archivo
- [ ] Botón "Enviar" activo

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Hora envío**: ___________________________________________

---

#### ☑️ Paso 5.2: Verificar Respuesta del Sistema

**Después de hacer click en "Enviar"**:

**Checklist**:
- [ ] Mensaje de confirmación visible
- [ ] Número de solicitud generado (ej: SOL-0001)
- [ ] Redirección o mensaje de éxito
- [ ] Sin errores en consola JavaScript
- [ ] Sin errores 500

**Número de solicitud**: ___________________________________________  
**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido

---

#### ☑️ Paso 5.3: Verificar Email Confirmación (Usuario)

**Revisar bandeja de entrada**: [tu_email]@gmail.com

**Tiempo esperado**: 1-3 minutos

**Checklist Email**:
- [ ] Email recibido
- [ ] Asunto: "Confirmación de Solicitud de Servicio" (o similar)
- [ ] Remitente: j_hidalgo@disfood.com
- [ ] Cuerpo del email contiene:
  - [ ] Número de solicitud (SOL-XXXX)
  - [ ] Datos del solicitante
  - [ ] Descripción del problema
  - [ ] Mensaje de confirmación
- [ ] Caracteres especiales correctos (ñ, á, é)
- [ ] NO está en spam

**Hora recepción email**: ___________________________________________  
**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Screenshot**: ___________________________________________

---

#### ☑️ Paso 5.4: Verificar Email Notificación (Admin)

**Revisar**: j_hidalgo@disfood.com

**Checklist Email Admin**:
- [ ] Email recibido
- [ ] Asunto: "Nueva Solicitud de Servicio" (o similar)
- [ ] Contiene todos los datos de la solicitud
- [ ] Link o botón para acceder al sistema
- [ ] Lista de archivos adjuntos (si aplica)

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

#### ☑️ Paso 5.5: Verificar Archivos Subidos

**Pasos**:
1. Login como admin
2. Ir a /solicitudes/admin (o ruta correspondiente)
3. Buscar solicitud SOL-XXXX
4. Abrir detalles
5. Verificar archivos adjuntos

**Checklist**:
- [ ] Archivos listados correctamente
- [ ] Número de archivos correcto
- [ ] Nombres de archivos visibles
- [ ] Tamaños mostrados
- [ ] Preview de imágenes funciona
- [ ] Links de descarga funcionan

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Ubicación archivos**: ___________________________________________

---

#### ☑️ Paso 5.6: Test UTF-8 Específico

**Crear nueva solicitud con caracteres especiales**:

```
Descripción: 
"El compresor está roto. Necesitamos reparación urgente.
Ubicación: Almacén nº 3
Problema: Ruido excesivo (señal de avería)
Contacto: José María Peña"
```

**Verificar en email recibido**:
- [ ] Todas las tildes correctas (á, é, í, ó, ú)
- [ ] Letra ñ correcta
- [ ] Símbolos correctos (nº)
- [ ] No aparece "?" o caracteres raros

**Estado**: ⬜ Pendiente | ✅ Completado | ❌ Fallido  
**Notas**: ___________________________________________

---

### 🔒 FASE 6: TEST #26-28 - SEGURIDAD BÁSICA (10 min)

#### ☑️ Paso 6.1: Test SQL Injection

**Intentos de inyección**:

**Test 1 - Login con OR '1'='1**:
```
Username: admin' OR '1'='1
Password: cualquiera
```
**Resultado esperado**: ❌ Login falla  
**Resultado real**: ⬜ Login falla | ⬜ Login exitoso (CRÍTICO)

**Test 2 - Login con UNION SELECT**:
```
Username: admin' UNION SELECT * FROM usuarios--
Password: test
```
**Resultado esperado**: ❌ Login falla  
**Resultado real**: ⬜ Login falla | ⬜ Login exitoso (CRÍTICO)

**Test 3 - Búsqueda de activos**:
```
Buscar: '; DROP TABLE activos; --
```
**Resultado esperado**: ❌ No ejecuta SQL  
**Resultado real**: ⬜ Busca normal | ⬜ Error SQL (BUG) | ⬜ Tabla eliminada (CRÍTICO)

**Estado global SQL Injection**: ⬜ Pendiente | ✅ SEGURO | ❌ VULNERABLE

---

#### ☑️ Paso 6.2: Test XSS (Cross-Site Scripting)

**Test 1 - Script en nombre de activo**:
```
Pasos:
1. Login como admin
2. Crear nuevo activo
3. Nombre: <script>alert('XSS')</script>
4. Guardar
5. Ver listado de activos
```

**Resultado esperado**: ✅ Script NO se ejecuta (se muestra como texto)  
**Resultado real**: ⬜ Texto plano | ⬜ Alert ejecutado (CRÍTICO)

**Test 2 - IMG tag malicioso**:
```
Crear orden con comentario:
<img src=x onerror="alert('XSS')">
```

**Resultado esperado**: ✅ No se ejecuta JavaScript  
**Resultado real**: ⬜ Seguro | ⬜ Alert ejecutado (CRÍTICO)

**Estado global XSS**: ⬜ Pendiente | ✅ SEGURO | ❌ VULNERABLE

---

#### ☑️ Paso 6.3: Test CSRF Token

**Pasos**:
1. Inspeccionar formulario de crear activo
2. Ver código fuente (Ctrl+U o click derecho → Ver código)
3. Buscar: `csrf_token`

**Checklist**:
- [ ] Token presente en formulario
- [ ] Token es un hash largo (ejemplo: IjY3MjQyNWFmZjk4...)
- [ ] Token diferente en cada carga de página
- [ ] Input tipo hidden: `<input type="hidden" name="csrf_token" value="...">`

**Intentar enviar sin token**:
```
Método: Postman o curl
POST /activos/crear
Sin incluir csrf_token
```

**Resultado esperado**: ❌ 400 Bad Request "CSRF token missing"  
**Resultado real**: ⬜ Error CSRF | ⬜ Acepta request (CRÍTICO)

**Estado global CSRF**: ⬜ Pendiente | ✅ PROTEGIDO | ❌ VULNERABLE

---

#### ☑️ Paso 6.4: Verificar Cookies Seguras

**Pasos**:
1. DevTools → Application → Cookies
2. Inspeccionar cookie de sesión

**Verificación**:

| Flag | Requerido | Presente | Notas |
|------|-----------|----------|-------|
| HttpOnly | ✅ | ⬜ | Previene acceso desde JS |
| Secure | ✅ (prod) | ⬜ | Solo HTTPS |
| SameSite | ✅ | ⬜ | Previene CSRF |

**Intentar acceder cookie desde consola**:
```javascript
// En consola de DevTools
document.cookie
```

**Resultado esperado**: Cookie de sesión NO visible (por HttpOnly)  
**Resultado real**: ___________________________________________

**Estado**: ⬜ Pendiente | ✅ SEGURO | ❌ VULNERABLE

---

### 📱 FASE 7: TEST #37 - RESPONSIVE DESIGN (15 min)

#### ☑️ Paso 7.1: Mobile - iPhone SE (375×667)

**Pasos**:
1. DevTools → Toggle device toolbar
2. Seleccionar "iPhone SE"
3. Probar páginas:
   - Login
   - Dashboard
   - Activos (listado)
   - Crear activo (formulario)
   - Solicitudes

**Checklist Mobile**:

**Login**:
- [ ] Formulario centrado
- [ ] Inputs ocupan todo el ancho
- [ ] Botones touch-friendly (>44px alto)
- [ ] Texto legible sin zoom
- [ ] Logo no muy grande
- [ ] Botón "Solicitar Servicio" full-width

**Dashboard**:
- [ ] Sidebar colapsado en hamburger menu
- [ ] Cards apiladas verticalmente
- [ ] Gráficos redimensionados
- [ ] Sin scroll horizontal

**Listado Activos**:
- [ ] Tabla scrollable horizontalmente O
- [ ] Tabla transformada a cards (mejor UX)
- [ ] Botones accesibles
- [ ] Búsqueda funcional

**Formularios**:
- [ ] Campos apilados verticalmente
- [ ] Labels visibles
- [ ] Botones guardar/cancelar accesibles
- [ ] Teclado móvil apropiado (email, tel, number)

**Estado Mobile**: ⬜ Pendiente | ✅ PASS | ❌ FAIL  
**Issues encontrados**: ___________________________________________

---

#### ☑️ Paso 7.2: Tablet - iPad (768×1024)

**Checklist Tablet**:
- [ ] Sidebar visible o colapsable
- [ ] Cards en 2 columnas
- [ ] Tablas visibles sin scroll
- [ ] Navegación cómoda

**Estado Tablet**: ⬜ Pendiente | ✅ PASS | ❌ FAIL

---

#### ☑️ Paso 7.3: Desktop - Full HD (1920×1080)

**Checklist Desktop**:
- [ ] Sidebar fija visible
- [ ] Contenido no excesivamente ancho
- [ ] Max-width razonable (1200-1400px)
- [ ] Whitespace apropiado
- [ ] Todo el espacio aprovechado

**Estado Desktop**: ⬜ Pendiente | ✅ PASS | ❌ FAIL

---

### 🎨 FASE 8: TEST #39-40 - UX Y FEEDBACK (10 min)

#### ☑️ Paso 8.1: Feedback Visual en Acciones

**Test crear activo**:
```
Acción: Crear nuevo activo exitosamente
```

**Checklist**:
- [ ] Mensaje de éxito aparece
- [ ] Color verde (success)
- [ ] Ícono de check visible
- [ ] Mensaje desaparece automáticamente (~5s)
- [ ] Posición: Top-right o top-center
- [ ] No bloquea la interfaz

**Test eliminar**:
```
Acción: Intentar eliminar activo
```

**Checklist**:
- [ ] Modal de confirmación aparece
- [ ] Mensaje claro: "¿Estás seguro?"
- [ ] Botones: Cancelar (gris) y Eliminar (rojo)
- [ ] Después de confirmar: Mensaje de éxito
- [ ] Elemento desaparece de la lista

**Test error de validación**:
```
Acción: Enviar formulario con campos vacíos
```

**Checklist**:
- [ ] Campos requeridos marcados en rojo
- [ ] Mensajes de error específicos
- [ ] Focus automático en primer error
- [ ] Mensaje general: "Completa los campos requeridos"

**Estado Feedback**: ⬜ Pendiente | ✅ PASS | ❌ FAIL

---

#### ☑️ Paso 8.2: Loading States

**Acciones que deberían mostrar spinner**:
- [ ] Login (durante autenticación)
- [ ] Cargar dashboard (si hay delay)
- [ ] Subir archivos
- [ ] Guardar formulario
- [ ] Eliminar registro

**Verificar**:
- [ ] Spinner visible
- [ ] Botón deshabilitado durante loading
- [ ] Texto cambia (ej: "Guardando...")
- [ ] No se puede enviar múltiples veces

**Estado Loading**: ⬜ Pendiente | ✅ PASS | ❌ FAIL

---

### 🔗 FASE 9: TEST #42 - INTEGRACIÓN BASE DE DATOS (10 min)

#### ☑️ Paso 9.1: Verificar Conexión Cloud SQL

**Comandos (Cloud Shell o local con Cloud SQL Proxy)**:
```bash
# Listar instancias
gcloud sql instances list --project=gmao-sistema-2025

# Conectar a BD
gcloud sql connect gmao-postgres --user=gmao-user --project=gmao-sistema-2025

# Dentro de PostgreSQL
\dt  -- Listar tablas
SELECT COUNT(*) FROM activo;
SELECT COUNT(*) FROM orden_trabajo;
SELECT COUNT(*) FROM solicitud_servicio;
```

**Resultados**:
```
Tabla activo: _____ registros
Tabla orden_trabajo: _____ registros
Tabla solicitud_servicio: _____ registros
```

**Estado**: ⬜ Pendiente | ✅ PASS | ❌ FAIL

---

#### ☑️ Paso 9.2: Test de Integridad Referencial

**Test 1: Eliminar activo con órdenes**:
```
1. Crear activo ACT-TEST
2. Crear orden para ACT-TEST
3. Intentar eliminar ACT-TEST
```

**Resultado esperado**: ❌ Error "No se puede eliminar, tiene órdenes asociadas"  
**Resultado real**: ⬜ Error mostrado | ⬜ Se eliminó (BUG)

**Test 2: Verificar CASCADE**:
```
1. Crear solicitud con archivos
2. Eliminar solicitud
3. Verificar que archivos también se eliminaron
```

**Resultado esperado**: ✅ Archivos eliminados automáticamente (CASCADE)  
**Resultado real**: ⬜ CASCADE OK | ⬜ Archivos huérfanos (BUG)

**Estado**: ⬜ Pendiente | ✅ PASS | ❌ FAIL

---

### 📊 FASE 10: RESUMEN Y REPORTE FINAL (5 min)

#### Resumen de Resultados

| Fase | Tests | Passed | Failed | Pendientes | % Éxito |
|------|-------|--------|--------|------------|---------|
| 1. Despliegue | 2 | _____ | _____ | _____ | ___% |
| 2. Enlace Login | 4 | _____ | _____ | _____ | ___% |
| 3. Logout Navegador | 6 | _____ | _____ | _____ | ___% |
| 4. Performance | 3 | _____ | _____ | _____ | ___% |
| 5. Email | 6 | _____ | _____ | _____ | ___% |
| 6. Seguridad | 4 | _____ | _____ | _____ | ___% |
| 7. Responsive | 3 | _____ | _____ | _____ | ___% |
| 8. UX/Feedback | 2 | _____ | _____ | _____ | ___% |
| 9. Base de Datos | 2 | _____ | _____ | _____ | ___% |
| **TOTAL** | **32** | _____ | _____ | _____ | ___% |

---

#### Issues Críticos Encontrados

| # | Descripción | Severidad | Fase | Acción Requerida |
|---|-------------|-----------|------|------------------|
| 1 | ______________ | 🔴 Alta | ____ | _______________ |
| 2 | ______________ | 🟡 Media | ____ | _______________ |
| 3 | ______________ | 🟢 Baja | ____ | _______________ |

**Severidades**:
- 🔴 **Alta**: Bloquea funcionalidad crítica o seguridad
- 🟡 **Media**: Afecta UX pero no bloquea
- 🟢 **Baja**: Mejora cosmética

---

#### Recomendaciones

**Corto plazo** (esta semana):
1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

**Medio plazo** (este mes):
1. ___________________________________________
2. ___________________________________________

**Largo plazo** (3 meses):
1. ___________________________________________
2. ___________________________________________

---

#### Firma y Aprobación

**Tester**: ___________________________________________  
**Fecha**: 2 de octubre de 2025  
**Hora finalización**: ___________________________________________  
**Tiempo total**: ___________________________________________  

**Estado General del Sistema**:
⬜ ✅ Aprobado para producción  
⬜ ⚠️ Aprobado con reservas (issues menores)  
⬜ ❌ No aprobado (issues críticos)

**Comentarios finales**:
___________________________________________
___________________________________________
___________________________________________

---

## 📎 ANEXOS

### Anexo A: Screenshots
- [ ] Login page con botón solicitudes
- [ ] Hover effect del botón
- [ ] Formulario de solicitud
- [ ] Email recibido (confirmación)
- [ ] Email admin (notificación)
- [ ] Lighthouse report
- [ ] DevTools cookies
- [ ] Mobile responsive
- [ ] Dashboard

### Anexo B: Logs Relevantes

```
[Pegar logs de GCP aquí]
```

### Anexo C: Métricas de Performance

```
[Resultados detallados de Lighthouse]
```

---

**Documento generado automáticamente**  
**Template versión**: 1.0  
**Sistema**: GMAO v20251002t210935
