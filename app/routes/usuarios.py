from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from functools import wraps
from app.controllers.usuarios_controller import (
    crear_usuario,  # type: ignore
    listar_usuarios,  # type: ignore
    editar_usuario,  # type: ignore
    cambiar_rol_usuario,  # type: ignore
    cambiar_estado_usuario,  # type: ignore
    obtener_usuario_por_id,  # type: ignore
    eliminar_usuario,  # type: ignore
    obtener_estadisticas_usuarios,  # type: ignore
)

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def admin_required(f):
    """Decorador para rutas que requieren permisos de administrador"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != "Administrador":
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Acceso denegado. Se requieren permisos de administrador.",
                    }
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated_function


def supervisor_or_admin_required(f):
    """Decorador para rutas que requieren permisos de supervisor o administrador"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol not in [
            "Administrador",
            "Supervisor",
        ]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Acceso denegado. Se requieren permisos de supervisor o administrador.",
                    }
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated_function


@usuarios_bp.route("/")
@login_required
def usuarios_page():
    """Página principal de usuarios"""
    return render_template("usuarios/usuarios.html", section="personal")


@usuarios_bp.route("/api", methods=["GET"])
@login_required
def obtener_usuarios():
    try:
        filtros = {}
        if "username" in request.args:
            filtros["username"] = request.args["username"]
        if "email" in request.args:
            filtros["email"] = request.args["email"]
        if "rol" in request.args:
            filtros["rol"] = request.args["rol"]
        if "activo" in request.args:
            filtros["activo"] = request.args.get("activo", "").lower() == "true"
        if "nombre" in request.args:
            filtros["nombre"] = request.args["nombre"]
        if "q" in request.args:
            filtros["q"] = request.args["q"]
        if "limit" in request.args:
            filtros["limit"] = request.args["limit"]

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        usuarios, total = listar_usuarios(filtros, page, per_page)
        return jsonify(
            {
                "total": total,
                "page": page,
                "per_page": per_page,
                "usuarios": [
                    {
                        "id": u.id,
                        "username": u.username,
                        "email": u.email,
                        "nombre": u.nombre,
                        "rol": u.rol,
                        "activo": u.activo,
                    }
                    for u in usuarios
                ],
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error al obtener usuarios"}), 500


@usuarios_bp.route("/api/<int:id>", methods=["PUT"])
@admin_required
def actualizar_usuario(id: int):
    try:
        data = request.get_json()
        user = editar_usuario(id, data)
        return jsonify(
            {
                "success": True,
                "message": "Usuario actualizado",
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "rol": user.rol,
                "activo": user.activo,
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


@usuarios_bp.route("/api/<int:id>/rol", methods=["PUT"])
@admin_required
def actualizar_rol_usuario(id: int):
    try:
        data = request.get_json()
        user = cambiar_rol_usuario(id, data["rol"])
        return jsonify(
            {
                "success": True,
                "message": "Rol actualizado",
                "id": user.id,
                "rol": user.rol,
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


@usuarios_bp.route("/api/<int:id>/estado", methods=["PUT"])
@supervisor_or_admin_required
def actualizar_estado_usuario(id: int):
    try:
        data = request.get_json()
        user = cambiar_estado_usuario(id, data["activo"])
        return jsonify(
            {
                "success": True,
                "message": "Estado actualizado",
                "id": user.id,
                "activo": user.activo,
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


@usuarios_bp.route("/api", methods=["POST"])
@admin_required
def registrar_usuario():
    try:
        data = request.get_json()
        user = crear_usuario(data)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Usuario creado exitosamente",
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "rol": user.rol,
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


@usuarios_bp.route("/api/<int:user_id>", methods=["GET"])
@supervisor_or_admin_required
def obtener_usuario(user_id: int):
    """Obtener detalles de un usuario específico"""
    try:
        usuario = obtener_usuario_por_id(user_id)
        return jsonify({"success": True, "usuario": usuario})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404


@usuarios_bp.route("/api/<int:user_id>", methods=["DELETE"])
@admin_required
def eliminar_usuario_route(user_id: int):
    """Eliminar un usuario"""
    try:
        eliminar_usuario(user_id)
        return jsonify({"success": True, "message": "Usuario eliminado exitosamente"})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


@usuarios_bp.route("/api/estadisticas", methods=["GET"])
@supervisor_or_admin_required
def obtener_estadisticas():
    """Obtener estadísticas de usuarios"""
    try:
        stats = obtener_estadisticas_usuarios()
        return jsonify({"success": True, "estadisticas": stats})
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500
