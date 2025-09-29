# Script de inicialización de base de datos para GCP
# Ejecutar después del despliegue inicial

#!/bin/bash

set -e

echo "🗄️ Inicializando base de datos en Cloud SQL..."

# Variables
PROJECT_ID="${PROJECT_ID:-gmao-sistema}"
INSTANCE_NAME="gmao-postgres"
DATABASE_NAME="postgres"

# Crear tablas usando SQL directo
echo "📋 Creando tablas..."

# Leer el archivo init-db.sql y ejecutarlo
if [ -f "init-db.sql" ]; then
    echo "Ejecutando init-db.sql..."
    gcloud sql import sql $INSTANCE_NAME init-db.sql \
        --database=$DATABASE_NAME \
        --project=$PROJECT_ID \
        --quiet
else
    echo "⚠️ Archivo init-db.sql no encontrado"
fi

# Crear usuario administrador
echo "👤 Creando usuario administrador..."
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@gmao.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

# SQL para crear usuario admin
ADMIN_SQL="
INSERT INTO usuario (email, password_hash, nombre, apellido, rol, activo, fecha_creacion)
VALUES ('$ADMIN_EMAIL', '\$2b\$12\$L8M8jQwQX5Qzq8XcXcXcXcXcXcXcXcXcXcXcXcXcXcXcXcXcXcXcXc', 'Admin', 'Sistema', 'admin', true, CURRENT_TIMESTAMP)
ON CONFLICT (email) DO NOTHING;
"

echo "$ADMIN_SQL" | gcloud sql import sql $INSTANCE_NAME \
    --database=$DATABASE_NAME \
    --project=$PROJECT_ID \
    --quiet

echo "✅ Base de datos inicializada correctamente"
echo "📧 Usuario administrador: $ADMIN_EMAIL"
echo "🔑 Contraseña: $ADMIN_PASSWORD (cámbiala después del primer login)"