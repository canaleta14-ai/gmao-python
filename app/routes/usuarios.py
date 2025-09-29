from flask import Blueprint, request, jsonify, render_template, Response
from flask_login import login_required
import csv
from io import StringIO

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/")
@login_required
def usuarios_page():
    return render_template("usuarios/usuarios.html", section="usuarios")


@usuarios_bp.route("/api", methods=["GET"])
@login_required
def api_usuarios():
    try:
        from app.models.usuario import Usuario

        # Obtener usuarios reales de la base de datos
        usuarios_db = Usuario.query.all()

        usuarios_data = []
        for usuario in usuarios_db:
            usuarios_data.append(
                {
                    "id": usuario.id,
                    "codigo": f"USR{str(usuario.id).zfill(3)}",  # Generar código basado en ID
                    "nombre": usuario.nombre,
                    "email": usuario.email,
                    "telefono": "",  # No tenemos teléfono en la DB actual
                    "departamento": "Mantenimiento",  # Valor por defecto
                    "cargo": (
                        "Técnico" if usuario.rol != "Administrador" else "Administrador"
                    ),
                    "estado": "Activo" if usuario.activo else "Inactivo",
                    "fecha_ingreso": (
                        usuario.fecha_creacion.strftime("%Y-%m-%d")
                        if usuario.fecha_creacion
                        else "2023-01-01"
                    ),
                    "rol": usuario.rol,
                    "permisos": (
                        ["*"]
                        if usuario.rol == "Administrador"
                        else ["mantenimiento.leer"]
                    ),
                }
            )

        return jsonify(
            {"success": True, "usuarios": usuarios_data, "total": len(usuarios_data)}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@usuarios_bp.route("/api", methods=["POST"])
@login_required
def crear_usuario_api():
    try:
        from app.models.usuario import Usuario
        from app.extensions import db

        data = request.get_json()

        # Validar campos requeridos
        required_fields = ["username", "email", "password", "nombre"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify(
                        {"success": False, "error": f"El campo {field} es requerido"}
                    ),
                    400,
                )

        # Verificar que el username no exista
        if Usuario.query.filter_by(username=data["username"]).first():
            return (
                jsonify({"success": False, "error": "El nombre de usuario ya existe"}),
                400,
            )

        # Verificar que el email no exista
        if Usuario.query.filter_by(email=data["email"]).first():
            return (
                jsonify({"success": False, "error": "El email ya está registrado"}),
                400,
            )

        # Crear el nuevo usuario
        nuevo_usuario = Usuario(
            username=data["username"],
            email=data["email"],
            nombre=data["nombre"],
            rol=data.get("rol", "Técnico"),
            activo=data.get("activo", True),
        )

        # Establecer la contraseña encriptada
        nuevo_usuario.set_password(data["password"])

        # Guardar en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Usuario creado correctamente",
                "id": nuevo_usuario.id,
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@usuarios_bp.route("/api/<int:user_id>", methods=["GET"])
@login_required
def obtener_usuario_api(user_id):
    try:
        from app.models.usuario import Usuario

        # Buscar el usuario
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404

        # Retornar datos del usuario
        usuario_data = {
            "id": usuario.id,
            "codigo": f"USR{str(usuario.id).zfill(3)}",
            "username": usuario.username,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "telefono": "",  # No tenemos teléfono en la DB actual
            "departamento": "Mantenimiento",  # Valor por defecto
            "cargo": ("Técnico" if usuario.rol != "Administrador" else "Administrador"),
            "estado": "Activo" if usuario.activo else "Inactivo",
            "fecha_ingreso": (
                usuario.fecha_creacion.strftime("%Y-%m-%d")
                if usuario.fecha_creacion
                else "2023-01-01"
            ),
            "rol": usuario.rol,
            "permisos": (
                ["*"] if usuario.rol == "Administrador" else ["mantenimiento.leer"]
            ),
        }

        return jsonify({"success": True, "usuario": usuario_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@usuarios_bp.route("/api/<int:user_id>", methods=["PUT"])
@login_required
def actualizar_usuario_api(user_id):
    try:
        from app.models.usuario import Usuario
        from app.extensions import db

        data = request.get_json()

        # Buscar el usuario
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404

        # Validar campos requeridos
        required_fields = ["username", "email", "nombre"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify(
                        {"success": False, "error": f"El campo {field} es requerido"}
                    ),
                    400,
                )

        # Verificar que el username no exista (excepto para el usuario actual)
        existing_user = Usuario.query.filter_by(username=data["username"]).first()
        if existing_user and existing_user.id != user_id:
            return (
                jsonify({"success": False, "error": "El nombre de usuario ya existe"}),
                400,
            )

        # Verificar que el email no exista (excepto para el usuario actual)
        existing_user = Usuario.query.filter_by(email=data["email"]).first()
        if existing_user and existing_user.id != user_id:
            return (
                jsonify({"success": False, "error": "El email ya está registrado"}),
                400,
            )

        # Actualizar los campos
        usuario.username = data["username"]
        usuario.email = data["email"]
        usuario.nombre = data["nombre"]
        usuario.rol = data.get("rol", "Técnico")

        # Convertir estado "Activo"/"Inactivo" a booleano
        estado = data.get("estado", "Activo")
        usuario.activo = estado == "Activo"

        # Actualizar contraseña solo si se proporcionó
        if data.get("password"):
            usuario.set_password(data["password"])

        # Guardar cambios
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Usuario {usuario.nombre} actualizado correctamente",
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@usuarios_bp.route("/api/<int:user_id>", methods=["DELETE"])
@login_required
def eliminar_usuario_api(user_id):
    try:
        from app.models.usuario import Usuario
        from app.extensions import db

        # Buscar el usuario en la base de datos
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404

        # No permitir eliminar el usuario admin
        if usuario.username == "admin":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No se puede eliminar el usuario administrador",
                    }
                ),
                403,
            )

        # Eliminar el usuario
        nombre_usuario = usuario.nombre
        db.session.delete(usuario)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Usuario {nombre_usuario} eliminado correctamente",
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@usuarios_bp.route("/api/roles", methods=["GET"])
@login_required
def api_roles():
    try:
        roles_data = [
            {
                "id": 1,
                "nombre": "Administrador",
                "descripcion": "Acceso completo al sistema",
                "permisos": ["*"],
                "color": "danger",
            },
            {
                "id": 2,
                "nombre": "Supervisor",
                "descripcion": "Supervisión y gestión de equipos",
                "permisos": [
                    "usuarios.leer",
                    "activos.leer",
                    "ordenes.leer",
                    "operaciones.leer",
                    "operaciones.editar",
                ],
                "color": "warning",
            },
            {
                "id": 3,
                "nombre": "Técnico",
                "descripcion": "Operaciones técnicas y mantenimiento",
                "permisos": [
                    "mantenimiento.leer",
                    "mantenimiento.editar",
                    "ordenes.crear",
                    "ordenes.editar",
                    "activos.leer",
                ],
                "color": "primary",
            },
            {
                "id": 4,
                "nombre": "Operador",
                "descripcion": "Operaciones básicas",
                "permisos": ["ordenes.leer", "activos.leer"],
                "color": "secondary",
            },
        ]
        return jsonify({"success": True, "roles": roles_data, "total": len(roles_data)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@usuarios_bp.route("/exportar-csv", methods=["GET"])
@login_required
def exportar_csv():
    """Exporta todos los usuarios a CSV"""
    try:
        from app.models.usuario import Usuario

        # Obtener todos los usuarios
        usuarios = Usuario.query.all()

        output = StringIO()
        writer = csv.writer(output)

        # Escribir encabezados
        writer.writerow(
            [
                "ID",
                "Código",
                "Nombre",
                "Email",
                "Teléfono",
                "Departamento",
                "Cargo",
                "Rol",
                "Estado",
                "Fecha Ingreso",
            ]
        )

        # Escribir datos de usuarios
        for usuario in usuarios:
            writer.writerow(
                [
                    usuario.id,
                    f"USR{str(usuario.id).zfill(3)}",  # Código generado
                    usuario.nombre,
                    usuario.email,
                    "",  # Teléfono (no disponible en el modelo actual)
                    "Mantenimiento",  # Departamento por defecto
                    (
                        "Técnico" if usuario.rol != "Administrador" else "Administrador"
                    ),  # Cargo
                    usuario.rol,
                    "Activo" if usuario.activo else "Inactivo",
                    (
                        usuario.fecha_creacion.strftime("%Y-%m-%d")
                        if usuario.fecha_creacion
                        else "2023-01-01"
                    ),
                ]
            )

        # Preparar respuesta
        output.seek(0)
        csv_data = output.getvalue()
        output.close()

        response = Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=usuarios.csv"},
        )
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
