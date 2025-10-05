"""
Script de migración para agregar soporte de archivos adjuntos en solicitudes de servicio.

Este script agrega la columna 'solicitud_servicio_id' a la tabla 'archivo_adjunto'
para permitir adjuntar archivos (fotos) a las solicitudes de servicio.

Cambios:
- Modifica tabla 'archivo_adjunto':
  - Hace nullable la columna 'orden_trabajo_id'
  - Agrega columna 'solicitud_servicio_id' (nullable, FK a solicitud_servicio)
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text, inspect

app = create_app()

with app.app_context():
    print("=" * 70)
    print("MIGRACIÓN: Soporte de archivos adjuntos en solicitudes")
    print("=" * 70)

    try:
        # Detectar tipo de base de datos
        db_type = db.engine.dialect.name
        print(f"\n🔍 Base de datos detectada: {db_type.upper()}")

        # Verificar si la tabla archivo_adjunto existe
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        if "archivo_adjunto" not in tables:
            print("\n⚠️  La tabla 'archivo_adjunto' no existe.")
            print("   Creando todas las tablas desde los modelos...")
            db.create_all()
            print("   ✅ Tablas creadas exitosamente")
            print(
                "\n✅ La migración se completó (tablas nuevas ya incluyen la columna)"
            )
            print("=" * 70)
            import sys

            sys.exit(0)

        # Verificar si la columna ya existe (compatible con SQLite y PostgreSQL)
        columns = [col["name"] for col in inspector.get_columns("archivo_adjunto")]

        if "solicitud_servicio_id" in columns:
            print("\n✅ La migración ya fue aplicada anteriormente.")
            print(
                "   La columna 'solicitud_servicio_id' ya existe en 'archivo_adjunto'."
            )
        else:
            print("\n📝 Aplicando migración...")

            if db_type == "sqlite":
                # SQLite requiere recrear la tabla (no soporta ALTER COLUMN)
                print("\n⚠️  SQLite detectado: recreando tabla...")

                # 1. Crear tabla temporal con nueva estructura
                db.session.execute(
                    text(
                        """
                    CREATE TABLE archivo_adjunto_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_original VARCHAR(255) NOT NULL,
                        nombre_archivo VARCHAR(255) NOT NULL,
                        tipo_archivo VARCHAR(50) NOT NULL,
                        extension VARCHAR(10),
                        tamaño INTEGER,
                        ruta_archivo VARCHAR(500),
                        url_enlace VARCHAR(1000),
                        descripcion TEXT,
                        fecha_subida DATETIME,
                        orden_trabajo_id INTEGER,
                        solicitud_servicio_id INTEGER,
                        usuario_id INTEGER,
                        FOREIGN KEY (orden_trabajo_id) REFERENCES orden_trabajo(id),
                        FOREIGN KEY (solicitud_servicio_id) REFERENCES solicitud_servicio(id) ON DELETE CASCADE,
                        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
                    )
                """
                    )
                )
                print("   ✅ Tabla temporal creada")

                # 2. Copiar datos existentes
                db.session.execute(
                    text(
                        """
                    INSERT INTO archivo_adjunto_new 
                    (id, nombre_original, nombre_archivo, tipo_archivo, extension, tamaño, 
                     ruta_archivo, url_enlace, descripcion, fecha_subida, orden_trabajo_id, usuario_id)
                    SELECT id, nombre_original, nombre_archivo, tipo_archivo, extension, tamaño,
                           ruta_archivo, url_enlace, descripcion, fecha_subida, orden_trabajo_id, usuario_id
                    FROM archivo_adjunto
                """
                    )
                )
                print("   ✅ Datos copiados")

                # 3. Eliminar tabla original
                db.session.execute(text("DROP TABLE archivo_adjunto"))
                print("   ✅ Tabla original eliminada")

                # 4. Renombrar tabla nueva
                db.session.execute(
                    text("ALTER TABLE archivo_adjunto_new RENAME TO archivo_adjunto")
                )
                print("   ✅ Tabla renombrada")

                # 5. Crear índice
                db.session.execute(
                    text(
                        """
                    CREATE INDEX idx_archivo_solicitud 
                    ON archivo_adjunto(solicitud_servicio_id)
                """
                    )
                )
                print("   ✅ Índice creado")

            else:
                # PostgreSQL soporta ALTER COLUMN directamente
                print("\n🐘 PostgreSQL detectado: usando ALTER TABLE...")

                # 1. Modificar orden_trabajo_id para permitir NULL
                print("\n1. Modificando 'orden_trabajo_id' para permitir NULL...")
                db.session.execute(
                    text(
                        """
                    ALTER TABLE archivo_adjunto 
                    ALTER COLUMN orden_trabajo_id DROP NOT NULL
                """
                    )
                )
                print("   ✅ Columna 'orden_trabajo_id' ahora permite NULL")

                # 2. Agregar nueva columna solicitud_servicio_id
                print("\n2. Agregando columna 'solicitud_servicio_id'...")
                db.session.execute(
                    text(
                        """
                    ALTER TABLE archivo_adjunto 
                    ADD COLUMN solicitud_servicio_id INTEGER
                """
                    )
                )
                print("   ✅ Columna 'solicitud_servicio_id' creada")

                # 3. Crear clave foránea
                print("\n3. Creando clave foránea a 'solicitud_servicio'...")
                db.session.execute(
                    text(
                        """
                    ALTER TABLE archivo_adjunto
                    ADD CONSTRAINT fk_archivo_solicitud
                    FOREIGN KEY (solicitud_servicio_id) 
                    REFERENCES solicitud_servicio(id)
                    ON DELETE CASCADE
                """
                    )
                )
                print("   ✅ Clave foránea creada")

                # 4. Agregar índice para mejor rendimiento
                print("\n4. Creando índice para mejor rendimiento...")
                db.session.execute(
                    text(
                        """
                    CREATE INDEX idx_archivo_solicitud 
                    ON archivo_adjunto(solicitud_servicio_id)
                """
                    )
                )
                print("   ✅ Índice creado")

            # Confirmar cambios
            db.session.commit()

            print("\n" + "=" * 70)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 70)
            print("\nCambios aplicados:")
            print("  • orden_trabajo_id ahora permite NULL")
            print("  • Nueva columna: solicitud_servicio_id")
            print("  • Clave foránea a solicitud_servicio")
            print("  • Índice para optimización de consultas")
            print("\nAhora las solicitudes de servicio pueden tener archivos adjuntos.")
            print("=" * 70)

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR durante la migración: {e}")
        print("\nLa migración no se completó. Por favor, revise el error.")
        raise
