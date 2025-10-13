// Ruta de autenticación - Login, registro, logout
import { Router } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { prisma } from '../index.js';
import { 
  ErrorValidacion, 
  ErrorAutenticacion, 
  capturarAsync 
} from '../middlewares/errores.js';
import { verificarToken } from '../middlewares/autenticacion.js';

const router = Router();

// Registrar nuevo usuario
router.post('/registrar', capturarAsync(async (req, res) => {
  const { nombre, email, username, password, rol = 'OPERADOR' } = req.body;

  // Validaciones básicas
  if (!nombre || !email || !username || !password) {
    throw new ErrorValidacion('Todos los campos son requeridos');
  }

  if (password.length < 6) {
    throw new ErrorValidacion('La contraseña debe tener al menos 6 caracteres');
  }

  // Verificar que el email sea válido
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    throw new ErrorValidacion('Formato de email inválido');
  }

  // Verificar que el rol sea válido
  const rolesValidos = ['ADMIN', 'SUPERVISOR', 'TECNICO', 'OPERADOR'];
  if (!rolesValidos.includes(rol)) {
    throw new ErrorValidacion('Rol inválido');
  }

  // Verificar si el usuario ya existe
  const usuarioExistente = await prisma.usuario.findFirst({
    where: {
      OR: [
        { email: email },
        { username: username }
      ]
    }
  });

  if (usuarioExistente) {
    throw new ErrorValidacion('El email o nombre de usuario ya están en uso');
  }

  // Encriptar contraseña
  const saltRounds = 12;
  const passwordEncriptada = await bcrypt.hash(password, saltRounds);

  // Crear usuario
  const nuevoUsuario = await prisma.usuario.create({
    data: {
      nombre,
      email: email.toLowerCase(),
      username,
      password: passwordEncriptada,
      rol
    },
    select: {
      id: true,
      nombre: true,
      email: true,
      username: true,
      rol: true,
      fechaCreacion: true
    }
  });

  res.status(201).json({
    exito: true,
    mensaje: 'Usuario registrado exitosamente',
    usuario: nuevoUsuario
  });
}));

// Iniciar sesión
router.post('/login', capturarAsync(async (req, res) => {
  const { login, password } = req.body;

  // Validaciones
  if (!login || !password) {
    throw new ErrorValidacion('Login y contraseña son requeridos');
  }

  // Buscar usuario por email o username
  const usuario = await prisma.usuario.findFirst({
    where: {
      OR: [
        { email: login.toLowerCase() },
        { username: login }
      ]
    }
  });

  if (!usuario) {
    throw new ErrorAutenticacion('Credenciales inválidas');
  }

  if (!usuario.activo) {
    throw new ErrorAutenticacion('Usuario desactivado');
  }

  // Verificar contraseña
  const passwordValida = await bcrypt.compare(password, usuario.password);
  if (!passwordValida) {
    throw new ErrorAutenticacion('Credenciales inválidas');
  }

  // Generar token JWT
  const secreto = process.env.JWT_SECRET;
  if (!secreto) {
    throw new Error('JWT_SECRET no configurado');
  }

  const payload = {
    id: usuario.id,
    email: usuario.email,
    username: usuario.username,
    rol: usuario.rol
  };

  const token = jwt.sign(
    payload, 
    secreto, 
    { 
      expiresIn: process.env.JWT_EXPIRES_IN || '24h',
      issuer: 'gmao-system',
      audience: 'gmao-users'
    }
  );

  // Actualizar último acceso
  await prisma.usuario.update({
    where: { id: usuario.id },
    data: { ultimoAcceso: new Date() }
  });

  res.json({
    exito: true,
    mensaje: 'Inicio de sesión exitoso',
    token,
    usuario: {
      id: usuario.id,
      nombre: usuario.nombre,
      email: usuario.email,
      username: usuario.username,
      rol: usuario.rol
    }
  });
}));

// Obtener perfil del usuario actual
router.get('/perfil', verificarToken, capturarAsync(async (req, res) => {
  const usuario = await prisma.usuario.findUnique({
    where: { id: req.usuario!.id },
    select: {
      id: true,
      nombre: true,
      email: true,
      username: true,
      rol: true,
      fechaCreacion: true,
      ultimoAcceso: true
    }
  });

  if (!usuario) {
    throw new ErrorAutenticacion('Usuario no encontrado');
  }

  res.json({
    exito: true,
    usuario
  });
}));

// Cambiar contraseña
router.put('/cambiar-password', verificarToken, capturarAsync(async (req, res) => {
  const { passwordActual, passwordNueva } = req.body;

  if (!passwordActual || !passwordNueva) {
    throw new ErrorValidacion('Contraseña actual y nueva son requeridas');
  }

  if (passwordNueva.length < 6) {
    throw new ErrorValidacion('La nueva contraseña debe tener al menos 6 caracteres');
  }

  // Buscar usuario con contraseña
  const usuario = await prisma.usuario.findUnique({
    where: { id: req.usuario!.id }
  });

  if (!usuario) {
    throw new ErrorAutenticacion('Usuario no encontrado');
  }

  // Verificar contraseña actual
  const passwordValida = await bcrypt.compare(passwordActual, usuario.password);
  if (!passwordValida) {
    throw new ErrorAutenticacion('Contraseña actual incorrecta');
  }

  // Encriptar nueva contraseña
  const saltRounds = 12;
  const nuevaPasswordEncriptada = await bcrypt.hash(passwordNueva, saltRounds);

  // Actualizar contraseña
  await prisma.usuario.update({
    where: { id: usuario.id },
    data: { password: nuevaPasswordEncriptada }
  });

  res.json({
    exito: true,
    mensaje: 'Contraseña actualizada exitosamente'
  });
}));

// Renovar token
router.post('/renovar-token', verificarToken, capturarAsync(async (req, res) => {
  const secreto = process.env.JWT_SECRET;
  if (!secreto) {
    throw new Error('JWT_SECRET no configurado');
  }

  const payload = {
    id: req.usuario!.id,
    email: req.usuario!.email,
    username: req.usuario!.username,
    rol: req.usuario!.rol
  };

  const nuevoToken = jwt.sign(
    payload, 
    secreto, 
    { 
      expiresIn: process.env.JWT_EXPIRES_IN || '24h',
      issuer: 'gmao-system',
      audience: 'gmao-users'
    }
  );

  res.json({
    exito: true,
    mensaje: 'Token renovado exitosamente',
    token: nuevoToken
  });
}));

// Cerrar sesión (en el frontend se debe eliminar el token)
router.post('/logout', verificarToken, capturarAsync(async (req, res) => {
  res.json({
    exito: true,
    mensaje: 'Sesión cerrada exitosamente'
  });
}));

export default router;