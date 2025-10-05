# 🧪 Plan de Pruebas Completo - Sistema GMAO
## Guía de Testing y Validación

**Fecha**: 2 de octubre de 2025  
**Proyecto**: Sistema GMAO  
**Versión**: 20251002t200236  
**URL Producción**: https://gmao-sistema-2025.ew.r.appspot.com

---

## 📋 ÍNDICE DE PRUEBAS

1. [Pruebas Funcionales](#1-pruebas-funcionales)
2. [Pruebas de Seguridad](#2-pruebas-de-seguridad)
3. [Pruebas de Rendimiento](#3-pruebas-de-rendimiento)
4. [Pruebas de UX/UI](#4-pruebas-de-uxui)
5. [Pruebas de Integración](#5-pruebas-de-integración)
6. [Pruebas de Datos](#6-pruebas-de-datos)
7. [Pruebas de Email](#7-pruebas-de-email)
8. [Pruebas de Infraestructura](#8-pruebas-de-infraestructura)
9. [Pruebas de Regresión](#9-pruebas-de-regresión)
10. [Pruebas de Accesibilidad](#10-pruebas-de-accesibilidad)

---

## 1. PRUEBAS FUNCIONALES

### 1.1 Autenticación y Sesiones ✅

#### Test 1: Login Correcto
```
URL: https://gmao-sistema-2025.ew.r.appspot.com/
Usuario: admin
Contraseña: admin123

Pasos:
1. Ir a la página de login
2. Ingresar credenciales correctas
3. Click en "Iniciar Sesión"

Resultado Esperado:
✅ Redirección a /dashboard
✅ Mensaje "Login exitoso"
✅ Sidebar visible con nombre de usuario
```

#### Test 2: Login Incorrecto
```
Pasos:
1. Ingresar usuario o contraseña incorrectos
2. Click en "Iniciar Sesión"

Resultado Esperado:
❌ No redirige
⚠️ Mensaje "Usuario o contraseña incorrectos"
🔒 Protección contra fuerza bruta
```

#### Test 3: Logout al Cerrar Navegador ⭐ NUEVO
```
Pasos:
1. Hacer login exitoso
2. Navegar por el sistema
3. Cerrar TODAS las ventanas del navegador
4. Abrir navegador de nuevo
5. Ir a https://gmao-sistema-2025.ew.r.appspot.com/activos

Resultado Esperado:
✅ Redirección automática a /login
✅ No mantiene sesión activa
✅ Cookie de sesión eliminada

Estado: 🟡 PENDIENTE DE DESPLEGAR
```

#### Test 4: Protección de Rutas
```
Pasos:
1. Sin hacer login, intentar acceder a:
   - /activos
   - /ordenes
   - /usuarios
   - /planes

Resultado Esperado:
✅ Redirección a /login con parámetro ?next=/ruta
✅ Después de login, redirige a la ruta solicitada
```

#### Test 5: Roles y Permisos
```
Crear usuarios con diferentes roles:
- Admin: Acceso total
- Técnico: Solo activos y órdenes
- Supervisor: Activos, órdenes y planes
- Almacén: Solo inventario

Resultado Esperado:
✅ Cada rol solo ve sus módulos permitidos
✅ Intento de acceso no autorizado → 403 Forbidden
```

---

### 1.2 Gestión de Activos

#### Test 6: Crear Activo
```
Pasos:
1. Ir a /activos
2. Click en "Nuevo Activo"
3. Completar formulario:
   - Código: ACT-001
   - Nombre: Compresor Industrial
   - Tipo: Maquinaria
   - Ubicación: Planta Producción
   - Estado: Operativo
4. Guardar

Resultado Esperado:
✅ Activo creado en BD
✅ Aparece en listado
✅ Mensaje de confirmación
✅ ID generado automáticamente
```

#### Test 7: Editar Activo
```
Pasos:
1. Buscar activo ACT-001
2. Click en "Editar"
3. Cambiar estado a "Mantenimiento"
4. Guardar

Resultado Esperado:
✅ Cambios guardados
✅ Histórico de cambios registrado (si existe)
✅ Actualización en tiempo real
```

#### Test 8: Eliminar Activo
```
Pasos:
1. Seleccionar activo sin órdenes asociadas
2. Click en "Eliminar"
3. Confirmar en modal

Resultado Esperado:
✅ Activo eliminado de BD
✅ Ya no aparece en listado
⚠️ Si tiene órdenes activas → Error, no se puede eliminar
```

#### Test 9: Búsqueda y Filtros
```
Pasos:
1. Crear 10+ activos de diferentes tipos
2. Usar barra de búsqueda: "Compresor"
3. Filtrar por tipo: "Maquinaria"
4. Filtrar por estado: "Operativo"

Resultado Esperado:
✅ Búsqueda en tiempo real
✅ Filtros combinables
✅ Resultados correctos
✅ Paginación funcional
```

#### Test 10: Upload de Manuales
```
Pasos:
1. Editar activo ACT-001
2. Adjuntar archivo PDF (manual)
3. Guardar

Resultado Esperado:
✅ Archivo subido a Cloud Storage
✅ Link de descarga visible
✅ Tamaño máximo respetado (10MB)
✅ Formatos permitidos: PDF, DOC, DOCX
```

---

### 1.3 Órdenes de Trabajo

#### Test 11: Crear Orden de Trabajo
```
Pasos:
1. Ir a /ordenes
2. Click "Nueva Orden"
3. Completar:
   - Título: Mantenimiento compresor
   - Tipo: Preventivo
   - Prioridad: Alta
   - Activo: ACT-001
   - Técnico asignado: Juan Pérez
   - Fecha planificada: Mañana
4. Guardar

Resultado Esperado:
✅ Orden creada con número único (OT-0001)
✅ Estado inicial: "Pendiente"
✅ Email notificación a técnico
✅ Aparece en calendario
```

#### Test 12: Workflow de Estados
```
Estados: Pendiente → En Progreso → Completada → Cerrada

Pasos:
1. Crear orden (Pendiente)
2. Iniciar trabajo → En Progreso
3. Marcar completada → Completada
4. Cerrar orden → Cerrada

Resultado Esperado:
✅ Transiciones correctas
✅ No se puede volver a estado anterior
✅ Fecha/hora de cada cambio registrada
✅ Usuario que hizo el cambio registrado
```

#### Test 13: Adjuntar Archivos a Orden
```
Pasos:
1. Abrir orden OT-0001
2. Subir fotos del trabajo (JPG)
3. Subir informe (PDF)

Resultado Esperado:
✅ Múltiples archivos (max 5)
✅ Preview de imágenes
✅ Tamaño total < 50MB
✅ Archivos en /tmp o Cloud Storage
```

#### Test 14: Historial de Orden
```
Pasos:
1. Ver orden OT-0001
2. Revisar pestaña "Historial"

Resultado Esperado:
✅ Todas las acciones registradas
✅ Fecha/hora de cada cambio
✅ Usuario responsable
✅ Comentarios añadidos
```

---

### 1.4 Mantenimiento Preventivo

#### Test 15: Crear Plan de Mantenimiento
```
Pasos:
1. Ir a /planes
2. Click "Nuevo Plan"
3. Configurar:
   - Nombre: Revisión Compresor
   - Activo: ACT-001
   - Frecuencia: Mensual
   - Día: 1 de cada mes
   - Tipo: Preventivo
4. Activar plan

Resultado Esperado:
✅ Plan creado y activo
✅ Primera orden generada automáticamente
✅ Próxima ejecución calculada
✅ Email confirmación a responsable
```

#### Test 16: Generación Automática de Órdenes
```
Condiciones:
- Plan mensual configurado
- Día: 1 de cada mes
- Hora: 00:00 (cron job)

Pasos:
1. Simular paso de tiempo al día 1
2. Ejecutar cron/scheduler

Resultado Esperado:
✅ Orden creada automáticamente
✅ Número correlativo (OT-0002)
✅ Técnico asignado según plan
✅ Email enviado
✅ Próxima ejecución actualizada
```

#### Test 17: Modificar Frecuencia de Plan
```
Pasos:
1. Editar plan existente
2. Cambiar de mensual a semanal
3. Guardar

Resultado Esperado:
✅ Frecuencia actualizada
✅ Próxima ejecución recalculada
✅ Órdenes futuras ajustadas
⚠️ Órdenes pasadas NO afectadas
```

---

### 1.5 Inventario

#### Test 18: Crear Artículo de Inventario
```
Pasos:
1. Ir a /inventario
2. Click "Nuevo Artículo"
3. Completar:
   - Código: REP-001
   - Nombre: Filtro de aire
   - Categoría: Repuestos
   - Stock actual: 10
   - Stock mínimo: 5
   - Proveedor: Proveedor A
   - Precio unitario: €25
4. Guardar

Resultado Esperado:
✅ Artículo creado
✅ Stock inicial registrado
✅ Valoración calculada (10 × €25 = €250)
```

#### Test 19: Movimientos de Inventario
```
Pasos:
1. Consumir 3 unidades de REP-001 (Orden OT-0001)
2. Entrada de 20 unidades (compra)
3. Ajuste de inventario: -2 (merma)

Resultado Esperado:
✅ Stock actualizado: 10 - 3 + 20 - 2 = 25
✅ Cada movimiento registrado con:
   - Fecha/hora
   - Tipo (entrada/salida/ajuste)
   - Cantidad
   - Usuario
   - Referencia (orden/compra)
✅ Valoración actualizada
```

#### Test 20: Alertas de Stock Bajo
```
Condiciones:
- REP-001: Stock mínimo = 5
- Stock actual = 4

Resultado Esperado:
✅ Alerta visual en inventario (color rojo)
✅ Badge "Stock Bajo" visible
✅ Email a responsable de compras (opcional)
✅ Dashboard muestra alerta
```

---

### 1.6 Solicitudes de Servicio (Públicas)

#### Test 21: Crear Solicitud sin Login ⭐
```
URL: https://gmao-sistema-2025.ew.r.appspot.com/solicitudes

Pasos:
1. Acceder sin estar logueado
2. Completar formulario:
   - Nombre: Juan Usuario
   - Email: juan@example.com
   - Teléfono: 600123456
   - Ubicación: Oficina 3
   - Descripción: Aire acondicionado no enfría
3. Adjuntar 2 fotos (JPG)
4. Enviar

Resultado Esperado:
✅ Solicitud creada sin login
✅ Número único asignado (SOL-0001)
✅ Email confirmación a juan@example.com
✅ Email notificación a admins
✅ Archivos subidos correctamente
✅ Preview de fotos funcionando
```

#### Test 22: Enlace Directo desde Login ⭐ NUEVO
```
Pasos:
1. Ir a página de login (sin estar logueado)
2. Ver botón "Solicitar Servicio de Mantenimiento"
3. Click en el botón

Resultado Esperado:
✅ Redirección a /solicitudes/nueva
✅ Formulario carga correctamente
✅ Efecto hover del botón (gradiente azul)
✅ Mensaje "No necesitas iniciar sesión" visible

Estado: 🟡 PENDIENTE DE DESPLEGAR
```

#### Test 23: Conversión a Orden de Trabajo
```
Pasos:
1. Como admin, ir a /solicitudes/admin
2. Abrir SOL-0001
3. Click "Convertir a Orden de Trabajo"
4. Asignar técnico y fecha
5. Confirmar

Resultado Esperado:
✅ Orden creada (OT-0003)
✅ Solicitud marcada como "Procesada"
✅ Link entre solicitud y orden
✅ Email a solicitante con número de orden
```

---

### 1.7 Proveedores

#### Test 24: CRUD Proveedores
```
Operaciones:
1. Crear: Proveedor A, CIF: A12345678
2. Editar: Cambiar teléfono
3. Ver: Historial de compras
4. Eliminar: Solo si no tiene movimientos

Resultado Esperado:
✅ Todas las operaciones funcionan
✅ Validación de CIF/NIF
✅ No se puede eliminar con compras asociadas
```

---

### 1.8 Usuarios y Roles

#### Test 25: Gestión de Usuarios
```
Pasos:
1. Como admin, ir a /usuarios
2. Crear usuario:
   - Username: tecnico1
   - Password: password123
   - Email: tecnico1@gmao.com
   - Rol: Técnico
3. Logout y login como tecnico1

Resultado Esperado:
✅ Usuario creado
✅ Password hasheado (bcrypt)
✅ Email único validado
✅ Solo ve módulos de su rol
```

---

## 2. PRUEBAS DE SEGURIDAD 🔒

### Test 26: SQL Injection
```
Pasos:
1. En login, intentar:
   - Username: admin' OR '1'='1
   - Password: ' OR '1'='1

2. En búsqueda de activos:
   - Buscar: '; DROP TABLE activos; --

Resultado Esperado:
✅ NO ejecuta código SQL malicioso
✅ Uso de ORM (SQLAlchemy) previene inyección
✅ Inputs sanitizados
```

### Test 27: XSS (Cross-Site Scripting)
```
Pasos:
1. Crear activo con nombre:
   <script>alert('XSS')</script>

2. Crear comentario en orden:
   <img src=x onerror="alert('XSS')">

Resultado Esperado:
✅ Script NO se ejecuta
✅ HTML escapado automáticamente (Jinja2)
✅ Se muestra como texto plano
```

### Test 28: CSRF (Cross-Site Request Forgery)
```
Pasos:
1. Inspeccionar formulario de creación de activo
2. Verificar presencia de token CSRF
3. Intentar enviar formulario sin token válido

Resultado Esperado:
✅ Token CSRF presente en todos los formularios
✅ Request sin token → 400 Bad Request
✅ Token rotado en cada petición
```

### Test 29: Sesiones Seguras
```
Verificar:
1. Cookies con flag HttpOnly
2. Cookies con flag Secure (HTTPS)
3. Session timeout configurado

Comandos (DevTools → Application → Cookies):
- SESSION_COOKIE_HTTPONLY: True
- SESSION_COOKIE_SECURE: True (producción)
- Max-Age: No existe (sesión del navegador)

Resultado Esperado:
✅ Cookies no accesibles desde JavaScript
✅ HTTPS obligatorio en producción
✅ Sesión expira al cerrar navegador
```

### Test 30: Protección de Endpoints API
```
Pasos:
1. Sin login, intentar:
   GET /api/activos
   POST /api/ordenes
   DELETE /api/usuarios/1

Resultado Esperado:
✅ 401 Unauthorized en todos
✅ Requiere autenticación
✅ Logs de intentos de acceso
```

### Test 31: Fuerza Bruta Login
```
Pasos:
1. Intentar login fallido 5 veces consecutivas
2. Verificar respuesta

Resultado Esperado (Opcional - implementar):
✅ Captcha después de 3 intentos
✅ Bloqueo temporal después de 5 intentos
✅ Log de intentos sospechosos
```

### Test 32: Subida de Archivos Maliciosos
```
Pasos:
1. Intentar subir archivo .exe
2. Intentar subir archivo .php
3. Intentar subir archivo >10MB
4. Renombrar malware.exe → malware.jpg

Resultado Esperado:
✅ Solo extensiones permitidas (jpg, png, pdf, doc)
✅ Validación de tamaño (max 10MB)
✅ Validación de MIME type (no solo extensión)
✅ Filename sanitizado (secure_filename)
```

---

## 3. PRUEBAS DE RENDIMIENTO ⚡

### Test 33: Carga de Página
```
Herramienta: Google Lighthouse

Métricas objetivo:
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Total Blocking Time: < 300ms
- Cumulative Layout Shift: < 0.1

Ejecutar:
1. DevTools → Lighthouse
2. Modo: Desktop/Mobile
3. Categorías: Performance, Accessibility, SEO

Resultado Esperado:
✅ Performance Score > 80
✅ Accessibility Score > 90
✅ SEO Score > 90
```

### Test 34: Carga con Muchos Registros
```
Preparación:
1. Crear 1000 activos
2. Crear 500 órdenes
3. Crear 100 usuarios

Pruebas:
1. Cargar /activos
2. Buscar en listado
3. Aplicar filtros
4. Exportar a Excel

Resultado Esperado:
✅ Paginación funcional (50 items/página)
✅ Búsqueda < 1s
✅ Filtros < 500ms
✅ No carga todos los registros a la vez
```

### Test 35: Prueba de Estrés (Load Testing)
```
Herramienta: Apache JMeter o Locust

Escenarios:
1. 50 usuarios concurrentes navegando
2. 100 peticiones/segundo al API
3. 20 uploads simultáneos

Comandos (Locust):
```bash
pip install locust
# Crear locustfile.py con escenarios
locust -f locustfile.py --host=https://gmao-sistema-2025.ew.r.appspot.com
```

Resultado Esperado:
✅ Sin errores 500 con carga normal
✅ Tiempo de respuesta < 2s (p95)
✅ Auto-scaling funciona en GCP
```

### Test 36: Optimización de Consultas SQL
```
Herramienta: Flask-DebugToolbar (desarrollo)

Pasos:
1. Activar SQL logging
2. Cargar /dashboard
3. Revisar número de queries

app.config['SQLALCHEMY_ECHO'] = True

Resultado Esperado:
✅ No hay N+1 queries
✅ Uso de joins en relaciones
✅ Índices en columnas buscadas
✅ < 10 queries por página
```

---

## 4. PRUEBAS DE UX/UI 🎨

### Test 37: Responsive Design
```
Dispositivos:
- Mobile: 375px × 667px (iPhone SE)
- Tablet: 768px × 1024px (iPad)
- Desktop: 1920px × 1080px

Pasos:
1. Abrir DevTools → Responsive Design Mode
2. Probar todas las páginas en cada tamaño

Resultado Esperado:
✅ Sidebar colapsable en mobile
✅ Tablas scrollables horizontalmente
✅ Botones touch-friendly (min 44×44px)
✅ No overflow horizontal
✅ Texto legible sin zoom
```

### Test 38: Navegación y Flujos
```
Flujo: Crear orden de trabajo completa

Pasos:
1. Dashboard → Ver alerta "Stock bajo"
2. Click en alerta → Ver artículo
3. Crear orden de reposición
4. Asignar técnico
5. Completar orden
6. Verificar stock actualizado

Resultado Esperado:
✅ Flujo intuitivo, máximo 5 clicks
✅ Breadcrumbs visible
✅ Botones "Volver" funcionales
✅ Sin callejones sin salida
```

### Test 39: Feedback Visual
```
Acciones que requieren feedback:
1. Crear registro → Mensaje éxito + color verde
2. Eliminar → Mensaje confirmación + color rojo
3. Editar → Mensaje guardado + color azul
4. Error → Mensaje error + color rojo
5. Loading → Spinner visible

Resultado Esperado:
✅ Feedback inmediato en todas las acciones
✅ Mensajes desaparecen automáticamente (5s)
✅ Colores consistentes (success/warning/danger)
✅ Spinners durante operaciones largas
```

### Test 40: Accesibilidad (a11y)
```
Herramienta: WAVE, axe DevTools

Verificar:
1. Todos los inputs tienen <label>
2. Contraste de colores WCAG AA (4.5:1)
3. Navegación por teclado funciona
4. Alt text en imágenes
5. ARIA labels en iconos

Resultado Esperado:
✅ 0 errores críticos de accesibilidad
✅ Navegación completa con Tab/Enter
✅ Screen readers compatibles
✅ Focus visible en elementos interactivos
```

---

## 5. PRUEBAS DE INTEGRACIÓN 🔗

### Test 41: Email SMTP (Gmail Enterprise)
```
Configuración:
- MAIL_SERVER: smtp.gmail.com
- MAIL_PORT: 587
- MAIL_USERNAME: j_hidalgo@disfood.com

Escenarios:
1. Nueva solicitud → Email a admin
2. Orden asignada → Email a técnico
3. Stock bajo → Email a compras
4. Orden completada → Email a solicitante

Resultado Esperado:
✅ Emails enviados correctamente
✅ Sin errores de encoding UTF-8
✅ Formato HTML correcto
✅ Remitente correcto (no spam)
```

### Test 42: Integración con Cloud SQL
```
Pasos:
1. Verificar conexión desde App Engine
2. Ejecutar query complejo (JOIN múltiples tablas)
3. Verificar transacciones (COMMIT/ROLLBACK)
4. Probar pool de conexiones

Comandos:
```python
# En Cloud Shell
gcloud sql connect gmao-postgres --user=gmao-user
SELECT COUNT(*) FROM activo;
SELECT COUNT(*) FROM orden_trabajo;
```

Resultado Esperado:
✅ Conexión estable
✅ Queries < 100ms
✅ Pool de conexiones eficiente
✅ No hay leaks de conexión
```

### Test 43: Upload a Cloud Storage (Futuro)
```
Nota: Actualmente archivos en /tmp (temporal)

Migración recomendada:
1. Crear bucket: gmao-uploads
2. Configurar CORS
3. Modificar upload_handler

Resultado Esperado (Post-migración):
✅ Archivos persisten entre deployments
✅ URLs firmadas para descarga segura
✅ CDN para servir archivos rápido
```

---

## 6. PRUEBAS DE DATOS 📊

### Test 44: Integridad de Datos
```
Verificar Foreign Keys:

1. Eliminar activo con órdenes → Debe fallar
2. Eliminar usuario con órdenes asignadas → Reasignar o fallar
3. Eliminar proveedor con compras → Debe fallar

Resultado Esperado:
✅ Integridad referencial respetada
✅ ON DELETE CASCADE donde corresponda
✅ Mensajes de error claros
```

### Test 45: Validación de Formularios
```
Casos de prueba:
1. Email inválido: "usuario@com"
2. Teléfono inválido: "abc123"
3. Fecha pasada en orden planificada
4. Stock negativo
5. Precio negativo
6. Campos requeridos vacíos

Resultado Esperado:
✅ Validación frontend (JavaScript)
✅ Validación backend (Flask-WTF)
✅ Mensajes de error específicos
✅ Campos marcados en rojo
```

### Test 46: Migración de Datos
```
Escenario: Migrar desde Excel a GMAO

Pasos:
1. Preparar CSV con activos
2. Crear script de importación
3. Ejecutar import masivo
4. Verificar consistencia

Script ejemplo:
```python
import pandas as pd
from app import create_app, db
from app.models.activo import Activo

app = create_app()
with app.app_context():
    df = pd.read_csv('activos.csv')
    for _, row in df.iterrows():
        activo = Activo(
            codigo=row['codigo'],
            nombre=row['nombre'],
            tipo=row['tipo']
        )
        db.session.add(activo)
    db.session.commit()
```

Resultado Esperado:
✅ Datos importados sin pérdidas
✅ Formatos convertidos correctamente
✅ Log de errores si hay registros inválidos
```

---

## 7. PRUEBAS DE EMAIL 📧

### Test 47: Plantillas de Email
```
Verificar HTML:
1. Nueva solicitud → admin
2. Orden asignada → técnico
3. Orden completada → solicitante
4. Stock bajo → compras

Elementos a verificar:
- Logo empresa
- Formato responsive
- Botones call-to-action
- Información completa
- Firma profesional
- Links funcionando

Resultado Esperado:
✅ HTML renderiza en Gmail, Outlook
✅ Mobile-friendly
✅ No va a spam
✅ Texto alternativo (plain text) incluido
```

### Test 48: Email con Caracteres Especiales
```
Pasos:
1. Crear solicitud con descripción:
   "El compresor hace mucho ruido (ñoño)"
2. Verificar email recibido

Resultado Esperado:
✅ Caracteres españoles (ñ, á, é, etc.) correctos
✅ No errores de encoding
✅ Fix con send_message() aplicado ✅
```

---

## 8. PRUEBAS DE INFRAESTRUCTURA ☁️

### Test 49: Auto-Scaling
```
Simular carga alta:

Herramienta: Apache Bench
```bash
ab -n 1000 -c 50 https://gmao-sistema-2025.ew.r.appspot.com/
```

Resultado Esperado:
✅ GCP crea instancias adicionales automáticamente
✅ Tiempo de respuesta se mantiene < 3s
✅ No errores 503 (Service Unavailable)
✅ Scaling down cuando baja carga
```

### Test 50: Backups Automáticos
```
Verificar Cloud SQL backups:

Comandos:
```bash
gcloud sql backups list --instance=gmao-postgres
```

Resultado Esperado:
✅ Backup diario automático
✅ Retención 7 días
✅ Posibilidad de restaurar backup

Prueba de restauración (staging):
1. Crear instancia temporal
2. Restaurar backup más reciente
3. Verificar datos
```

### Test 51: Logs y Monitoreo
```
Google Cloud Logging:

Comandos:
```bash
gcloud app logs tail -s default
gcloud app logs read --limit=50
```

Verificar logs de:
- Errores 500
- Intentos de login fallidos
- Queries lentas
- Excepciones Python

Resultado Esperado:
✅ Logs centralizados
✅ Filtros funcionales
✅ Alertas configuradas (opcional)
✅ Retención 30 días
```

### Test 52: SSL/HTTPS
```
Herramienta: SSL Labs (https://www.ssllabs.com/ssltest/)

Verificar:
1. Certificado válido
2. Protocolo TLS 1.2+
3. Cifrado fuerte
4. HSTS header
5. No mixed content (HTTP en HTTPS)

Resultado Esperado:
✅ Rating A o superior
✅ Certificado renovado automáticamente (Google)
✅ Redirect HTTP → HTTPS
```

---

## 9. PRUEBAS DE REGRESIÓN 🔄

### Test 53: Funcionalidades Previas
```
Después de cada deployment, verificar:

Checklist rápido (10 min):
□ Login funciona
□ Dashboard carga
□ Crear activo
□ Crear orden
□ Subir archivo a solicitud
□ Email se envía
□ Logout funciona

Automatizar con Selenium:
```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://gmao-sistema-2025.ew.r.appspot.com/")
driver.find_element_by_id("username").send_keys("admin")
driver.find_element_by_id("password").send_keys("admin123")
driver.find_element_by_id("submit").click()
assert "Dashboard" in driver.title
```

Resultado Esperado:
✅ Todas las funcionalidades previas siguen funcionando
✅ No hay efectos colaterales de nuevos cambios
```

---

## 10. PRUEBAS DE ACCESIBILIDAD ♿

### Test 54: Navegación por Teclado
```
Pasos:
1. No usar mouse
2. Navegar con Tab, Enter, Esc
3. Completar formulario de login
4. Crear orden de trabajo

Resultado Esperado:
✅ Todos los elementos accesibles por teclado
✅ Focus visible (outline azul)
✅ Tab order lógico
✅ Modals se abren/cierran con teclado
```

### Test 55: Screen Readers
```
Herramienta: NVDA (Windows) o VoiceOver (Mac)

Verificar:
1. Encabezados correctamente etiquetados (h1, h2)
2. Formularios con labels descriptivos
3. Tablas con headers
4. Botones con texto descriptivo (no solo icono)
5. Alertas anunciadas

Resultado Esperado:
✅ Navegación completa con screen reader
✅ Contenido semántico (no solo divs)
✅ ARIA landmarks donde corresponda
```

---

## 11. PRUEBAS ADICIONALES RECOMENDADAS 🚀

### Test 56: Multi-Browser
```
Navegadores a probar:
- Chrome 118+ ✅
- Firefox 119+ ✅
- Safari 17+ (Mac/iOS) ⚠️
- Edge 118+ ✅

Resultado Esperado:
✅ Funcionalidad consistente
✅ CSS compatible
✅ JavaScript funciona
```

### Test 57: PWA (Progressive Web App) - Futuro
```
Convertir a PWA para uso offline:

Implementar:
1. Service Worker
2. manifest.json
3. Cache API para recursos estáticos
4. Sync API para órdenes offline

Resultado Esperado:
✅ Instalable en mobile
✅ Funciona offline (modo lectura)
✅ Sincroniza cuando vuelve online
```

### Test 58: API REST Documentación
```
Herramienta: Swagger/OpenAPI

Implementar:
```python
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint)
```

Resultado Esperado:
✅ Documentación automática de endpoints
✅ Pruebas interactivas desde Swagger UI
✅ Esquemas de request/response
```

### Test 59: Auditoría de Seguridad
```
Herramientas:
- OWASP ZAP
- Burp Suite
- Safety (Python dependencies)

Comandos:
```bash
pip install safety
safety check --json
```

Resultado Esperado:
✅ No vulnerabilidades conocidas en dependencias
✅ Headers de seguridad correctos
✅ No credenciales expuestas en código
```

### Test 60: Pruebas de Disaster Recovery
```
Escenarios:
1. Database down → App muestra error amigable
2. Cloud Storage down → Upload falla gracefully
3. Email server down → Queue de reintentos

Pasos:
1. Simular caída de Cloud SQL
2. Intentar acceder a la app

Resultado Esperado:
✅ No errores 500
✅ Mensaje: "Servicio temporalmente no disponible"
✅ App se recupera automáticamente al volver servicio
```

---

## 📊 CHECKLIST DE DESPLIEGUE

Antes de cada deployment a producción:

### Pre-Deployment
- [ ] Todos los tests unitarios pasan
- [ ] Tests de integración OK
- [ ] Revisión de código (code review)
- [ ] Changelog actualizado
- [ ] Variables de entorno verificadas
- [ ] Backup manual de BD

### Post-Deployment
- [ ] Login funciona
- [ ] Dashboard carga
- [ ] Crear registro de prueba
- [ ] Email se envía
- [ ] Logs sin errores
- [ ] Performance aceptable (< 2s)
- [ ] Versión correcta en footer

### Rollback Plan
Si algo falla:
```bash
# Revertir a versión anterior
gcloud app versions list
gcloud app services set-traffic default --splits=VERSION_ANTERIOR=1
```

---

## 🧪 HERRAMIENTAS RECOMENDADAS

### Testing
- **Pytest**: Tests unitarios Python
- **Selenium**: Tests E2E automatizados
- **Locust**: Load testing
- **Postman**: Tests de API

### Seguridad
- **OWASP ZAP**: Security scanning
- **Safety**: Vulnerabilidades Python
- **Snyk**: Monitoreo continuo

### Performance
- **Google Lighthouse**: Auditoría web
- **GTmetrix**: Performance analysis
- **New Relic**: APM (opcional, €€€)

### Monitoreo
- **Google Cloud Monitoring**: Métricas GCP
- **Sentry**: Error tracking (opcional)
- **Uptime Robot**: Availability monitoring

---

## 📝 REGISTRO DE PRUEBAS

### Formato de Reporte

```markdown
## Test #XX: [Nombre del Test]

**Fecha**: 2025-10-02  
**Ejecutado por**: [Nombre]  
**Entorno**: Producción / Staging  
**Versión**: 20251002t200236  

**Pasos**:
1. [Paso 1]
2. [Paso 2]

**Resultado**: ✅ PASS / ❌ FAIL  
**Notas**: [Observaciones]  
**Evidencia**: [Screenshot/Log]  
```

### Estado Actual de Tests

| Test | Estado | Fecha | Notas |
|------|--------|-------|-------|
| Test 1-25 | ✅ PASS | 2025-10-02 | Funcionales OK |
| Test 26-32 | 🟡 PARCIAL | 2025-10-02 | Seguridad básica OK |
| Test 33-36 | ⚪ NO REALIZADO | - | Performance pending |
| Test 37-40 | 🟡 PARCIAL | 2025-10-02 | UX básico OK |
| Test 41 | ✅ PASS | 2025-10-02 | Email UTF-8 fixed |
| Test 42 | ✅ PASS | 2025-10-02 | Cloud SQL OK |
| Test 43 | ⏳ FUTURO | - | Migrar a Cloud Storage |

---

## 🎯 PRÓXIMOS PASOS RECOMENDADOS

### Corto Plazo (Esta semana)
1. ✅ Test 3: Logout al cerrar navegador (desplegar)
2. ✅ Test 22: Enlace directo en login (desplegar)
3. ⚪ Test 33: Performance Lighthouse
4. ⚪ Test 37: Responsive design completo
5. ⚪ Test 41: Verificar emails en diferentes clientes

### Medio Plazo (Este mes)
6. ⚪ Test 43: Migrar archivos a Cloud Storage
7. ⚪ Test 49: Pruebas de auto-scaling
8. ⚪ Test 53: Automatizar tests de regresión (Selenium)
9. ⚪ Test 58: Documentar API con Swagger
10. ⚪ Test 31: Implementar protección fuerza bruta

### Largo Plazo (3 meses)
11. ⚪ Test 57: Convertir a PWA
12. ⚪ Test 59: Auditoría seguridad completa
13. ⚪ Test 60: Plan de disaster recovery
14. ⚪ Integración continua (CI/CD con GitHub Actions)
15. ⚪ Tests automatizados en cada commit

---

**Documento creado**: 2 de octubre de 2025  
**Última actualización**: 2 de octubre de 2025  
**Versión**: 1.0  
**Autor**: Sistema GMAO Testing Team
