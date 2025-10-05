# Implementación de Subida de Archivos en Solicitudes de Servicio

## 📋 Resumen de Cambios

Se ha implementado la funcionalidad para adjuntar fotos y documentos del problema al crear una solicitud de servicio.

## 🔧 Archivos Modificados

### 1. **Modelos** (`app/models/`)

#### `archivo_adjunto.py`
- ✅ Agregado campo `solicitud_servicio_id` (opcional, FK a `solicitud_servicio`)
- ✅ Modificado `orden_trabajo_id` para ser opcional (nullable=True)
- ✅ Actualizado método `to_dict()` para incluir `solicitud_servicio_id`

#### `solicitud_servicio.py`
- ✅ Agregada relación `archivos` con ArchivoAdjunto
- ✅ Configurado cascade "all, delete-orphan" para eliminar archivos al borrar solicitud

### 2. **Controladores** (`app/routes/`)

#### `solicitudes.py`
- ✅ Importados módulos necesarios:
  - `ArchivoAdjunto` (modelo)
  - `secure_filename` (werkzeug)
  - `uuid` (generación de nombres únicos)
  
- ✅ Agregadas constantes de configuración:
  ```python
  ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
  MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
  ```

- ✅ Nueva función `allowed_file(filename)`:
  - Valida extensiones permitidas

- ✅ Nueva función `procesar_archivos_solicitud(archivos, solicitud_id)`:
  - Valida archivos (extensión y tamaño)
  - Genera nombres únicos con UUID
  - Guarda archivos en `static/uploads/solicitudes/{solicitud_id}/`
  - Crea registros en base de datos
  - Maneja errores de forma robusta
  - Retorna cantidad de archivos guardados

- ✅ Modificada función `procesar_solicitud()`:
  - Usa `db.session.flush()` para obtener ID antes de commit
  - Procesa archivos con `request.files.getlist('archivos')`
  - Actualiza mensaje de confirmación con cantidad de archivos adjuntados

### 3. **Templates** (`app/templates/solicitudes/`)

#### `nueva_solicitud.html`
- ✅ Agregado `enctype="multipart/form-data"` al formulario
- ✅ Nuevo campo de subida de archivos:
  ```html
  <input type="file" class="form-control" id="archivos" 
         name="archivos" multiple accept="image/*,.pdf,.doc,.docx">
  ```
- ✅ Vista previa de archivos seleccionados (thumbnails para imágenes)
- ✅ Validación JavaScript en cliente:
  - Máximo 5 archivos
  - Máximo 10 MB por archivo
  - Preview visual de imágenes
  - Iconos para documentos PDF/DOC

### 4. **Migración de Base de Datos**

#### `migrate_solicitud_archivos.py`
Script de migración que:
- ✅ Modifica `orden_trabajo_id` para permitir NULL
- ✅ Agrega columna `solicitud_servicio_id`
- ✅ Crea clave foránea con CASCADE DELETE
- ✅ Agrega índice para optimización
- ✅ Verifica si ya fue aplicada (idempotente)

## 📂 Estructura de Archivos

Los archivos se guardan en:
```
static/uploads/solicitudes/{solicitud_id}/
  ├── 1a2b3c4d_foto_problema.jpg
  ├── 5e6f7g8h_documento.pdf
  └── ...
```

## ✨ Características Implementadas

1. **Subida Múltiple**: Hasta 5 archivos por solicitud
2. **Validación de Tamaño**: Máximo 10 MB por archivo
3. **Formatos Soportados**: JPG, PNG, GIF, PDF, DOC, DOCX
4. **Preview en Tiempo Real**: Vista previa de imágenes antes de enviar
5. **Nombres Únicos**: UUID para evitar colisiones
6. **Seguridad**: Uso de `secure_filename()` contra ataques
7. **Organización**: Archivos separados por solicitud
8. **Feedback Visual**: Contador de archivos adjuntados
9. **Manejo de Errores**: Validación robusta

## 🚀 Cómo Usar

### Para Usuarios:
1. Ir a "Solicitud de Servicio"
2. Llenar el formulario
3. Hacer clic en "Fotos del Problema (Opcional)"
4. Seleccionar hasta 5 archivos (imágenes o documentos)
5. Ver preview de los archivos seleccionados
6. Enviar la solicitud

### Para Desarrolladores:

1. **Ejecutar Migración:**
   ```bash
   python migrate_solicitud_archivos.py
   ```

2. **Verificar en Producción:**
   ```python
   from app.models import SolicitudServicio
   solicitud = SolicitudServicio.query.first()
   print(f"Archivos: {len(solicitud.archivos)}")
   for archivo in solicitud.archivos:
       print(f"  - {archivo.nombre_original} ({archivo.tamaño} bytes)")
   ```

3. **Desplegar Cambios:**
   ```bash
   # Copiar archivos modificados
   # Ejecutar migración en producción
   python migrate_solicitud_archivos.py
   
   # Reiniciar aplicación (si es necesario)
   ```

## 📊 Impacto en Base de Datos

### Tabla `archivo_adjunto`:
- **Antes**: Solo relacionada con `orden_trabajo`
- **Después**: Relacionada con `orden_trabajo` **Y** `solicitud_servicio`

### Compatibilidad:
- ✅ 100% compatible con archivos existentes de órdenes de trabajo
- ✅ No afecta funcionalidad existente
- ✅ Migración segura y reversible

## 🔐 Seguridad

- ✅ Validación de extensiones (whitelist)
- ✅ Validación de tamaño de archivo
- ✅ Sanitización de nombres con `secure_filename()`
- ✅ Nombres únicos (UUID) para evitar sobrescritura
- ✅ Validación en cliente y servidor
- ✅ Manejo seguro de errores

## 🎨 Interfaz de Usuario

- ✅ Diseño consistente con el resto de la aplicación
- ✅ Iconos Bootstrap Icons
- ✅ Preview visual de imágenes
- ✅ Iconos para documentos PDF/DOC
- ✅ Mensajes informativos
- ✅ Validación en tiempo real
- ✅ Responsive (funciona en móvil)

## 📝 Notas Técnicas

1. **Directorio de Uploads**: Se crea automáticamente si no existe
2. **CASCADE DELETE**: Los archivos se eliminan al borrar la solicitud
3. **Performance**: Índice creado en `solicitud_servicio_id`
4. **Límites**: Configurables en constantes del controlador
5. **MIME Types**: Detección automática por extensión

## ✅ Testing Recomendado

1. Crear solicitud sin archivos (debe funcionar)
2. Crear solicitud con 1 imagen
3. Crear solicitud con 5 imágenes
4. Crear solicitud con documentos PDF/DOC
5. Intentar subir más de 5 archivos (debe rechazar)
6. Intentar subir archivo >10 MB (debe rechazar)
7. Intentar subir extensión no permitida (debe rechazar)
8. Verificar que archivos se guardan correctamente
9. Verificar que registros se crean en BD
10. Verificar CASCADE DELETE al eliminar solicitud

## 🔄 Próximos Pasos Sugeridos

1. [ ] Agregar vista de archivos en detalles de solicitud (admin)
2. [ ] Permitir descargar archivos adjuntos
3. [ ] Agregar thumbnails en lista de solicitudes
4. [ ] Implementar galería de imágenes
5. [ ] Permitir eliminar archivos individuales
6. [ ] Agregar soporte para más formatos (Excel, etc.)
7. [ ] Implementar compresión de imágenes
8. [ ] Agregar watermark a imágenes
9. [ ] Integrar con Cloud Storage (GCP Storage)
10. [ ] Estadísticas de archivos por solicitud

## 📞 Soporte

Para dudas o problemas:
- Revisar logs en consola del servidor
- Verificar permisos de carpeta `static/uploads/`
- Comprobar que migración se ejecutó correctamente
- Validar configuración de `UPLOAD_FOLDER` en app config
