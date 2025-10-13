// Utilidades para crear el README.md del proyecto
export const crearReadme = () => `# Sistema GMAO (Gestión de Mantenimiento Asistido por Ordenador)

Un sistema completo de gestión de mantenimiento desarrollado con tecnologías modernas de JavaScript/TypeScript.

## 🚀 Tecnologías Utilizadas

### Backend (Servidor)
- **Node.js** + **Express.js** - Framework del servidor
- **TypeScript** - Tipado estático
- **Prisma ORM** - Mapeo objeto-relacional
- **PostgreSQL** - Base de datos
- **JWT** - Autenticación
- **bcrypt** - Encriptación de contraseñas
- **Helmet** - Seguridad HTTP
- **CORS** - Control de acceso entre dominios
- **Rate Limiting** - Limitación de velocidad

### Frontend (Cliente)
- **React 18** - Librería de UI
- **TypeScript** - Tipado estático
- **Vite** - Herramienta de construcción
- **Tailwind CSS** - Framework de estilos
- **React Router** - Enrutamiento
- **Axios** - Cliente HTTP
- **React Hook Form** - Gestión de formularios
- **React Query** - Gestión de estado del servidor

## 📁 Estructura del Proyecto

\`\`\`
gmao-js-vs/
├── servidor/                 # Backend API
│   ├── src/
│   │   ├── controladores/   # Lógica de negocio
│   │   ├── rutas/          # Definición de rutas
│   │   ├── middlewares/    # Middlewares personalizados
│   │   ├── servicios/      # Servicios de negocio
│   │   ├── utils/          # Utilidades
│   │   └── index.ts        # Punto de entrada
│   ├── prisma/
│   │   └── schema.prisma   # Esquema de base de datos
│   └── package.json
├── cliente/                 # Frontend React
│   ├── src/
│   │   ├── componentes/    # Componentes React
│   │   ├── paginas/        # Páginas principales
│   │   ├── hooks/          # Hooks personalizados
│   │   ├── servicios/      # Servicios API
│   │   ├── tipos/          # Definiciones TypeScript
│   │   └── main.tsx        # Punto de entrada
│   └── package.json
└── package.json            # Configuración del workspace
\`\`\`

## ⚡ Características Principales

### 🔧 Gestión de Activos
- Registro y seguimiento de activos
- Histórico de mantenimiento
- Clasificación por tipo y prioridad
- Gestión de ubicaciones

### 📋 Órdenes de Trabajo
- Creación de órdenes preventivas y correctivas
- Asignación de técnicos
- Seguimiento de estados
- Control de tiempos y costos

### 📅 Planes de Mantenimiento
- Mantenimiento preventivo programado
- Frecuencias personalizables
- Asignación de responsables
- Generación automática de órdenes

### 📦 Gestión de Inventario
- Control de repuestos y materiales
- Movimientos de entrada y salida
- Alertas de stock mínimo
- Integración con órdenes de trabajo

### 👥 Gestión de Usuarios
- Sistema de roles (Admin, Supervisor, Técnico, Operador)
- Autenticación JWT
- Permisos granulares
- Histórico de accesos

### 🔔 Sistema de Alertas
- Notificaciones de mantenimiento vencido
- Alertas de stock bajo
- Seguimiento de órdenes críticas
- Panel de alertas personalizable

### 📊 Reportes y Dashboard
- Indicadores clave de rendimiento (KPIs)
- Gráficos y estadísticas
- Reportes personalizables
- Dashboard en tiempo real

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Node.js (v18 o superior)
- PostgreSQL (v12 o superior)
- npm o yarn

### 1. Clonar el repositorio
\`\`\`bash
git clone <url-del-repositorio>
cd gmao-js-vs
\`\`\`

### 2. Instalar dependencias
\`\`\`bash
# Instalar dependencias del workspace
npm install

# Instalar dependencias del servidor
cd servidor
npm install

# Instalar dependencias del cliente
cd ../cliente
npm install
\`\`\`

### 3. Configurar variables de entorno

#### Servidor (\`servidor/.env\`)
\`\`\`env
DATABASE_URL="postgresql://usuario:contraseña@localhost:5432/gmao_db"
JWT_SECRET="tu_jwt_secret_super_seguro"
JWT_EXPIRES_IN="24h"
PORT=3001
NODE_ENV="development"
CORS_ORIGIN="http://localhost:3000"
\`\`\`

### 4. Configurar base de datos
\`\`\`bash
cd servidor

# Generar cliente Prisma
npx prisma generate

# Ejecutar migraciones
npx prisma migrate dev --name init

# (Opcional) Poblar con datos de prueba
npx prisma db seed
\`\`\`

### 5. Ejecutar el proyecto

#### Modo desarrollo (ambos servicios)
\`\`\`bash
# Desde la raíz del proyecto
npm run dev
\`\`\`

#### Ejecutar servicios por separado
\`\`\`bash
# Servidor (puerto 3001)
cd servidor
npm run dev

# Cliente (puerto 3000)
cd cliente
npm run dev
\`\`\`

## 🔑 API Endpoints

### Autenticación
- \`POST /api/auth/login\` - Iniciar sesión
- \`POST /api/auth/registrar\` - Registrar usuario
- \`GET /api/auth/perfil\` - Obtener perfil
- \`PUT /api/auth/cambiar-password\` - Cambiar contraseña

### Usuarios
- \`GET /api/usuarios\` - Listar usuarios
- \`POST /api/usuarios\` - Crear usuario
- \`PUT /api/usuarios/:id\` - Actualizar usuario
- \`DELETE /api/usuarios/:id\` - Eliminar usuario

### Activos
- \`GET /api/activos\` - Listar activos
- \`POST /api/activos\` - Crear activo
- \`PUT /api/activos/:id\` - Actualizar activo
- \`DELETE /api/activos/:id\` - Eliminar activo

### Órdenes de Trabajo
- \`GET /api/ordenes\` - Listar órdenes
- \`POST /api/ordenes\` - Crear orden
- \`PUT /api/ordenes/:id\` - Actualizar orden
- \`DELETE /api/ordenes/:id\` - Eliminar orden

### Inventario
- \`GET /api/inventario\` - Listar inventario
- \`POST /api/inventario\` - Crear item
- \`PUT /api/inventario/:id\` - Actualizar item
- \`POST /api/inventario/:id/movimiento\` - Registrar movimiento

## 🧪 Testing

\`\`\`bash
# Tests del servidor
cd servidor
npm test

# Tests del cliente
cd cliente
npm test
\`\`\`

## 📦 Construcción para Producción

\`\`\`bash
# Construir ambos proyectos
npm run build

# Solo servidor
cd servidor
npm run build

# Solo cliente
cd cliente
npm run build
\`\`\`

## 🔒 Seguridad

- Autenticación JWT con expiración configurable
- Encriptación de contraseñas con bcrypt
- Helmet para headers de seguridad HTTP
- Rate limiting para prevenir ataques
- Validación de entrada en todas las rutas
- CORS configurado correctamente

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo \`LICENSE\` para más detalles.

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (\`git checkout -b feature/nueva-caracteristica\`)
3. Commit tus cambios (\`git commit -am 'Agregar nueva característica'\`)
4. Push a la rama (\`git push origin feature/nueva-caracteristica\`)
5. Crea un Pull Request

## 📞 Soporte

Para soporte técnico o consultas, crear un issue en el repositorio del proyecto.

---

**Sistema GMAO** - Gestión de Mantenimiento Moderna y Eficiente 🔧⚡
`;

export default crearReadme;