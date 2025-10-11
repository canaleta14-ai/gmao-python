# Configuración GDPR para GMAO - España

## Cumplimiento GDPR para empresa española

### 1. Residencia de datos

- **Región**: `europe-west1` (Bélgica) - dentro de la UE
- **Bucket Storage**: `disfood-gmao-uploads-eu` - región europea
- **Base de datos**: Cloud SQL en `europe-west1`

### 2. Retención de datos

- **Documentos de mantenimiento**: 7 años (según normativa española)
- **Logs de acceso**: 1 año
- **Datos personales**: Según política de privacidad
- **Variable configurada**: `DATA_RETENTION_DAYS=2555` (7 años)

### 3. Derechos GDPR implementados

- **Derecho de acceso**: Los usuarios pueden ver sus datos
- **Derecho de rectificación**: Los usuarios pueden modificar sus datos
- **Derecho de supresión**: Administradores pueden eliminar usuarios
- **Derecho de portabilidad**: Exportación de datos disponible

### 4. Medidas de seguridad

- **Cifrado en tránsito**: HTTPS obligatorio
- **Cifrado en reposo**: Cloud SQL y Storage cifrados
- **Autenticación**: Sistema de usuarios con roles
- **Auditoría**: Logs de todas las acciones

### 5. Configuración de cookies

```yaml
SESSION_COOKIE_SECURE: "true"
REMEMBER_COOKIE_SECURE: "true"
SESSION_COOKIE_SAMESITE: "Lax"
```

### 6. Política de privacidad

- Debe incluirse en la aplicación
- Informar sobre uso de cookies
- Explicar retención de datos
- Contacto del DPO (Delegado de Protección de Datos)

### 7. Consentimiento

- Banner de cookies implementado
- Consentimiento para procesamiento de datos
- Opción de retirar consentimiento

### 8. Transferencias internacionales

- **No aplicable**: Todos los datos permanecen en la UE
- Proveedores: Google Cloud (certificado GDPR)

### 9. Notificación de brechas

- **Plazo**: 72 horas a la AEPD
- **Logs**: Monitoreados en Google Cloud Logging
- **Alertas**: Configuradas para incidentes de seguridad

### 10. Evaluación de impacto (DPIA)

- Realizada para el sistema GMAO
- Riesgos identificados y mitigados
- Documentación disponible para auditores

## Variables de entorno GDPR

```bash
GDPR_COMPLIANCE=true
DATA_RETENTION_DAYS=2555
GCLOUD_REGION=europe-west1
TIMEZONE=Europe/Madrid
LANGUAGE=es
LOCALE=es_ES.UTF-8
```

## Contacto DPO

- **Email**: dpo@disfood.es
- **Teléfono**: +34 XXX XXX XXX
- **Dirección**: [Dirección de la empresa]

## Auditorías

- **Frecuencia**: Anual
- **Última auditoría**: [Fecha]
- **Próxima auditoría**: [Fecha]
- **Certificaciones**: ISO 27001, SOC 2 (Google Cloud)
