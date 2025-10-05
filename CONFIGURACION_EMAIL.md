# Configuración de Email para Notificaciones

## 🎯 Propósito
Este documento explica cómo configurar el envío de emails para las notificaciones de solicitudes de servicio.

## 📧 Configuración de Gmail

### Paso 1: Crear una Contraseña de Aplicación de Gmail

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Navega a **Seguridad** en el menú lateral
3. En "Acceso a Google", habilita la **Verificación en dos pasos** (si no está habilitada)
4. Una vez habilitada la verificación en dos pasos, busca **Contraseñas de aplicaciones**
5. Selecciona:
   - **Aplicación**: Correo
   - **Dispositivo**: Otro (nombre personalizado)
   - Escribe: "GMAO Sistema"
6. Haz clic en **Generar**
7. Google te mostrará una contraseña de 16 caracteres (ejemplo: `abcd efgh ijkl mnop`)
8. **GUARDA ESTA CONTRASEÑA** - la necesitarás en el siguiente paso

### Paso 2: Actualizar app.yaml

Edita el archivo `app.yaml` y reemplaza los siguientes valores:

```yaml
env_variables:
  # ... otras variables ...
  
  # Configuración de email
  MAIL_SERVER: smtp.gmail.com
  MAIL_PORT: "587"
  MAIL_USE_TLS: "True"
  MAIL_USERNAME: tucorreo@gmail.com  # ← CAMBIAR: Tu email de Gmail
  MAIL_PASSWORD: abcd efgh ijkl mnop  # ← CAMBIAR: La contraseña de aplicación que generaste
  ADMIN_EMAIL: tucorreo@gmail.com    # ← CAMBIAR: Email donde recibirás las notificaciones
```

**Ejemplo real:**
```yaml
  MAIL_USERNAME: mantenimiento@tuempresa.com
  MAIL_PASSWORD: xyzw abcd efgh ijkl
  ADMIN_EMAIL: admin@tuempresa.com
```

### Paso 3: Desplegar

Después de editar `app.yaml`, despliega la aplicación:

```powershell
gcloud app deploy app.yaml --project=gmao-sistema-2025 --quiet
```

## 🔍 Verificación

### 1. Envía una solicitud de prueba
- Ve a: https://gmao-sistema-2025.ew.r.appspot.com/solicitudes/
- Llena el formulario
- Envía la solicitud

### 2. Revisa los logs
```powershell
gcloud app logs read --limit=50 --project=gmao-sistema-2025 | Select-String "email|Email"
```

### 3. Verifica tu bandeja de entrada
Deberías recibir dos emails:
- **Email 1**: Confirmación al solicitante
- **Email 2**: Notificación al administrador (tu email)

## ⚠️ Solución de Problemas

### Error: "Authentication failed"
- Verifica que hayas habilitado la verificación en dos pasos en Gmail
- Asegúrate de usar una **contraseña de aplicación**, NO tu contraseña normal
- Copia la contraseña de aplicación SIN espacios

### Error: "MAIL_USERNAME not configured"
- Verifica que las variables estén en `app.yaml`
- Vuelve a desplegar después de editar `app.yaml`

### No llegan los emails
- Revisa la carpeta de spam
- Verifica los logs con el comando anterior
- Asegúrate de que `ADMIN_EMAIL` esté correctamente configurado

## 🔐 Seguridad

**IMPORTANTE**: 
- Nunca subas `app.yaml` con credenciales reales a un repositorio público
- La contraseña de aplicación es específica para esta app y puede revocarse en cualquier momento desde tu cuenta de Google
- Si crees que la contraseña fue comprometida, revócala y genera una nueva

## 📝 Notas Adicionales

### Usar otro proveedor de email (Outlook, Yahoo, etc.)

Si prefieres usar otro proveedor, cambia estas variables:

**Outlook/Hotmail:**
```yaml
MAIL_SERVER: smtp-mail.outlook.com
MAIL_PORT: "587"
MAIL_USERNAME: tucorreo@outlook.com
MAIL_PASSWORD: tu-contraseña
```

**Yahoo:**
```yaml
MAIL_SERVER: smtp.mail.yahoo.com
MAIL_PORT: "587"
MAIL_USERNAME: tucorreo@yahoo.com
MAIL_PASSWORD: tu-contraseña-de-aplicacion
```

### Actualizar el email del usuario admin en la base de datos

Para que las notificaciones también se envíen a los administradores registrados en el sistema:

```sql
-- Conectar a Cloud SQL
gcloud sql connect gmao-postgres --user=gmao-user --database=gmao --project=gmao-sistema-2025

-- Actualizar email del admin
UPDATE usuario 
SET email = 'admin@tuempresa.com' 
WHERE username = 'admin';
```

## ✅ Checklist de Configuración

- [ ] Habilitar verificación en dos pasos en Gmail
- [ ] Generar contraseña de aplicación de Gmail
- [ ] Actualizar `MAIL_USERNAME` en app.yaml
- [ ] Actualizar `MAIL_PASSWORD` en app.yaml
- [ ] Actualizar `ADMIN_EMAIL` en app.yaml
- [ ] Desplegar con `gcloud app deploy`
- [ ] Probar enviando una solicitud de prueba
- [ ] Verificar que lleguen ambos emails
- [ ] (Opcional) Actualizar email del usuario admin en la BD
