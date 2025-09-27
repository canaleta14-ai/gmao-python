# Sistema de Gestión de Mantenimiento (GMAO)

Un sistema completo de gestión de mantenimiento asistido por ordenador (GMAO) desarrollado con Flask y SQLAlchemy.

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- Git
- VS Code (recomendado)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd gmao
   ```

2. **Configurar entorno virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Inicializar base de datos**
   ```bash
   python init_db.py
   ```

6. **Ejecutar la aplicación**
   ```bash
   python run.py
   ```

   O usando VS Code: `Ctrl+Shift+B` → "Run Flask App"

## 🛠️ Desarrollo

### Configuración de VS Code

El proyecto incluye configuración optimizada de VS Code en la carpeta `.vscode/`:

- **UTF-8 encoding** por defecto
- **Black** para formateo de Python
- **Prettier** para JavaScript/CSS
- Tareas preconfiguradas (Run, Test, Install)
- Configuraciones de debugging

### Estructura del Proyecto

```
gmao/
├── app/                    # Código principal de la aplicación
│   ├── controllers/        # Lógica de controladores
│   ├── models/            # Modelos de base de datos
│   ├── routes/            # Definición de rutas
│   ├── templates/         # Plantillas Jinja2
│   ├── static/            # Archivos estáticos (CSS, JS, imágenes)
│   └── utils/             # Utilidades
├── instance/              # Base de datos y configuración local
├── static/                # Archivos estáticos adicionales
├── uploads/               # Archivos subidos por usuarios
├── .vscode/               # Configuración de VS Code
├── tests/                 # Archivos de prueba
└── requirements.txt       # Dependencias Python
```

### Funcionalidades Principales

- ✅ Gestión de activos
- ✅ Órdenes de trabajo
- ✅ Planes de mantenimiento preventivo
- ✅ Inventario
- ✅ Gestión de proveedores
- ✅ Usuarios y permisos
- ✅ Reportes y estadísticas
- ✅ Sistema de alertas

## 🐳 Docker

### Desarrollo con Docker Compose

```bash
# Construir y ejecutar
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f gmao-app

# Detener
docker-compose down
```

### Producción

```bash
# Construir imagen
docker build -t gmao-app .

# Ejecutar contenedor
docker run -p 5000:5000 gmao-app
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app --cov-report=html

# Ejecutar tests específicos
pytest test_usuarios.py -v
```

## 📊 Base de Datos

### Desarrollo (SQLite)
- Archivo: `instance/database.db`
- Automáticamente creado con `init_db.py`

### Producción (PostgreSQL/MySQL)
Configurar `DATABASE_URL` en `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/gmao_db
DATABASE_URL=mysql://user:pass@localhost:3306/gmao_db
```

## 🔧 Configuración

### Variables de Entorno

Ver `.env.example` para todas las opciones disponibles.

### Configuración de Producción

- Cambiar `FLASK_ENV=production`
- Configurar `SECRET_KEY` segura
- Usar base de datos PostgreSQL/MySQL
- Configurar servidor web (Gunicorn/Nginx)

## 📝 API

La aplicación incluye endpoints RESTful para integración con otros sistemas.

### Endpoints Principales

- `GET /api/activos` - Listar activos
- `POST /api/ordenes` - Crear orden de trabajo
- `GET /api/inventario` - Estado del inventario

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 📞 Soporte

Para soporte técnico o reportar bugs, crear un issue en el repositorio.

## 🔄 Actualizaciones

### v1.0.0
- Sistema básico de gestión de activos
- Órdenes de trabajo
- Planes de mantenimiento
- Gestión de usuarios

### Próximas Funcionalidades
- [ ] Dashboard con métricas en tiempo real
- [ ] API REST completa
- [ ] Integración con IoT
- [ ] Móvil app
- [ ] Reportes avanzados