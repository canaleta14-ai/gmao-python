#!/bin/bash

# Directorio de la aplicación
APP_DIR="/home/gmao/gmao-python/gmao-sistema"
cd $APP_DIR

# Activar entorno virtual
source .venv/bin/activate

# Crear directorio de logs si no existe
mkdir -p logs

# Variables de entorno
export FLASK_APP=run.py
export FLASK_ENV=production

# Iniciar Gunicorn
exec gunicorn \
    --config gunicorn_config.py \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    "app.factory:create_app()"
