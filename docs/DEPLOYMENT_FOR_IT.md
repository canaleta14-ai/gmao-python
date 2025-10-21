# Guía para el Departamento Informático — Despliegue y Migración GMAO

Este documento recoge todas las opciones, comandos y checks necesarios para desplegar la aplicación GMAO y migrar la base de datos desde el entorno de desarrollo a producción.

Contenido:

- Resumen ejecutivo
- Requisitos previos
- Opciones de despliegue (SSH/Git, RDP, red local)
- Transferencia de datos (SCP, SFTP, rsync, USB)
- Uso de scripts Python y Bash (export/import)
- Comandos detallados por escenario
- Seguridad y checklist
- Rollback y verificación post-importación
- Contactos y notas

---

## Resumen ejecutivo

El proceso se divide en tres fases principales:

1. Exportación de la base de datos desde el entorno de desarrollo (archivo comprimido + checksum).
2. Transferencia segura del archivo al servidor de producción.
3. Importación en el servidor de producción (backup automático + import + migraciones + reinicio).

Se recomiendan los scripts Python incluidos (`export_production_data.py` y `import_production_data.py`) por su compatibilidad multiplataforma y detección automática de PostgreSQL en Windows y Linux/Mac.

---

## Requisitos Previos (Servidor de Producción)

- Sistema operativo: Ubuntu 20.04+/CentOS 7+/Windows Server 2019+
- PostgreSQL 13+ (cliente `psql` y `pg_dump` disponibles)
- Git instalado (opcional si se usa `git clone` / `git pull` en servidor)
- Supervisor o systemd para gestionar el proceso Gunicorn/Flask (o equivalente)
- Nginx disponible como proxy inverso (opcional)
- Usuario con permisos sudo para tareas administrativas
- Firewall configurado para permitir solo los puertos necesarios (SSH, HTTP(S))

---

## Opciones de despliegue (detalladas)

### Opción A: Despliegue estándar (recomendado)

- Pasos:
  1. Desde el equipo de desarrollo: exportar DB (script Python).
  2. Transferir al servidor por SCP (VPN/SSH recomendado).
  3. Conectar al servidor por SSH.
  4. Actualizar repo (git pull) y ejecutar `import_production_data.py`.
- Ventajas: seguro, reproducible, auditable.
- Comandos clave:

```powershell
# En desarrollo (local)
python export_production_data.py
scp db_export\gmao_data_export_YYYYMMDD_HHMMSS.sql.gz usuario@servidor:/home/gmao/

# En servidor (SSH)
ssh usuario@servidor
cd /home/gmao/gmao-python/gmao-sistema
python import_production_data.py gmao_data_export_YYYYMMDD_HHMMSS.sql.gz
```

### Opción B: Despliegue con Git (código en servidor)

- Pasos:
  1. Push del código al repositorio central (GitHub/GitLab).
  2. En servidor: `git pull` para obtener cambios.
  3. Ejecutar scripts en servidor para migraciones y restart.
- Ventajas: control de versiones, fácil rollback.
- Comandos clave:

```bash
# En servidor
cd /home/gmao/gmao-python/gmao-sistema
git pull origin master
python export_production_data.py  # si exportas desde servidor
python import_production_data.py archivo.sql.gz
```

### Opción C: Acceso RDP / Desktop remoto (Windows Server)

- Pasos:
  1. Usar RDP o KVM para entrar en el servidor.
  2. Copiar archivos con SFTP o unidad compartida.
  3. Ejecutar `import_production_data.py` localmente en servidor.
- Recomendación: usar VPN para la conexión RDP y cuentas de servicio con permisos limitados.

### Opción D: Transferencia por red local o USB

- Útil en entornos con restricción de acceso remoto.
- Pasos:
  1. Copiar `db_export` a medio físico/compartido.
  2. Ejecutar import en servidor.
- Riesgos: menor trazabilidad y posible exposición física; eliminar archivos sensibles tras importación.

---

## Transferencia segura de archivos

- SCP (recomendado): `scp archivo usuario@servidor:/ruta/`
- SFTP: `sftp usuario@servidor` → `put archivo`
- rsync (para archivos grandes o reanudar): `rsync -avz --progress archivo usuario@servidor:/ruta/`
- Evitar FTP sin TLS.

---

## Scripts disponibles y uso

Rutas relativas en el repo:

- `export_production_data.py` (recomendado)
- `export_production_data.sh` (alternativa para Linux/Mac)
- `import_production_data.py` (recomendado)
- `import_production_data.sh` (alternativa para Linux/Mac)

### Export (local dev)

```powershell
python export_production_data.py
```

Salida: `db_export/gmao_data_export_YYYYMMDD_HHMMSS.sql.gz` + `.sha256` + `README.txt`

### Import (production server)

```bash
python import_production_data.py gmao_data_export_YYYYMMDD_HHMMSS.sql.gz
```

Proceso: verificación checksum → confirmación `SI CONFIRMO` → backup automático → import → migraciones → restart

---

## Comandos y scripts de ejemplo (copiar/pegar)

### Preparar servidor Ubuntu (resumen)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip postgresql postgresql-contrib nginx git supervisor build-essential libpq-dev
```

### Crear usuario y BD en PostgreSQL

```bash
sudo -u postgres psql -c "CREATE ROLE gmao_user LOGIN PASSWORD 'securepassword';"
sudo -u postgres psql -c "CREATE DATABASE gmao_db OWNER gmao_user;"
```

### Configuración Supervisor (ejemplo)

```
[program:gmao]
command=/home/gmao/gmao-python/gmao-sistema/start_gunicorn.sh
directory=/home/gmao/gmao-python/gmao-sistema
user=gmao
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/gmao/gmao-python/gmao-sistema/logs/gunicorn-access.log
stderr_logfile=/home/gmao/gmao-python/gmao-sistema/logs/gunicorn-error.log
```

---

## Seguridad: Checklist para el despliegue

- [ ] Acceso SSH por clave pública (evitar autenticación solo por contraseña)
- [ ] VPN activa para conexiones remotas cuando sea posible
- [ ] Firewall limitado a puertos necesarios (22, 80, 443)
- [ ] Usuarios y permisos mínimos en el servidor
- [ ] No subir `.env` con contraseñas al repositorio
- [ ] Verificación de checksums antes de importar
- [ ] Backup manual adicional antes de la importación (opcional pero recomendado)
- [ ] Mantener logs y backups por al menos 7 días
- [ ] Revisar y aplicar updates de seguridad del SO

---

## Rollback y recuperación

1. Detener la aplicación
2. Restaurar backup automático (archivo creado por `import_production_data.py`)
3. Reiniciar la aplicación

Comando ejemplo:

```bash
psql -U gmao_user -d gmao_db < /home/gmao/backups/pre_import_backup_YYYYMMDD_HHMMSS.sql
sudo supervisorctl restart gmao
```

---

## Verificación post-importación (pruebas mínimas)

- Comprobar que Gunicorn está corriendo y sin errores
- Ver logs: `tail -f logs/gunicorn-error.log` y `tail -f logs/gunicorn-access.log`
- Hacer pruebas de login, creación de inventario y búsqueda
- Ejecutar consultas básicas en base de datos (cuentas de tablas)

---

## Contactos y notas

- Repositorio: https://github.com/canaleta14-ai/gmao-python
- Documentación ampliada: `DEPLOYMENT.md` en la raíz del repo

---

> NOTA: Pide autorización del responsable de infra/IT antes de ejecutar cualquier importación en producción. Coordina la ventana de mantenimiento con usuarios afectados.
