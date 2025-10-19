#!/bin/bash

# Script para importar datos en el servidor de PRODUCCIÓN
# ADVERTENCIA: Este script sobrescribirá TODOS los datos existentes

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}⚠️  IMPORTACIÓN DE DATOS A PRODUCCIÓN ⚠️${NC}"
echo -e "${YELLOW}Este script sobrescribirá TODOS los datos actuales${NC}"
echo ""

# Verificar que se proporcionó un archivo
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Debe proporcionar el archivo SQL a importar${NC}"
    echo ""
    echo "Uso: $0 archivo.sql.gz"
    echo "Ejemplo: $0 db_export/gmao_data_export_20250119_150000.sql.gz"
    exit 1
fi

IMPORT_FILE="$1"

# Verificar que el archivo existe
if [ ! -f "$IMPORT_FILE" ]; then
    echo -e "${RED}❌ Error: Archivo no encontrado: $IMPORT_FILE${NC}"
    exit 1
fi

# Leer credenciales del .env
if [ -f ".env" ]; then
    echo -e "${YELLOW}📄 Leyendo credenciales de .env...${NC}"
    export $(grep -v '^#' .env | xargs)
    
    DB_NAME=${DB_NAME:-gmao_db}
    DB_USER=${DB_USER:-gmao_user}
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5432}
else
    echo -e "${RED}❌ Error: No se encontró archivo .env${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}🔍 Configuración de importación:${NC}"
echo "  Base de datos: $DB_NAME"
echo "  Usuario: $DB_USER"
echo "  Host: $DB_HOST"
echo "  Puerto: $DB_PORT"
echo "  Archivo origen: $IMPORT_FILE"
echo ""

# Verificar checksum si existe
CHECKSUM_FILE="${IMPORT_FILE}.sha256"
if [ -f "$CHECKSUM_FILE" ]; then
    echo -e "${YELLOW}🔐 Verificando integridad del archivo...${NC}"
    if command -v sha256sum &> /dev/null; then
        sha256sum -c "$CHECKSUM_FILE"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Checksum verificado correctamente${NC}"
        else
            echo -e "${RED}❌ Error: Checksum no coincide. El archivo puede estar corrupto.${NC}"
            read -p "¿Continuar de todos modos? (yes/NO): " confirm
            if [ "$confirm" != "yes" ]; then
                echo "Importación cancelada"
                exit 1
            fi
        fi
    fi
fi

# Confirmación final
echo ""
echo -e "${RED}⚠️  ÚLTIMA ADVERTENCIA ⚠️${NC}"
echo -e "${YELLOW}Esta acción:${NC}"
echo "  1. Detendrá la aplicación"
echo "  2. Hará un backup automático de la BD actual"
echo "  3. ELIMINARÁ todos los datos existentes"
echo "  4. Importará los nuevos datos"
echo "  5. Reiniciará la aplicación"
echo ""
read -p "¿Está COMPLETAMENTE seguro de continuar? (escriba 'SI CONFIRMO' para proceder): " confirmation

if [ "$confirmation" != "SI CONFIRMO" ]; then
    echo -e "${YELLOW}Importación cancelada${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Iniciando proceso de importación...${NC}"

# Paso 1: Detener la aplicación
echo -e "${YELLOW}1️⃣ Deteniendo aplicación...${NC}"
sudo supervisorctl stop gmao
sleep 2

# Paso 2: Hacer backup automático
echo -e "${YELLOW}2️⃣ Creando backup de seguridad...${NC}"
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR
BACKUP_FILE="$BACKUP_DIR/pre_import_backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    gzip "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backup creado: ${BACKUP_FILE}.gz${NC}"
else
    echo -e "${RED}❌ Error al crear backup. Abortando importación.${NC}"
    sudo supervisorctl start gmao
    exit 1
fi

# Paso 3: Descomprimir archivo si es necesario
TEMP_SQL_FILE=""
if [[ "$IMPORT_FILE" == *.gz ]]; then
    echo -e "${YELLOW}3️⃣ Descomprimiendo archivo...${NC}"
    TEMP_SQL_FILE="${IMPORT_FILE%.gz}"
    gunzip -c "$IMPORT_FILE" > "$TEMP_SQL_FILE"
    SQL_FILE="$TEMP_SQL_FILE"
else
    SQL_FILE="$IMPORT_FILE"
fi

# Paso 4: Importar datos
echo -e "${YELLOW}4️⃣ Importando datos en la base de datos...${NC}"
echo -e "${YELLOW}   (Esto puede tomar varios minutos)${NC}"

# Importar usando psql
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < "$SQL_FILE" 2>&1 | tee import.log

IMPORT_RESULT=${PIPESTATUS[0]}

# Limpiar archivo temporal
if [ ! -z "$TEMP_SQL_FILE" ] && [ -f "$TEMP_SQL_FILE" ]; then
    rm "$TEMP_SQL_FILE"
fi

if [ $IMPORT_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Datos importados correctamente${NC}"
else
    echo -e "${RED}❌ Error durante la importación${NC}"
    echo -e "${YELLOW}📋 Ver detalles en: import.log${NC}"
    echo ""
    echo -e "${RED}⚠️  Recomendación: Restaurar desde el backup${NC}"
    echo "Comando: gunzip ${BACKUP_FILE}.gz && psql -U $DB_USER -d $DB_NAME < ${BACKUP_FILE}"
    
    sudo supervisorctl start gmao
    exit 1
fi

# Paso 5: Ejecutar migraciones por si acaso
echo -e "${YELLOW}5️⃣ Verificando esquema de base de datos...${NC}"
source .venv/bin/activate
export FLASK_APP=run.py
flask db upgrade

# Paso 6: Reiniciar aplicación
echo -e "${YELLOW}6️⃣ Reiniciando aplicación...${NC}"
sudo supervisorctl start gmao
sleep 3

# Verificar estado
sudo supervisorctl status gmao

echo ""
echo -e "${GREEN}✅ ¡Importación completada exitosamente!${NC}"
echo ""
echo -e "${YELLOW}📋 Próximos pasos de verificación:${NC}"
echo "  1. Acceder a la aplicación web"
echo "  2. Verificar que los datos se muestran correctamente"
echo "  3. Probar funcionalidades principales"
echo "  4. Revisar logs:"
echo "     ${GREEN}tail -f logs/gunicorn-error.log${NC}"
echo ""
echo -e "${YELLOW}📦 Backup de seguridad guardado en:${NC}"
echo "     ${GREEN}${BACKUP_FILE}.gz${NC}"
echo ""
echo -e "${YELLOW}📋 Log de importación:${NC}"
echo "     ${GREEN}import.log${NC}"
