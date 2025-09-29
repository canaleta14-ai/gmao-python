#!/bin/bash
# Script para configurar PostgreSQL automáticamente

set -e

echo "🔧 Configurando PostgreSQL para GMAO..."

# Variables (cambiar según necesidad)
DB_NAME="gmao_db"
DB_USER="gmao_user"
DB_PASSWORD="gmao_password"

# Función para ejecutar comandos como postgres
run_as_postgres() {
    sudo -u postgres psql -c "$1"
}

echo "📦 Creando usuario de base de datos..."
run_as_postgres "CREATE USER IF NOT EXISTS $DB_USER WITH PASSWORD '$DB_PASSWORD';"

echo "🗄️  Creando base de datos..."
run_as_postgres "CREATE DATABASE IF NOT EXISTS $DB_NAME OWNER $DB_USER;"

echo "🔑 Otorgando permisos..."
run_as_postgres "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "✅ Configuración completada!"
echo ""
echo "📝 Variables de entorno para .env:"
echo "DB_TYPE=postgresql"
echo "DB_HOST=localhost"
echo "DB_PORT=5432"
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
echo ""
echo "🚀 Ahora puedes ejecutar: python migrate_to_postgres.py"