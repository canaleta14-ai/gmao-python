-- Agregar columna apellidos si no existe
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS apellidos VARCHAR(100);

-- Insertar usuario admin (ahora sí funcionará)
INSERT INTO usuario (username, email, nombre, apellidos, password_hash, rol, activo)
VALUES ('admin', 'admin@mantenimiento.com', 'Administrador', 'Sistema',
    'scrypt:32768:8:1$8ZGiIdkR6hKgEBjS$3d4a1f8b9c2e5d8a7f6e9c8b5a4d7f0e3c6b9a8e5d2f1c4b7a0e9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d8c5b2f7e0a9d6c3f8b5a2e7d0c9f6b3a8e5d2c7f0b9a6e3d',
    'admin', true)
ON CONFLICT (username) DO NOTHING;

-- Verificar que se creó
SELECT username, email, nombre, rol FROM usuario WHERE username = 'admin';
