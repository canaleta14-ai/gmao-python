#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

echo -e "${GREEN}🔄 Actualizando aplicación GMAO...${NC}"

# Ir al directorio de la aplicación
APP_DIR="/home/gmao/gmao-python/gmao-sistema"
cd $APP_DIR || exit 1

# Verificar que estamos en el directorio correcto
if [ ! -f "run.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra run.py. ¿Estás en el directorio correcto?${NC}"
    exit 1
fi

# Hacer backup de la base de datos
echo -e "${YELLOW}📦 Haciendo backup de la base de datos...${NC}"
mkdir -p backups
BACKUP_FILE="backups/gmao_db_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -U gmao_user gmao_db > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup creado: $BACKUP_FILE${NC}"
    gzip "$BACKUP_FILE"
else
    echo -e "${RED}❌ Error al crear backup${NC}"
    exit 1
fi

# Obtener últimos cambios
echo -e "${YELLOW}📥 Obteniendo últimos cambios desde GitHub...${NC}"
git fetch origin
git pull origin master

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al obtener cambios de Git${NC}"
    exit 1
fi

# Activar entorno virtual
echo -e "${YELLOW}🔧 Activando entorno virtual...${NC}"
source .venv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al activar entorno virtual${NC}"
    exit 1
fi

# Actualizar dependencias
echo -e "${YELLOW}📦 Actualizando dependencias...${NC}"
pip install -r requirements.txt --upgrade

# Ejecutar migraciones
echo -e "${YELLOW}🗄️ Ejecutando migraciones de base de datos...${NC}"
export FLASK_APP=run.py
flask db upgrade

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al ejecutar migraciones${NC}"
    exit 1
fi

# Reiniciar aplicación con Supervisor
echo -e "${YELLOW}🔄 Reiniciando aplicación...${NC}"
sudo supervisorctl restart gmao

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Aplicación reiniciada correctamente${NC}"
else
    echo -e "${RED}❌ Error al reiniciar aplicación${NC}"
    exit 1
fi

# Esperar un momento y verificar estado
sleep 3

echo -e "${YELLOW}🔍 Verificando estado de la aplicación...${NC}"
sudo supervisorctl status gmao

# Verificar logs por si hay errores
echo -e "${YELLOW}📋 Últimas líneas del log de errores:${NC}"
tail -n 20 logs/gunicorn-error.log

echo ""
echo -e "${GREEN}✅ ¡Actualización completada exitosamente!${NC}"
echo -e "${GREEN}🌐 La aplicación está corriendo en: https://tu-dominio.empresa.com${NC}"
