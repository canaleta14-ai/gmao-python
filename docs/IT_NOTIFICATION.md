# Notificación para Departamento Informático — Sistema GMAO

---

**Para:** Departamento Informático / Sistemas  
**De:** Equipo de Desarrollo GMAO  
**Asunto:** Despliegue Sistema GMAO en Producción - Documentación y Scripts Listos  
**Fecha:** 21 de octubre de 2025  
**Prioridad:** Alta

---

## Resumen

El sistema GMAO (Gestión de Mantenimiento Asistido por Ordenador) está listo para desplegarse en el entorno de producción. Hemos preparado toda la documentación, scripts automatizados y procedimientos de seguridad necesarios.

**Estado actual:**

- ✅ Código fuente completado y testeado
- ✅ Base de datos exportada y verificada (78 KB comprimidos)
- ✅ Scripts de migración automáticos (Python + Bash)
- ✅ Documentación técnica completa
- ✅ Checklist de seguridad incluido

---

## Documentos disponibles

### 📘 Guía completa para IT

**Archivo:** `docs/DEPLOYMENT_FOR_IT.md`  
**Contenido:**

- Requisitos del servidor (hardware, software, permisos)
- Opciones de despliegue (SSH/Git, RDP, red local)
- Comandos listos para copiar/pegar
- Checklist de seguridad pre-despliegue
- Procedimientos de rollback y recuperación
- Verificación post-importación

**Link directo:** https://github.com/canaleta14-ai/gmao-python/blob/master/docs/DEPLOYMENT_FOR_IT.md

### 📗 Guía técnica detallada

**Archivo:** `DEPLOYMENT.md` (raíz del proyecto)  
**Contenido:**

- Paso a paso completo (11 pasos principales)
- Configuración PostgreSQL, Nginx, Supervisor
- SSL/HTTPS con Let's Encrypt
- Backups automáticos y monitoreo
- Troubleshooting y logs

**Link directo:** https://github.com/canaleta14-ai/gmao-python/blob/master/DEPLOYMENT.md

---

## Scripts automatizados incluidos

### 🔧 Exportación de base de datos

**Archivo:** `export_production_data.py`  
**Funcionalidad:**

- Detecta automáticamente PostgreSQL (Windows/Linux/Mac)
- Genera archivo comprimido `.sql.gz`
- Crea checksum SHA256 para verificación
- Genera README con instrucciones

**Uso:**

```bash
python export_production_data.py
```

### 🔧 Importación en producción

**Archivo:** `import_production_data.py`  
**Funcionalidad:**

- Verificación de integridad (checksum)
- Backup automático pre-importación
- Confirmación explícita requerida ("SI CONFIRMO")
- Detiene/reinicia aplicación automáticamente
- Incluye instrucciones de rollback

**Uso:**

```bash
python import_production_data.py archivo_exportado.sql.gz
```

---

## Requisitos del servidor de producción

### Hardware mínimo

- CPU: 2 cores
- RAM: 4 GB
- Disco: 20 GB SSD
- Red: Conexión estable

### Software requerido

- Ubuntu 20.04+ / CentOS 7+ / Windows Server 2019+
- PostgreSQL 13+ (con `psql` y `pg_dump`)
- Python 3.10+
- Git (para actualizaciones)
- Nginx (proxy inverso)
- Supervisor o systemd (gestión de procesos)

### Accesos necesarios

- SSH con autenticación por clave (recomendado)
- Permisos sudo para instalación de paquetes
- Firewall: puertos 22 (SSH), 80 (HTTP), 443 (HTTPS)
- VPN activa para conexiones remotas (si aplica)

---

## Repositorio y acceso

**Repositorio GitHub:** https://github.com/canaleta14-ai/gmao-python

**Branch principal:** `master`

**Estructura del proyecto:**

```
gmao-sistema/
├── app/                          # Aplicación Flask
├── docs/                         # Documentación
│   ├── DEPLOYMENT_FOR_IT.md     # Guía para IT ⭐
│   └── ...
├── DEPLOYMENT.md                 # Guía técnica completa ⭐
├── export_production_data.py     # Script exportación ⭐
├── import_production_data.py     # Script importación ⭐
├── requirements.txt              # Dependencias Python
├── gunicorn_config.py            # Config servidor WSGI
├── nginx.conf.example            # Config Nginx
└── supervisor.conf.example       # Config Supervisor
```

---

## Checklist de seguridad (pre-despliegue)

Por favor, verificar antes de proceder:

- [ ] Acceso SSH configurado con clave pública (no solo contraseña)
- [ ] VPN empresarial activa para conexiones remotas
- [ ] Firewall limitado a puertos necesarios (22, 80, 443)
- [ ] Usuario con permisos mínimos para la aplicación
- [ ] PostgreSQL instalado y configurado
- [ ] No subir archivos `.env` con contraseñas al repositorio
- [ ] Backup manual del servidor antes de la importación
- [ ] Ventana de mantenimiento coordinada con usuarios
- [ ] Logs y backups configurados con retención de 7+ días

---

## Proceso de despliegue (resumen)

### Fase 1: Preparación (1-2 horas)

1. Preparar servidor con requisitos (OS actualizado, paquetes instalados)
2. Crear usuario PostgreSQL y base de datos
3. Clonar repositorio desde GitHub
4. Configurar entorno virtual Python e instalar dependencias

### Fase 2: Transferencia de datos (15-30 minutos)

1. Ejecutar `export_production_data.py` en desarrollo
2. Transferir archivos al servidor vía SCP/SFTP
3. Verificar checksum en servidor

### Fase 3: Importación y despliegue (30-45 minutos)

1. Ejecutar `import_production_data.py` en servidor
2. Confirmar importación (escribe "SI CONFIRMO")
3. Verificar aplicación y logs
4. Configurar Nginx, Supervisor y SSL

**Tiempo total estimado: 2-4 horas** (incluye pruebas y verificación)

---

## Ventana de mantenimiento sugerida

**Downtime estimado:** 5-15 minutos (solo durante importación de BD)

**Mejor momento:**

- Fuera de horario laboral (tarde/noche/fin de semana)
- Avisar usuarios con 48h de antelación
- Tener plan de rollback listo

---

## Contacto y soporte

**Desarrollador:** [Tu nombre/contacto]  
**Email:** [Tu email]  
**Disponibilidad:** [Horarios disponibles para soporte]

**Repositorio issues:** https://github.com/canaleta14-ai/gmao-python/issues

---

## Próximos pasos recomendados

1. **Revisar** `docs/DEPLOYMENT_FOR_IT.md` completo
2. **Validar** que el servidor cumple requisitos mínimos
3. **Coordinar** fecha/hora de despliegue
4. **Preparar** accesos SSH y credenciales PostgreSQL
5. **Ejecutar** despliegue siguiendo la guía paso a paso
6. **Verificar** aplicación funcional post-importación

---

## Notas importantes

- Los scripts Python son **multiplataforma** y no requieren Git Bash en Windows
- Existe backup automático pre-importación, pero se recomienda uno manual adicional
- El proceso es **reversible** (rollback incluido en documentación)
- Todos los comandos están listos para copiar/pegar desde la documentación
- Se mantiene compatibilidad con scripts Bash (`.sh`) para usuarios Linux/Mac

---

**¿Dudas o necesitas aclaraciones?** Responde a este mensaje o abre un issue en el repositorio.

**¡Gracias por tu colaboración en el despliegue del sistema GMAO!** 🚀
