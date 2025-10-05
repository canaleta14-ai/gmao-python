# 🚀 Guía de Despliegue - Subida de Archivos en Solicitudes

## ✅ Estado Actual
- ✅ Migración probada localmente con SQLite
- ✅ Script compatible con PostgreSQL y SQLite
- ✅ Todos los cambios de código completados

## 📦 Archivos Modificados para Despliegue

### Modelos (app/models/)
1. `archivo_adjunto.py` - Soporte para solicitudes
2. `solicitud_servicio.py` - Relación con archivos

### Controladores (app/routes/)
3. `solicitudes.py` - Procesamiento de archivos

### Templates (app/templates/solicitudes/)
4. `nueva_solicitud.html` - Formulario con campo de archivos

### Scripts
5. `migrate_solicitud_archivos.py` - Migración de BD

## 🎯 Pasos de Despliegue a Producción

### 1. Ejecutar Migración en Cloud SQL (PostgreSQL)

```bash
# Desde tu PC local, ejecutar:
python migrate_solicitud_archivos.py
```

**Nota:** El script detectará automáticamente PostgreSQL en producción.

### 2. Desplegar Aplicación a App Engine

```bash
# Configurar PATH de gcloud
$env:PATH += ";C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"

# Desplegar
gcloud app deploy app.yaml --project=gmao-sistema-2025 --quiet
```

### 3. Verificar Logs

```bash
# Ver logs en tiempo real
gcloud app logs tail --service=default --project=gmao-sistema-2025

# Ver logs recientes
gcloud app logs read --limit=50 --project=gmao-sistema-2025
```

## 🧪 Testing en Producción

1. **Abrir la aplicación:**
   - URL: https://gmao-sistema-2025.ew.r.appspot.com
   - Ir a "Solicitud de Servicio"

2. **Probar subida de archivos:**
   - Completar formulario
   - Adjuntar 1-3 fotos (JPG/PNG)
   - Verificar preview
   - Enviar solicitud

3. **Verificar en admin:**
   - Login como admin
   - Ver solicitudes
   - Confirmar que archivos se guardaron

## ⚠️ Consideraciones Importantes

### Cloud Storage
Los archivos se guardarán en el sistema de archivos de App Engine, que es **efímero**. Para producción real, considera migrar a Cloud Storage:

```python
# TODO: Migrar a Cloud Storage Bucket
# upload_folder = 'gs://gmao-archivos/solicitudes/'
```

### Cuotas de App Engine
- Almacenamiento local limitado
- Para más de 100 solicitudes/día con fotos, usar Cloud Storage

### Backups
Los archivos en el sistema de archivos de App Engine se pierden al redesplegar. **Usar Cloud Storage para persistencia.**

## 📋 Checklist de Despliegue

- [ ] Migración ejecutada en Cloud SQL
- [ ] Aplicación desplegada
- [ ] Logs revisados (sin errores)
- [ ] Test de subida de 1 archivo
- [ ] Test de subida de múltiples archivos
- [ ] Test de formatos variados (JPG, PNG, PDF)
- [ ] Verificar archivos en servidor
- [ ] Verificar registros en base de datos

## 🔄 Rollback (si algo falla)

Si necesitas revertir los cambios:

1. **Revertir a versión anterior:**
```bash
gcloud app versions list --project=gmao-sistema-2025
gcloud app services set-traffic default --splits VERSION_ANTERIOR=1 --project=gmao-sistema-2025
```

2. **Revertir migración de BD (si es necesario):**
```sql
-- Conectar a Cloud SQL
ALTER TABLE archivo_adjunto DROP COLUMN solicitud_servicio_id;
```

## 💡 Mejoras Futuras

1. [ ] Migrar a Cloud Storage Bucket
2. [ ] Compresión automática de imágenes
3. [ ] Thumbnails para preview
4. [ ] Galería de imágenes en vista de solicitud
5. [ ] Descarga de archivos
6. [ ] Eliminación de archivos individuales
7. [ ] Integración con Cloud Vision AI (análisis de imágenes)

## 📞 Soporte

Si encuentras problemas:
1. Revisar logs: `gcloud app logs read`
2. Verificar que migración se ejecutó
3. Comprobar permisos de escritura en filesystem
4. Validar que `UPLOAD_FOLDER` está configurado
