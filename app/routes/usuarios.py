from flask import Blueprint, request, jsonify, render_template
from app.controllers.usuarios_controller import (
    crear_usuario,  # type: ignore
    listar_usuarios,  # type: ignore
    editar_usuario,  # type: ignore
    cambiar_rol_usuario,  # type: ignore
    cambiar_estado_usuario,  # type: ignore
)

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/")
def usuarios_page():
    """Página principal de usuarios"""
    return render_template("usuarios/usuarios.html", section="personal")


@usuarios_bp.route("/api", methods=["GET"])
def obtener_usuarios():
    filtros = {}
    if "username" in request.args:
        filtros["username"] = request.args["username"]
    if "email" in request.args:
        filtros["email"] = request.args["email"]
    if "rol" in request.args:
        filtros["rol"] = request.args["rol"]
    if "activo" in request.args:
        filtros["activo"] = request.args.get("activo", "").lower() == "true"
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


@usuarios_bp.route("/api/<int:id>", methods=["PUT"])
def actualizar_usuario(id: int):
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


@usuarios_bp.route("/api/<int:id>/rol", methods=["PUT"])
def actualizar_rol_usuario(id: int):
    data = request.get_json()
    user = cambiar_rol_usuario(id, data["rol"])
    return jsonify(
        {"success": True, "message": "Rol actualizado", "id": user.id, "rol": user.rol}
    )


@usuarios_bp.route("/api/<int:id>/estado", methods=["PUT"])
def actualizar_estado_usuario(id: int):
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


@usuarios_bp.route("/api", methods=["POST"])
def registrar_usuario():
    data = request.get_json()
    user = crear_usuario(data)
    return jsonify(
        {
            "success": True,
            "message": "Usuario creado exitosamente",
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol,
        }
    )
