# Configuración de Email con Gmail

## Requisitos para Gmail

Para usar Gmail como servidor de email, necesitas:

### 1. Configuración Básica

```properties
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_cuenta@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicación
```

### 2. Contraseña de Aplicación (Obligatorio si tienes 2FA)

Si tienes **verificación en 2 pasos** habilitada en tu cuenta de Gmail, NO puedes usar tu contraseña normal. Necesitas crear una **contraseña de aplicación**:

#### Pasos para crear contraseña de aplicación:

1. Ve a tu cuenta de Gmail
2. Ve a **Configuración** → **Ver todas las configuraciones**
3. Pestaña **Cuentas e Importación** → **Otras configuraciones de Gmail**
4. **Contraseñas de aplicación**
5. Selecciona **Aplicación**: "Correo"
6. Selecciona **Dispositivo**: "Otro (nombre personalizado)"
7. Ingresa un nombre como "GMAO System"
8. Copia la contraseña de 16 caracteres generada
9. Úsala como `MAIL_PASSWORD` en el archivo `.env`

### 3. Para Google Workspace (Gmail Empresarial)

Si usas Google Workspace (dominio personalizado como @empresa.com):

- El `MAIL_USERNAME` debe ser tu dirección completa: `usuario@empresa.com`
- El `MAIL_PASSWORD` debe ser tu contraseña normal O una contraseña de aplicación
- Asegúrate de que tu administrador haya habilitado el acceso SMTP

### 4. Solución de Problemas

#### Error: "Aplicación menos segura"

- Gmail puede bloquear aplicaciones que considera "menos seguras"
- Si ves este error, habilita el acceso para aplicaciones menos seguras:
  - Ve a: https://myaccount.google.com/lesssecureapps
  - Activa "Permitir aplicaciones menos seguras"

#### Error de Autenticación

- Verifica que la contraseña de aplicación sea correcta
- Asegúrate de que no tenga espacios
- Si usas Google Workspace, verifica con tu administrador

#### Error de Conexión

- Verifica tu conexión a internet
- Algunos firewalls/antivirus bloquean conexiones SMTP
- Prueba con un puerto diferente: 465 (SSL) en lugar de 587 (TLS)

### 5. Configuración Recomendada

Para máxima compatibilidad, usa:

```properties
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=contraseña_de_aplicación_16_caracteres
```

### 6. Prueba de Configuración

Ejecuta el script de prueba:

```bash
python test_gmail_config.py
```

Si la prueba falla, revisa los puntos anteriores y asegúrate de que:

- La dirección de email sea correcta
- La contraseña de aplicación sea válida
- No haya restricciones de seguridad en tu cuenta de Gmail</content>
  <parameter name="filePath">c:\gmao - copia\CONFIGURACION_GMAIL.md
