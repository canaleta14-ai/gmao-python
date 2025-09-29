# Migración a PostgreSQL para Producción

Esta guía explica cómo migrar la base de datos de SQLite (desarrollo) a PostgreSQL (producción).

## 📋 Prerrequisitos

1. **PostgreSQL instalado** en el servidor de producción
2. **Python dependencies** actualizadas
3. **Backup** de la base de datos SQLite actual

## 🚀 Pasos de Migración

### 1. Instalar PostgreSQL

#### En Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### En CentOS/RHEL:
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### En Windows:
- Descargar e instalar desde: https://www.postgresql.org/download/windows/
- O usar el instalador descargado anteriormente

### 2. Configurar PostgreSQL

```bash
# Crear usuario para la aplicación
sudo -u postgres createuser --interactive --pwprompt gmao_user

# Crear base de datos
sudo -u postgres createdb -O gmao_user gmao_db

# Configurar permisos (opcional)
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gmao_db TO gmao_user;"
```

### 3. Instalar Dependencias Python

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura:

```bash
cp .env.example .env
```

Edita `.env` con tus valores de PostgreSQL:

```bash
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gmao_db
DB_USER=gmao_user
DB_PASSWORD=tu_password_seguro
```

### 5. Ejecutar Migración

```bash
python migrate_to_postgres.py
```

Este script:
- ✅ Crea la base de datos PostgreSQL si no existe
- ✅ Migra todas las tablas y datos de SQLite a PostgreSQL
- ✅ Verifica la integridad de los datos

### 6. Verificar Migración

```bash
# Cambiar a PostgreSQL
export DB_TYPE=postgresql

# Probar la aplicación
python run.py
```

### 7. Configuración de Producción

#### Variables de entorno adicionales:
```bash
FLASK_ENV=production
SESSION_COOKIE_SECURE=True  # Importante para HTTPS
```

#### Configurar PostgreSQL para producción:
```bash
# Editar postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf

# Configuraciones recomendadas:
listen_addresses = '*'
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# Editar pg_hba.conf para conexiones remotas
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Agregar línea para conexiones locales:
host    gmao_db    gmao_user    127.0.0.1/32    md5
```

## 🔧 Solución de Problemas

### Error de conexión
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Verificar credenciales
psql -h localhost -U gmao_user -d gmao_db
```

### Error de permisos
```bash
# Otorgar permisos al usuario
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gmao_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gmao_user;"
```

### Rollback a SQLite
Si hay problemas, puedes volver a SQLite cambiando:
```bash
DB_TYPE=sqlite
```

## 📊 Diferencias SQLite vs PostgreSQL

| Característica | SQLite | PostgreSQL |
|---|---|---|
| Concurrencia | Limitada | Alta |
| Escalabilidad | Baja | Alta |
| Transacciones | ACID básico | ACID completo |
| Tipos de datos | Limitados | Completos |
| JSON | Básico | Avanzado |
| Índices | Básicos | Avanzados |
| Triggers | Limitados | Completos |

## 🔒 Seguridad en Producción

1. **Usar HTTPS** siempre
2. **Configurar firewall** para PostgreSQL
3. **Rotar passwords** regularmente
4. **Monitorear logs** de PostgreSQL
5. **Realizar backups** automáticos

## 📈 Rendimiento

PostgreSQL ofrece mejor rendimiento para:
- Aplicaciones con alta concurrencia
- Consultas complejas
- Grandes volúmenes de datos
- Operaciones de escritura intensivas

## 🆘 Soporte

Si encuentras problemas durante la migración:
1. Verifica los logs de la aplicación
2. Revisa los logs de PostgreSQL: `/var/log/postgresql/`
3. Asegúrate de que todas las dependencias estén instaladas
4. Verifica la configuración de red de PostgreSQL