import multiprocessing

# Configuración del servidor
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
loglevel = "info"

# Proceso
daemon = False
pidfile = "gunicorn.pid"

# Seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Reload automático en desarrollo (desactivar en producción)
reload = False

# Preload de la aplicación para mejor rendimiento
preload_app = True

# Graceful timeout
graceful_timeout = 30
