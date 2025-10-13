// Middleware para manejar errores de la aplicación
import { Request, Response, NextFunction } from 'express';
import { Prisma } from '@prisma/client';

// Tipo para errores personalizados
export interface ErrorPersonalizado extends Error {
  statusCode?: number;
  codigo?: string;
  detalles?: any;
}

// Clase para errores de validación
export class ErrorValidacion extends Error {
  statusCode: number;
  codigo: string;
  detalles: any;

  constructor(mensaje: string, detalles: any = null) {
    super(mensaje);
    this.name = 'ErrorValidacion';
    this.statusCode = 400;
    this.codigo = 'VALIDATION_ERROR';
    this.detalles = detalles;
  }
}

// Clase para errores de autenticación
export class ErrorAutenticacion extends Error {
  statusCode: number;
  codigo: string;

  constructor(mensaje: string = 'No autorizado') {
    super(mensaje);
    this.name = 'ErrorAutenticacion';
    this.statusCode = 401;
    this.codigo = 'AUTH_ERROR';
  }
}

// Clase para errores de permisos
export class ErrorPermisos extends Error {
  statusCode: number;
  codigo: string;

  constructor(mensaje: string = 'Permisos insuficientes') {
    super(mensaje);
    this.name = 'ErrorPermisos';
    this.statusCode = 403;
    this.codigo = 'PERMISSION_ERROR';
  }
}

// Clase para errores de recurso no encontrado
export class ErrorNoEncontrado extends Error {
  statusCode: number;
  codigo: string;

  constructor(mensaje: string = 'Recurso no encontrado') {
    super(mensaje);
    this.name = 'ErrorNoEncontrado';
    this.statusCode = 404;
    this.codigo = 'NOT_FOUND';
  }
}

// Función para manejar errores de Prisma
const manejarErrorPrisma = (error: Prisma.PrismaClientKnownRequestError) => {
  switch (error.code) {
    case 'P2002':
      return {
        statusCode: 400,
        codigo: 'DUPLICATE_ERROR',
        mensaje: 'Ya existe un registro con estos datos únicos',
        detalles: error.meta
      };
    case 'P2025':
      return {
        statusCode: 404,
        codigo: 'NOT_FOUND',
        mensaje: 'Registro no encontrado',
        detalles: error.meta
      };
    case 'P2003':
      return {
        statusCode: 400,
        codigo: 'FOREIGN_KEY_ERROR',
        mensaje: 'Error de referencia: el registro está siendo usado por otros datos',
        detalles: error.meta
      };
    case 'P2014':
      return {
        statusCode: 400,
        codigo: 'RELATION_ERROR',
        mensaje: 'La operación falló debido a una violación de relación',
        detalles: error.meta
      };
    default:
      return {
        statusCode: 500,
        codigo: 'DATABASE_ERROR',
        mensaje: 'Error en la base de datos',
        detalles: process.env.NODE_ENV === 'development' ? error.message : null
      };
  }
};

// Middleware principal de manejo de errores
export const manejarErrores = (
  error: ErrorPersonalizado | Prisma.PrismaClientKnownRequestError | Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  console.error('Error capturado:', {
    nombre: error.name,
    mensaje: error.message,
    stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    url: req.url,
    metodo: req.method,
    ip: req.ip,
    timestamp: new Date().toISOString()
  });

  // Error de Prisma
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    const errorInfo = manejarErrorPrisma(error);
    return res.status(errorInfo.statusCode).json({
      exito: false,
      error: errorInfo.mensaje,
      codigo: errorInfo.codigo,
      detalles: errorInfo.detalles
    });
  }

  // Error personalizado con statusCode
  if ('statusCode' in error && error.statusCode) {
    return res.status(error.statusCode).json({
      exito: false,
      error: error.message,
      codigo: error.codigo || 'CUSTOM_ERROR',
      detalles: 'detalles' in error ? error.detalles : null
    });
  }

  // Error de validación de JSON
  if (error instanceof SyntaxError && 'body' in error) {
    return res.status(400).json({
      exito: false,
      error: 'Formato JSON inválido',
      codigo: 'INVALID_JSON'
    });
  }

  // Error genérico del servidor
  res.status(500).json({
    exito: false,
    error: process.env.NODE_ENV === 'production' 
      ? 'Error interno del servidor' 
      : error.message,
    codigo: 'INTERNAL_SERVER_ERROR',
    ...(process.env.NODE_ENV === 'development' && { 
      stack: error.stack 
    })
  });
};

// Middleware para capturar errores asíncronos
export const capturarAsync = (fn: Function) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};