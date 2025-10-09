# Solución Completa del Problema de Envío de Emails

## 📧 Resumen del Problema

La aplicación GMAO tenía problemas para enviar emails de notificación debido a:

1. **Secret faltante**: El secret `gmao-mail-password` no existía en Google Cloud Platform
2. **Configuración incorrecta**: Variable `ADMIN_EMAIL` en lugar de `ADMIN_EMAILS` en `app.yaml`
3. **Permisos insuficientes**: El service account no tenía acceso al Secret Manager

## ✅ Solución Implementada

### 1. Creación del Secret en Google Cloud Platform

```bash
# Crear el secret con la contraseña de aplicación de Gmail
echo "dvematimfpjjpxji" | gcloud secrets create gmao-mail-password --data-file=-

# Otorgar permisos al service account de App Engine
gcloud secrets add-iam-policy-binding gmao-mail-password \
    --member="serviceAccount:mantenimiento-470311@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 2. Corrección de Configuración en app.yaml

**Antes:**
```yaml
ADMIN_EMAIL: j_hidalgo@disfood.com
```

**Después:**
```yaml
ADMIN_EMAILS: j_hidalgo@disfood.com
```

### 3. Configuración Final de Email

La configuración completa en `app.yaml`:

```yaml
# Configuración de email (Gmail/Google Workspace)
MAIL_SERVER: smtp.gmail.com
MAIL_PORT: "587"
MAIL_USE_TLS: "True"
MAIL_USERNAME: j_hidalgo@disfood.com
MAIL_PASSWORD: ""  # Se obtiene vía Secret Manager
ADMIN_EMAILS: j_hidalgo@disfood.com
```

### 4. Configuración en factory.py

El código en `factory.py` ya estaba correctamente configurado para obtener la contraseña desde Secret Manager:

```python
app.config["MAIL_PASSWORD"] = get_secret_or_env("gmao-mail-password", "MAIL_PASSWORD")
```

## 🧪 Verificación de la Solución

### 1. Prueba Local Exitosa

```bash
python test_email.py
# ✅ Email enviado exitosamente
```

### 2. Verificación en Producción

- ✅ Secret `gmao-mail-password` creado y accesible
- ✅ Permisos configurados correctamente
- ✅ Aplicación desplegada con nueva configuración
- ✅ Logs sin warnings de "No hay destinatarios configurados"
- ✅ Cron job ejecutándose correctamente

### 3. Logs de Verificación

```
2025-10-09 10:00:08 - app.routes.cron - INFO - PLAN CANDIDATO preparado: id=3
2025-10-09 10:00:08 - app.routes.cron - INFO - === FIN: Parche DB aplicado. Comandos ejecutados: 21, errores: 0 ===
```

## 📋 Configuración de Gmail

### Contraseña de Aplicación

La contraseña utilizada (`dvematimfpjjpxji`) es una **contraseña de aplicación de Gmail** generada específicamente para esta aplicación.

### Pasos para Generar Nueva Contraseña (si es necesario):

1. Ir a [Gestión de cuenta de Google](https://myaccount.google.com/)
2. Seguridad → Verificación en 2 pasos
3. Contraseñas de aplicaciones
4. Generar nueva contraseña para "GMAO Mantenimiento"
5. Actualizar el secret:

```bash
echo "NUEVA_CONTRASEÑA" | gcloud secrets versions add gmao-mail-password --data-file=-
```

## 🔧 Archivos Modificados

1. **app.yaml**: Corregida variable `ADMIN_EMAIL` → `ADMIN_EMAILS`
2. **Secrets en GCP**: Creado `gmao-mail-password` con permisos
3. **Scripts de prueba**: Creados para verificación

## 📊 Estado Final

| Componente | Estado | Descripción |
|------------|--------|-------------|
| Secret Manager | ✅ Configurado | `gmao-mail-password` creado y accesible |
| Permisos IAM | ✅ Configurado | Service account con acceso a secrets |
| Configuración Email | ✅ Corregida | Variables correctas en `app.yaml` |
| Despliegue | ✅ Completado | Aplicación actualizada en producción |
| Pruebas | ✅ Exitosas | Envío de emails funcionando |

## 🚀 Próximos Pasos

1. **Monitoreo**: Verificar regularmente los logs para asegurar el correcto funcionamiento
2. **Seguridad**: Rotar la contraseña de aplicación periódicamente
3. **Escalabilidad**: Considerar múltiples destinatarios en `ADMIN_EMAILS` si es necesario

## 📝 Notas Importantes

- Los emails se envían automáticamente cuando el cron job detecta órdenes de mantenimiento pendientes
- El endpoint `/api/cron/generar-ordenes-preventivas` está protegido y solo accesible desde Cloud Scheduler
- La configuración es compatible tanto con desarrollo local como producción en GCP

---

**Fecha de resolución**: 9 de octubre de 2025  
**Estado**: ✅ COMPLETADO  
**Responsable**: Sistema GMAO - Gestión de Mantenimiento