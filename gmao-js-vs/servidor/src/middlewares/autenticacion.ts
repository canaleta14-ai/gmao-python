// Middleware de autenticación JWT
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { prisma } from '../index.js';
import { ErrorAutenticacion, ErrorPermisos } from './errores.js';

// Extender el tipo Request para incluir el usuario
declare global {
  namespace Express {
    interface Request {
      usuario?: {
        id: number;
        email: string;
        username: string;
        rol: string;
      };
    }
  }
}

// Verificar token JWT
export const verificarToken = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.startsWith('Bearer ') 
      ? authHeader.substring(7) 
      : null;

    if (!token) {
      throw new ErrorAutenticacion('Token de acceso requerido');
    }

    const secreto = process.env.JWT_SECRET;
    if (!secreto) {
      throw new Error('JWT_SECRET no configurado');
    }

    // Verificar token
    const payload = jwt.verify(token, secreto) as any;
    
    // Buscar usuario en la base de datos
    const usuario = await prisma.usuario.findUnique({
      where: { id: payload.id },
      select: {
        id: true,
        email: true,
        username: true,
        rol: true,
        activo: true,
        ultimoAcceso: true
      }
    });

    if (!usuario) {
      throw new ErrorAutenticacion('Usuario no encontrado');
    }

    if (!usuario.activo) {
      throw new ErrorAutenticacion('Usuario desactivado');
    }

    // Actualizar último acceso
    await prisma.usuario.update({
      where: { id: usuario.id },
      data: { ultimoAcceso: new Date() }
    });

    // Agregar usuario al request
    req.usuario = {
      id: usuario.id,
      email: usuario.email,
      username: usuario.username,
      rol: usuario.rol
    };

    next();
  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      next(new ErrorAutenticacion('Token inválido'));
    } else if (error instanceof jwt.TokenExpiredError) {
      next(new ErrorAutenticacion('Token expirado'));
    } else {
      next(error);
    }
  }
};

// Verificar rol específico
export const verificarRol = (...rolesPermitidos: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.usuario) {
      return next(new ErrorAutenticacion('Usuario no autenticado'));
    }

    if (!rolesPermitidos.includes(req.usuario.rol)) {
      return next(new ErrorPermisos(`Rol requerido: ${rolesPermitidos.join(' o ')}`));
    }

    next();
  };
};

// Verificar si es admin
export const verificarAdmin = verificarRol('ADMIN');

// Verificar si es admin o supervisor
export const verificarSupervisor = verificarRol('ADMIN', 'SUPERVISOR');

// Verificar si es técnico o superior
export const verificarTecnico = verificarRol('ADMIN', 'SUPERVISOR', 'TECNICO');

// Middleware opcional - no lanza error si no hay token
export const autenticacionOpcional = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.startsWith('Bearer ') 
      ? authHeader.substring(7) 
      : null;

    if (!token) {
      return next();
    }

    const secreto = process.env.JWT_SECRET;
    if (!secreto) {
      return next();
    }

    const payload = jwt.verify(token, secreto) as any;
    const usuario = await prisma.usuario.findUnique({
      where: { id: payload.id, activo: true },
      select: {
        id: true,
        email: true,
        username: true,
        rol: true
      }
    });

    if (usuario) {
      req.usuario = usuario;
    }

    next();
  } catch (error) {
    // En autenticación opcional, continuamos sin usuario
    next();
  }
};