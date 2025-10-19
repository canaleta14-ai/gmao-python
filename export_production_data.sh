#!/bin/bash

# Script para exportar datos de la base de datos local a producción
# Ejecutar en el entorno de DESARROLLO

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}📦 Exportando datos de base de datos para migración a producción...${NC}"

# Configuración
EXPORT_DIR="./db_export"
DATE=$(date +%Y%m%d_%H%M%S)
EXPORT_FILE="$EXPORT_DIR/gmao_data_export_$DATE.sql"

# Crear directorio de exportación
mkdir -p $EXPORT_DIR

# Detectar sistema operativo y configurar comando
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    echo -e "${YELLOW}🪟 Sistema Windows detectado${NC}"
    
    # Verificar si PostgreSQL está instalado
    if command -v pg_dump &> /dev/null; then
        PG_DUMP="pg_dump"
    elif [ -f "C:/Program Files/PostgreSQL/*/bin/pg_dump.exe" ]; then
        PG_DUMP="C:/Program Files/PostgreSQL/*/bin/pg_dump.exe"
    else
        echo -e "${RED}❌ Error: pg_dump no encontrado. Instalar PostgreSQL primero.${NC}"
        exit 1
    fi
else
    # Linux/Mac
    echo -e "${YELLOW}🐧 Sistema Unix detectado${NC}"
    PG_DUMP="pg_dump"
fi

# Leer credenciales del .env si existe
if [ -f ".env" ]; then
    echo -e "${YELLOW}📄 Leyendo credenciales de .env...${NC}"
    export $(grep -v '^#' .env | xargs)
    
    DB_NAME=${DB_NAME:-gmao_db}
    DB_USER=${DB_USER:-gmao_user}
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5432}
else
    echo -e "${YELLOW}⚠️ No se encontró .env, usando valores por defecto${NC}"
    DB_NAME="gmao_db"
    DB_USER="gmao_user"
    DB_HOST="localhost"
    DB_PORT="5432"
fi

echo ""
echo -e "${GREEN}🔍 Configuración de exportación:${NC}"
echo "  Base de datos: $DB_NAME"
echo "  Usuario: $DB_USER"
echo "  Host: $DB_HOST"
echo "  Puerto: $DB_PORT"
echo "  Archivo destino: $EXPORT_FILE"
echo ""

# Exportar base de datos completa
echo -e "${YELLOW}📤 Exportando base de datos completa...${NC}"

# Exportar con datos (estructura + datos)
$PG_DUMP -h $DB_HOST -p $DB_PORT -U $DB_USER \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    --verbose \
    $DB_NAME > "$EXPORT_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Base de datos exportada correctamente${NC}"
    
    # Comprimir archivo
    echo -e "${YELLOW}🗜️ Comprimiendo archivo...${NC}"
    gzip "$EXPORT_FILE"
    COMPRESSED_FILE="${EXPORT_FILE}.gz"
    
    # Información del archivo
    FILE_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    
    echo ""
    echo -e "${GREEN}✅ Exportación completada exitosamente!${NC}"
    echo -e "${GREEN}📁 Archivo: $COMPRESSED_FILE${NC}"
    echo -e "${GREEN}💾 Tamaño: $FILE_SIZE${NC}"
    echo ""
    echo -e "${YELLOW}📋 Próximos pasos:${NC}"
    echo "  1. Copiar el archivo al servidor de producción:"
    echo "     ${GREEN}scp $COMPRESSED_FILE usuario@servidor:/home/gmao/gmao-python/gmao-sistema/db_export/${NC}"
    echo ""
    echo "  2. En el servidor de producción, ejecutar:"
    echo "     ${GREEN}./import_production_data.sh $COMPRESSED_FILE${NC}"
    echo ""
    
    # Crear archivo de verificación con checksums
    echo -e "${YELLOW}🔐 Generando checksum para verificación...${NC}"
    if command -v sha256sum &> /dev/null; then
        sha256sum "$COMPRESSED_FILE" > "${COMPRESSED_FILE}.sha256"
        echo -e "${GREEN}✅ Checksum generado: ${COMPRESSED_FILE}.sha256${NC}"
    elif command -v shasum &> /dev/null; then
        shasum -a 256 "$COMPRESSED_FILE" > "${COMPRESSED_FILE}.sha256"
        echo -e "${GREEN}✅ Checksum generado: ${COMPRESSED_FILE}.sha256${NC}"
    fi
    
else
    echo -e "${RED}❌ Error al exportar la base de datos${NC}"
    echo -e "${RED}Verificar credenciales y conexión a PostgreSQL${NC}"
    exit 1
fi

# Crear README con instrucciones
cat > "$EXPORT_DIR/README.txt" << 'EOF'
INSTRUCCIONES PARA MIGRAR DATOS A PRODUCCIÓN
==============================================

1. PREPARACIÓN EN DESARROLLO:
   - Ya ejecutado: export_production_data.sh

2. TRANSFERIR ARCHIVOS AL SERVIDOR:
   
   En Windows (PowerShell):
   scp db_export/gmao_data_export_*.sql.gz usuario@servidor:/home/gmao/db_export/
   
   En Linux/Mac:
   scp db_export/gmao_data_export_*.sql.gz usuario@servidor:/home/gmao/db_export/

3. EN EL SERVIDOR DE PRODUCCIÓN:
   
   a) Conectarse al servidor:
      ssh usuario@servidor
   
   b) Ir al directorio de la aplicación:
      cd /home/gmao/gmao-python/gmao-sistema
   
   c) IMPORTANTE: Hacer backup de la BD actual:
      ./backup_gmao.sh
   
   d) Importar los nuevos datos:
      ./import_production_data.sh db_export/gmao_data_export_XXXXX.sql.gz
   
   e) Verificar que todo funciona:
      sudo supervisorctl restart gmao
      sudo supervisorctl status gmao

4. VERIFICACIÓN POST-MIGRACIÓN:
   - Acceder a la aplicación web
   - Verificar que los datos se muestran correctamente
   - Probar funcionalidades principales
   - Revisar logs: tail -f logs/gunicorn-error.log

5. EN CASO DE PROBLEMAS:
   - Restaurar desde el backup:
     gunzip backups/db_XXXXX.sql.gz
     psql -U gmao_user -d gmao_db < backups/db_XXXXX.sql

NOTAS IMPORTANTES:
- Siempre hacer backup antes de importar
- Verificar el checksum del archivo transferido
- La importación sobrescribirá TODOS los datos existentes
- Tiempo estimado de importación: 5-15 minutos (depende del tamaño)

EOF

echo -e "${GREEN}📄 README creado en: $EXPORT_DIR/README.txt${NC}"
echo ""
echo -e "${YELLOW}⚠️ RECORDATORIO IMPORTANTE:${NC}"
echo -e "${RED}   - Hacer BACKUP de producción antes de importar${NC}"
echo -e "${RED}   - Verificar el checksum del archivo después de transferirlo${NC}"
echo -e "${RED}   - Planificar la migración en horario de bajo tráfico${NC}"
