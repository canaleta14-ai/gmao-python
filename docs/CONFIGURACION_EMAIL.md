# 📧 Configuración de Envío de Correos Electrónicos

## ❌ Estado Actual

**El envío de correos NO está funcionando** porque faltan las credenciales SMTP en el archivo `.env`.

### Error en los logs:

```
Error enviando email: Configuración de email incompleta.
MAIL_USERNAME: MISSING, MAIL_PASSWORD: MISSING
```

---

## ✅ Solución: Configurar Credenciales SMTP

### Paso 1: Editar el archivo `.env`

Abre el archivo `.env` en la raíz del proyecto y añade/actualiza estas variables:

```env
# Configuración de Email SMTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
ADMIN_EMAILS=admin@tuempresa.com,gerente@tuempresa.com
```

---

## 🔐 Cómo Obtener Credenciales para Gmail

### Opción 1: Contraseña de Aplicación (Recomendado)

Si usas Gmail, **debes** crear una contraseña de aplicación:

#### Pasos:

1. Ve a tu [Cuenta de Google](https://myaccount.google.com/)
2. Seguridad → **Verificación en 2 pasos** (actívala si no está activa)
3. Busca **Contraseñas de aplicaciones**
4. Selecciona:
   - App: **Correo**
   - Dispositivo: **Otro (Nombre personalizado)**
   - Nombre: `GMAO Sistema`
5. Google generará una contraseña de 16 caracteres
6. **Copia esta contraseña** (sin espacios)
7. Úsala en `MAIL_PASSWORD`

#### Ejemplo:

```env
MAIL_USERNAME=empresa@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop  # Sin espacios: abcdefghijklmnop
```

### Opción 2: Otros Proveedores SMTP

#### **Outlook/Hotmail**

```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@outlook.com
MAIL_PASSWORD=tu_contraseña
```

#### **Office 365**

```env
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@tuempresa.com
MAIL_PASSWORD=tu_contraseña
```

#### **Yahoo Mail**

```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@yahoo.com
MAIL_PASSWORD=contraseña_de_aplicacion_yahoo
```

#### **SendGrid (Profesional)**

```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=tu_api_key_de_sendgrid
```

---

## 🔧 Verificar Configuración

### Método 1: Script de Prueba

Crea un archivo `test_email.py`:

```python
from app import create_app
from app.utils.email_utils import enviar_email

app = create_app()

with app.app_context():
    try:
        enviar_email(
            destinatario="tu_email@gmail.com",
            asunto="Prueba de configuración SMTP",
            contenido_html="""
                <h2>✅ Configuración correcta</h2>
                <p>Si recibes este correo, el sistema está funcionando.</p>
            """
        )
        print("✅ Email enviado correctamente")
    except Exception as e:
        print(f"❌ Error: {e}")
```

Ejecutar:

```bash
python test_email.py
```

### Método 2: Verificar en Solicitudes

1. Accede a `/solicitudes/`
2. Crea una nueva solicitud de trabajo
3. Verifica los logs del servidor
4. El administrador debería recibir un correo

---

## 📝 Configuración de Administradores

La variable `ADMIN_EMAILS` define quiénes reciben notificaciones:

```env
# Un solo administrador
ADMIN_EMAILS=admin@tuempresa.com

# Múltiples administradores (separados por coma)
ADMIN_EMAILS=admin@empresa.com,gerente@empresa.com,supervisor@empresa.com
```

---

## 🚨 Solución de Problemas

### Error: "Authentication failed"

**Causa**: Credenciales incorrectas

**Solución**:

- Gmail: Verifica que uses **contraseña de aplicación** (no tu contraseña normal)
- Otros: Verifica usuario y contraseña
- Intenta iniciar sesión manualmente en el webmail

---

### Error: "Connection refused" o timeout

**Causa**: Puerto bloqueado o firewall

**Solución**:

- Verifica que el puerto 587 esté abierto
- Prueba con puerto 465 (SSL):
  ```env
  MAIL_PORT=465
  MAIL_USE_TLS=False
  MAIL_USE_SSL=True
  ```
- Desactiva temporalmente firewall/antivirus para probar

---

### Error: "Less secure apps"

**Causa**: Gmail requiere verificación en 2 pasos

**Solución**:

1. Activa verificación en 2 pasos en Google
2. Genera contraseña de aplicación
3. **NO uses** "Permitir aplicaciones menos seguras" (obsoleto desde 2022)

---

### Gmail bloquea el acceso

**Posibles causas**:

1. No usas contraseña de aplicación
2. Verificación en 2 pasos no activada
3. IP bloqueada por intentos fallidos

**Solución**:

1. Ve a https://accounts.google.com/DisplayUnlockCaptcha
2. Haz clic en "Continuar"
3. Intenta enviar email nuevamente en 5 minutos

---

## 📄 Plantillas de Email

El sistema usa estas plantillas:

### 1. Confirmación de Solicitud (al creador)

```
Asunto: Confirmación: Solicitud #{id} creada
Contenido: Detalles de la solicitud creada
```

### 2. Notificación a Administradores

```
Asunto: Nueva Solicitud de Trabajo #{id}
Contenido: Detalles + Link para gestionar
```

---

## 🔒 Seguridad

### ⚠️ IMPORTANTE:

1. **NUNCA** subas el archivo `.env` a GitHub
2. Ya está en `.gitignore` por defecto
3. La contraseña se maneja de forma segura en memoria
4. No se registra en logs

### Verificar que .env está ignorado:

```bash
git status
# .env NO debe aparecer en "Changes to be committed"
```

---

## 📊 Logs de Email

Los eventos de email se registran en:

- `logs/app.log` - Logs generales
- Consola del servidor (modo desarrollo)

### Mensajes típicos:

```
✅ Éxito:
INFO - Email enviado exitosamente a usuario@email.com

❌ Error de configuración:
ERROR - Error enviando email: Configuración de email incompleta

❌ Error de autenticación:
ERROR - Error enviando email: Authentication failed

❌ Error de conexión:
ERROR - Error enviando email: Connection refused
```

---

## 🧪 Modo Desarrollo Sin Email

Si no quieres configurar email en desarrollo local:

### Opción 1: Dejar vacío (comportamiento actual)

```env
MAIL_USERNAME=
MAIL_PASSWORD=
```

**Resultado**: Los errores se registran en logs pero la app sigue funcionando

### Opción 2: Usar MailHog (servidor SMTP de prueba)

1. Instalar MailHog:

   ```bash
   # Windows (con Chocolatey)
   choco install mailhog

   # O descargar de: https://github.com/mailhog/MailHog/releases
   ```

2. Ejecutar MailHog:

   ```bash
   mailhog
   ```

3. Configurar:

   ```env
   MAIL_SERVER=localhost
   MAIL_PORT=1025
   MAIL_USE_TLS=False
   MAIL_USERNAME=
   MAIL_PASSWORD=
   ```

4. Ver emails en: http://localhost:8025

---

## ✅ Checklist de Configuración

- [ ] Archivo `.env` existe
- [ ] `MAIL_USERNAME` configurado
- [ ] `MAIL_PASSWORD` configurado (contraseña de aplicación si es Gmail)
- [ ] `MAIL_SERVER` configurado
- [ ] `MAIL_PORT` configurado
- [ ] `ADMIN_EMAILS` configurado
- [ ] Verificación en 2 pasos activa (Gmail)
- [ ] Contraseña de aplicación generada (Gmail)
- [ ] Email de prueba enviado exitosamente
- [ ] `.env` NO está en git

---

## 📞 Soporte

Si sigues teniendo problemas:

1. Verifica los logs: `logs/app.log`
2. Prueba con otro proveedor SMTP
3. Usa MailHog para desarrollo local
4. Revisa la configuración del firewall

---

## 🎯 Resumen Rápido

Para Gmail:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Contraseña de aplicación
ADMIN_EMAILS=admin@empresa.com
```

**Recuerda**:

1. Activa verificación en 2 pasos en Google
2. Genera contraseña de aplicación
3. Reinicia el servidor después de cambiar `.env`

---

✨ **¡Con esto el envío de correos funcionará correctamente!** ✨
