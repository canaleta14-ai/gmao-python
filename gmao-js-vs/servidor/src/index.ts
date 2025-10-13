import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';

// Importar rutas
import rutasAutenticacion from './rutas/autenticacion';
import rutasUsuarios from './rutas/usuarios';
import rutasActivos from './rutas/activos';
import rutasOrdenes from './rutas/ordenes';
import rutasInventario from './rutas/inventario';
import rutasProveedores from './rutas/proveedores';
import rutasPlanes from './rutas/planes';
import rutasReportes from './rutas/reportes';
import rutasAlertas from './rutas/alertas';

// Importar middleware
import { manejarErrores } from './middleware/errores';
import { logger } from './utils/logger';

// Cargar variables de entorno
dotenv.config();

const app = express();
const puerto = process.env.PUERTO || 3001;

// Inicializar Prisma
export const prisma = new PrismaClient();

// Middleware de seguridad
app.use(helmet());
app.use(cors({
  origin: process.env.URL_CLIENTE || 'http://localhost:5173',
  credentials: true
}));

// Limitador de velocidad
const limitador = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // Límite de 100 solicitudes por ventana de tiempo
  message: 'Demasiadas solicitudes desde esta IP, intente de nuevo más tarde.'
});
app.use(limitador);

// Middleware general
app.use(compression());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rutas de la API
app.use('/api/auth', rutasAutenticacion);
app.use('/api/usuarios', rutasUsuarios);
app.use('/api/activos', rutasActivos);
app.use('/api/ordenes', rutasOrdenes);
app.use('/api/inventario', rutasInventario);
app.use('/api/proveedores', rutasProveedores);
app.use('/api/planes', rutasPlanes);
app.use('/api/reportes', rutasReportes);
app.use('/api/alertas', rutasAlertas);

// Ruta de prueba
app.get('/api/salud', (req, res) => {
  res.json({ 
    mensaje: 'Servidor GMAO funcionando correctamente',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Middleware de manejo de errores (debe ir al final)
app.use(manejarErrores);

// Iniciar servidor
const iniciarServidor = async () => {
  try {
    // Conectar a la base de datos
    await prisma.$connect();
    logger.info('Conexión a la base de datos establecida');

    // Iniciar servidor
    app.listen(puerto, () => {
      logger.info(`Servidor GMAO iniciado en puerto ${puerto}`);
      logger.info(`URL: http://localhost:${puerto}`);
    });
  } catch (error) {
    logger.error('Error al iniciar el servidor:', error);
    process.exit(1);
  }
};

// Manejar cierre graceful
process.on('SIGINT', async () => {
  logger.info('Cerrando servidor...');
  await prisma.$disconnect();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('Cerrando servidor...');
  await prisma.$disconnect();
  process.exit(0);
});

// Iniciar la aplicación
iniciarServidor();

export default app;