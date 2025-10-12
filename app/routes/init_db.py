"""
Endpoint para inicializar la base de datos desde la aplicación desplegada
"""

from flask import Blueprint, jsonify
from app.extensions import db
from app.models.usuario import Usuario

init_bp = Blueprint("init_db", __name__)


@init_bp.route("/admin/init-database", methods=["GET"])
def init_database():
    """Inicializa la base de datos con todas las tablas y usuario admin"""
    try:
        print("🚀 Iniciando inicialización de base de datos...")

        # 1. Verificar conexión
        result = db.session.execute(db.text("SELECT current_database(), current_user"))
        db_info = result.fetchone()

        # 2. Verificar tablas existentes
        result = db.session.execute(
            db.text(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            )
        )
        tablas_antes = [row[0] for row in result.fetchall()]

        # 3. Crear todas las tablas
        db.create_all()

        # 4. Verificar tablas después de creación
        result = db.session.execute(
            db.text(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            )
        )
        tablas_despues = [row[0] for row in result.fetchall()]

        # 5. Crear usuario admin si no existe
        admin_existente = Usuario.query.filter_by(username="admin").first()
        usuario_info = ""

        if admin_existente:
            admin_existente.set_password("admin123")
            db.session.commit()
            usuario_info = "Usuario admin actualizado"
        else:
            admin = Usuario(
                username="admin",
                email="admin@gmao.com",
                nombre="Administrador",
                rol="Administrador",
                activo=True,
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            usuario_info = "Usuario admin creado"

        # 6. Verificar conteos
        verificaciones = {}
        tablas_verificar = ["usuario", "activo", "plan_mantenimiento", "orden_trabajo"]
        for tabla in tablas_verificar:
            try:
                result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {tabla}"))
                count = result.scalar()
                verificaciones[tabla] = count
            except Exception as e:
                verificaciones[tabla] = f"Error: {str(e)}"

        return jsonify(
            {
                "success": True,
                "message": "Base de datos inicializada correctamente",
                "database": db_info[0] if db_info else "unknown",
                "user": db_info[1] if db_info else "unknown",
                "tablas_antes": len(tablas_antes),
                "tablas_despues": len(tablas_despues),
                "tablas_creadas": list(set(tablas_despues) - set(tablas_antes)),
                "todas_las_tablas": tablas_despues,
                "usuario_admin": usuario_info,
                "verificaciones": verificaciones,
            }
        )

    except Exception as e:
        import traceback

        return (
            jsonify(
                {"success": False, "error": str(e), "traceback": traceback.format_exc()}
            ),
            500,
        )
