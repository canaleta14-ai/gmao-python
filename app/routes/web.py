from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, logout_user
from app.controllers.usuarios_controller import autenticar_usuario
from app.models.orden_trabajo import (
    OrdenTrabajo,
)  # Ensure this model is defined correctly and properly initialized
from app.extensions import db  # Importar db correctamente desde extensions
from app.models.activo import Activo
from app.models.inventario import Inventario

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("web.login"))


@web_bp.route("/dashboard")
@login_required
def dashboard():
    from datetime import date
    from sqlalchemy import func
    from app.models.orden_trabajo import OrdenTrabajo

    hoy = date.today()
    stats: dict[str, int] = {
        "ordenes_activas": OrdenTrabajo.query.filter_by(estado="En Proceso").count(),
        "ordenes_completadas_hoy": OrdenTrabajo.query.filter(
            OrdenTrabajo.estado == "Completada",
            func.date(OrdenTrabajo.fecha_completada) == hoy,
        ).count(),
        "ordenes_pendientes": OrdenTrabajo.query.filter_by(estado="Pendiente").count(),
        "total_activos": Activo.query.count(),
        "activos_operativos": Activo.query.filter_by(estado="Operativo").count(),
        "activos_mantenimiento": Activo.query.filter_by(
            estado="En Mantenimiento"
        ).count(),
        "inventario_bajo": Inventario.query.filter(
            Inventario.stock_actual <= Inventario.stock_minimo
        ).count(),
    }

    ordenes_recientes = (
        OrdenTrabajo.query.order_by(OrdenTrabajo.fecha_creacion.desc()).limit(10).all()
    )
    return render_template(
        "dashboard/dashboard.html", stats=stats, ordenes_recientes=ordenes_recientes
    )


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        username = data.get("username")
        password = data.get("password")
        user = autenticar_usuario(username, password)
        if user:
            if request.is_json:
                return jsonify({"success": True, "message": "Login exitoso"})
            flash("Login exitoso", "success")
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


@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.login"))
