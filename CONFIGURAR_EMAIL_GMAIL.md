# 📧 Configuración de Email Gmail para GMAO

## 🎯 Problema Identificado
Los emails no se envían porque falta la contraseña de aplicación de Gmail en Google Cloud Secret Manager.

## ✅ Solución Implementada
1. ✅ Creado el secret `gmao-mail-password` en Google Cloud Platform
2. ✅ Configurados los permisos para que App Engine pueda acceder al secret
3. ⚠️ **PENDIENTE**: Configurar la contraseña de aplicación de Gmail real

## 🔧 Pasos para Completar la Configuración

### Paso 1: Crear Contraseña de Aplicación de Gmail

1. **Accede a tu cuenta de Google**: https://myaccount.google.com/
2. **Ve a Seguridad** en el menú lateral izquierdo
3. **Habilita la verificación en dos pasos** (si no está habilitada):
   - En "Acceso a Google", busca "Verificación en dos pasos"
   - Sigue las instrucciones para configurarla
4. **Crear contraseña de aplicación**:
   - Una vez habilitada la verificación en dos pasos
   - Busca "Contraseñas de aplicaciones" en la misma sección
   - Haz clic en "Contraseñas de aplicaciones"
   - Selecciona:
     - **Aplicación**: Correo
     - **Dispositivo**: Otro (nombre personalizado)
     - Escribe: "GMAO Sistema Mantenimiento"
   - Haz clic en **Generar**
5. **Copia la contraseña**: Google te mostrará una contraseña de 16 caracteres
   - Ejemplo: `abcd efgh ijkl mnop`
   - **GUARDA ESTA CONTRASEÑA** - la necesitarás en el siguiente paso

### Paso 2: Actualizar el Secret en Google Cloud Platform

Ejecuta este comando reemplazando `TU_PASSWORD_DE_APLICACION` con la contraseña que generaste:

```powershell
# Actualizar el secret con la contraseña real de Gmail
echo "TU_PASSWORD_DE_APLICACION" | gcloud secrets versions add gmao-mail-password --data-file=-
```

**Ejemplo:**
```powershell
# Si tu contraseña es: abcd efgh ijkl mnop
echo "abcd efgh ijkl mnop" | gcloud secrets versions add gmao-mail-password --data-file=-
```

### Paso 3: Verificar la Configuración

```powershell
# Verificar que el secret se actualizó correctamente
gcloud secrets versions list gmao-mail-password

# Desplegar la aplicación para que use el nuevo secret
gcloud app deploy --quiet
```

### Paso 4: Probar el Envío de Emails

1. **Accede a la aplicación**: https://mantenimiento-470311.ew.r.appspot.com
2. **Crea una nueva solicitud de servicio**
3. **Verifica que lleguen los emails**:
   - Email de confirmación al solicitante
   - Email de notificación al administrador (j_hidalgo@disfood.com)

## 📋 Configuración Actual

- **Email del sistema**: j_hidalgo@disfood.com
- **Servidor SMTP**: smtp.gmail.com:587 (TLS)
- **Secret en GCP**: `gmao-mail-password` ✅ Creado
- **Permisos**: ✅ Configurados para App Engine

## 🔍 Verificación de Logs

Si después de configurar la contraseña los emails siguen sin enviarse, revisa los logs:

```powershell
# Ver logs de la aplicación en tiempo real
gcloud app logs tail -s default

# Ver logs específicos de errores de email
gcloud app logs read --filter="severity>=ERROR" --limit=50
```

## 🚨 Importante

- **NUNCA** compartas la contraseña de aplicación por email o chat
- **NUNCA** la subas a GitHub o repositorios públicos
- Si crees que la contraseña fue comprometida, revócala y genera una nueva
- La contraseña de aplicación es específica para esta aplicación y puede revocarse en cualquier momento

## 📞 Soporte

Si tienes problemas con la configuración:
1. Verifica que la verificación en dos pasos esté habilitada
2. Asegúrate de usar la contraseña de aplicación, no tu contraseña normal de Gmail
3. Revisa los logs de la aplicación para errores específicos