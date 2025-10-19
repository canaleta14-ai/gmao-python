#!/bin/bash

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="/home/gmao/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo -e "${YELLOW}📦 Iniciando backup del sistema GMAO...${NC}"

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# Backup de la base de datos
echo -e "${YELLOW}💾 Haciendo backup de PostgreSQL...${NC}"
pg_dump -U gmao_user gmao_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup de BD creado: db_$DATE.sql.gz${NC}"
else
    echo "❌ Error al crear backup de la base de datos"
    exit 1
fi

# Backup de archivos subidos
echo -e "${YELLOW}📁 Haciendo backup de archivos subidos...${NC}"
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" /home/gmao/gmao-python/gmao-sistema/uploads/ 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup de uploads creado: uploads_$DATE.tar.gz${NC}"
else
    echo "❌ Error al crear backup de uploads"
fi

# Backup de configuración
echo -e "${YELLOW}⚙️ Haciendo backup de configuración...${NC}"
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /home/gmao/gmao-python/gmao-sistema/.env \
    /etc/nginx/sites-available/gmao \
    /etc/supervisor/conf.d/gmao.conf 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup de configuración creado: config_$DATE.tar.gz${NC}"
fi

# Eliminar backups antiguos
echo -e "${YELLOW}🗑️ Eliminando backups antiguos (más de $RETENTION_DAYS días)...${NC}"
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
DELETED=$(find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS | wc -l)
echo -e "${GREEN}✅ $DELETED archivos antiguos eliminados${NC}"

# Mostrar resumen
echo ""
echo -e "${GREEN}📊 Resumen de Backups:${NC}"
echo "-----------------------------------"
ls -lh $BACKUP_DIR/*$DATE* 2>/dev/null

# Tamaño total de backups
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
BACKUP_COUNT=$(ls -1 $BACKUP_DIR/*.gz 2>/dev/null | wc -l)

echo ""
echo -e "${GREEN}✅ Backup completado exitosamente!${NC}"
echo -e "📦 Total de backups: $BACKUP_COUNT"
echo -e "💾 Espacio usado: $TOTAL_SIZE"
echo -e "📅 Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
