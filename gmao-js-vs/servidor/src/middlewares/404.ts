// Middleware para manejar rutas no encontradas (404)
import { Request, Response, NextFunction } from 'express';

export const middleware404 = (req: Request, res: Response, next: NextFunction) => {
  res.status(404).json({
    exito: false,
    error: 'Ruta no encontrada',
    codigo: 'NOT_FOUND',
    mensaje: `La ruta ${req.method} ${req.originalUrl} no existe`,
    timestamp: new Date().toISOString()
  });
};