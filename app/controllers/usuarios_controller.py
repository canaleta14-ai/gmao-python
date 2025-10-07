from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user
from app.models.usuario import Usuario
from app.extensions import db, limiter, csrf

usuarios_controller = Blueprint("usuarios_controller", __name__)


def autenticar_usuario(username, password):
    """
    Función de autenticación de usuarios
    Retorna el objeto usuario si las credenciales son válidas, None en caso contrario
    """
    try:
        user = Usuario.query.filter_by(username=username).first()
        if user and user.activo and user.check_password(password):
            return user
        return None
    except Exception as e:
        print(f"Error en autenticación: {e}")
        return None


@usuarios_controller.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Máximo 10 intentos por minuto por IP
@csrf.exempt  # Eximir CSRF para el endpoint de login
def login():
    """
    Ruta de login - maneja tanto GET (mostrar formulario) como POST (procesar login)
    Protegido con rate limiting: 10 intentos por minuto
    """
    if current_user.is_authenticated:
        # Si ya está autenticado, responder en el formato adecuado
        if request.is_json:
            return jsonify({"success": True, "message": "Ya autenticado"}), 200
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        # Aceptar JSON o form y ser tolerante si get_json devuelve None
        data = request.get_json(silent=True) or request.form or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            if request.is_json:
                return (
                    jsonify(
                        {"success": False, "message": "Usuario y contraseña requeridos"}
                    ),
                    400,
                )
            flash("Usuario y contraseña requeridos", "warning")
            return render_template("web/login.html", no_sidebar=True, login_bg=True)

        user = autenticar_usuario(username, password)
        if user:
            login_user(
                user, remember=False
            )  # remember=False para cerrar sesión al cerrar navegador
            if request.is_json:
                return jsonify({"success": True, "message": "Login exitoso"})
            flash("Login exitoso", "success")
            # Redirigir a la página solicitada originalmente o al dashboard
            next_page = request.args.get("next")
            if next_page and next_page.startswith(
                "/"
            ):  # Solo redirigir a rutas locales
                return redirect(next_page)
            return redirect(url_for("web.dashboard"))
        else:
            if request.is_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Usuario o contraseña incorrectos",
                        }
                    ),
                    401,
                )
            flash("Usuario o contraseña incorrectos", "danger")
            return render_template("web/login.html", no_sidebar=True, login_bg=True)

    return render_template("web/login.html", no_sidebar=True, login_bg=True)


@usuarios_controller.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """
    Ruta de logout - cierra la sesión del usuario actual
    """
    logout_user()
    flash("Sesión cerrada exitosamente", "info")
    return redirect(url_for("usuarios_controller.login"))


@usuarios_controller.route("/api/user/info")
@login_required
def get_user_info():
    """
    API endpoint para obtener información del usuario actual
    """
    if current_user.is_authenticated:
        return jsonify(
            {
                "success": True,
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "email": current_user.email,
                    "nombre": current_user.nombre,
                    "rol": current_user.rol,
                    "activo": current_user.activo,
                },
            }
        )
    return jsonify({"success": False, "message": "Usuario no autenticado"}), 401


@usuarios_controller.route("/api/user/change-password", methods=["POST"])
@login_required
def change_password():
    """
    API endpoint para cambiar la contraseña del usuario actual
    """
    try:
        data = request.get_json()
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not all([current_password, new_password, confirm_password]):
            return (
                jsonify(
                    {"success": False, "message": "Todos los campos son requeridos"}
                ),
                400,
            )

        if new_password != confirm_password:
            return (
                jsonify(
                    {"success": False, "message": "Las contraseñas nuevas no coinciden"}
                ),
                400,
            )

        if not current_user.check_password(current_password):
            return (
                jsonify({"success": False, "message": "Contraseña actual incorrecta"}),
                400,
            )

        current_user.set_password(new_password)
        db.session.commit()

        return jsonify({"success": True, "message": "Contraseña cambiada exitosamente"})

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {"success": False, "message": f"Error al cambiar contraseña: {str(e)}"}
            ),
            500,
        )
