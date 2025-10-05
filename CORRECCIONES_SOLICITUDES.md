# Correcciones Implementadas - Solicitudes de Servicio

## 🐛 Problemas Encontrados y Solucionados

### 1. ❌ Error: Template Syntax Error (Jinja)
**Problema**: El template `nueva_solicitud.html` tenía un bloque `{% block extra_js %}` mal ubicado dentro del contenido HTML.

**Error**:
```
jinja2.exceptions.TemplateSyntaxError: Unexpected end of template. 
Jinja was looking for the following tags: 'endblock'
```

**Solución**: 
- Reorganizado el template para que el JavaScript esté al final del archivo
- Movido el bloque `{% block extra_js %}` después de `{% endblock %}` del contenido
- Consolidado todo el JavaScript en un solo bloque

**Archivos modificados**:
- `app/templates/solicitudes/nueva_solicitud.html`

---

### 2. ❌ Error: CSRF Token Missing
**Problema**: El formulario no incluía el token CSRF requerido por Flask-WTF.

**Error**:
```
400 Bad Request: The CSRF token is missing.
```

**Solución**: 
- Agregado campo oculto con token CSRF al formulario:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

**Archivos modificados**:
- `app/templates/solicitudes/nueva_solicitud.html`

---

### 3. ❌ Error: Read-only File System
**Problema**: App Engine tiene sistema de archivos de solo lectura, excepto `/tmp`.

**Error**:
```
[Errno 30] Read-only file system: '/workspace/uploads/solicitudes'
```

**Solución**: 
- Modificado `procesar_archivos_solicitud()` para detectar entorno de producción
- En producción: guardar archivos en `/tmp/uploads`
- En desarrollo: guardar en `static/uploads` (como antes)

**Código agregado**:
```python
if os.getenv("FLASK_ENV") == "production":
    upload_folder = "/tmp/uploads"
else:
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "static/uploads")
```

**Archivos modificados**:
- `app/routes/solicitudes.py`

**Nota importante**: 
⚠️ Los archivos en `/tmp` son **temporales** y se pierden al reiniciar la instancia.
💡 **Siguiente paso recomendado**: Migrar a Google Cloud Storage para persistencia permanente.

---

### 4. ❌ Error: Email Configuration Missing
**Problema**: No había configuración de email en variables de entorno, por lo que no se podían enviar notificaciones.

**Solución**: 
- Agregadas variables de entorno para configuración SMTP en `app.yaml`:
  - `MAIL_SERVER`
  - `MAIL_PORT`
  - `MAIL_USE_TLS`
  - `MAIL_USERNAME`
  - `MAIL_PASSWORD`
  - `ADMIN_EMAIL`

- Modificado `enviar_email_notificacion_admin()` para usar `ADMIN_EMAIL` como fallback si no hay admins en BD

**Archivos modificados**:
- `app.yaml`
- `app/utils/email_utils.py`

**Documentación creada**:
- `CONFIGURACION_EMAIL.md` - Guía completa para configurar Gmail

---

## 📋 Checklist de Configuración Pendiente

Para que el sistema funcione completamente, necesitas:

### ✅ Configuración de Email (CRÍTICO)

1. [ ] Generar contraseña de aplicación de Gmail
2. [ ] Editar `app.yaml` y reemplazar:
   - `MAIL_USERNAME: tu-email@gmail.com`
   - `MAIL_PASSWORD: tu-contraseña-de-aplicacion`
   - `ADMIN_EMAIL: tu-email@gmail.com`
3. [ ] Desplegar con el nuevo `app.yaml`

**Instrucciones detalladas**: Ver `CONFIGURACION_EMAIL.md`

### ⚠️ Migración a Cloud Storage (RECOMENDADO)

Los archivos actualmente se guardan en `/tmp`, que es temporal. Para producción:

1. [ ] Crear bucket de Cloud Storage
2. [ ] Modificar `procesar_archivos_solicitud()` para usar Cloud Storage
3. [ ] Actualizar permisos de la cuenta de servicio

### 🗄️ Migración de Base de Datos

La funcionalidad de archivos requiere la columna `solicitud_servicio_id` en la tabla `archivo_adjunto`:

1. [ ] Ejecutar migración en Cloud SQL:
```bash
python migrate_solicitud_archivos.py
```

---

## 🚀 Comandos de Despliegue

### Desplegar cambios actuales:
```powershell
gcloud app deploy app.yaml --project=gmao-sistema-2025 --quiet
```

### Ver logs:
```powershell
gcloud app logs tail --service=default --project=gmao-sistema-2025
```

### Ejecutar migración de BD:
```powershell
# Asegurarse de que DB_TYPE=postgresql en variables de entorno
python migrate_solicitud_archivos.py
```

---

## 📝 Resumen de Archivos Modificados

1. **app/templates/solicitudes/nueva_solicitud.html**
   - Reorganizado estructura de bloques Jinja
   - Agregado token CSRF
   - JavaScript consolidado al final

2. **app/routes/solicitudes.py**
   - Modificado para guardar archivos en `/tmp` en producción
   - Mantiene `static/uploads` para desarrollo

3. **app.yaml**
   - Agregadas variables de entorno para email
   - **REQUIERE EDICIÓN MANUAL** para agregar credenciales reales

4. **app/utils/email_utils.py**
   - Agregado fallback a `ADMIN_EMAIL` si no hay admins en BD

5. **Documentación creada**:
   - `CONFIGURACION_EMAIL.md` - Guía de configuración de email
   - `CORRECCIONES_SOLICITUDES.md` - Este archivo

---

## 🎯 Estado Actual

| Componente | Estado | Comentarios |
|------------|--------|-------------|
| Template HTML | ✅ Corregido | Sintaxis Jinja válida |
| Token CSRF | ✅ Agregado | Formulario seguro |
| Guardado de archivos | ⚠️ Temporal | Funciona pero archivos se pierden al reiniciar |
| Configuración email | ⏳ Pendiente | Requiere editar `app.yaml` con credenciales reales |
| Migración BD | ⏳ Pendiente | Necesita ejecutarse en Cloud SQL |

---

## ⏭️ Próximos Pasos

1. **INMEDIATO**: Configurar email en `app.yaml` y redesplegar
2. **IMPORTANTE**: Ejecutar migración de base de datos
3. **RECOMENDADO**: Migrar almacenamiento de archivos a Cloud Storage
4. **OPCIONAL**: Actualizar email del usuario admin en la BD

---

Fecha: 2 de octubre de 2025
Versión desplegada: 20251002t192747
