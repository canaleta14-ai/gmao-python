from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db
from datetime import datetime

actualizar_fecha_bp = Blueprint("actualizar_fecha", __name__, url_prefix="/api")


@actualizar_fecha_bp.route("/planes/<int:plan_id>/actualizar-fecha", methods=["POST"])
@login_required
def actualizar_fecha_plan(plan_id):
    """
    Actualiza solo la fecha de próxima ejecución de un plan
    Sin recalcular ni validar otras condiciones
    """
    try:
        data = request.get_json()
        nueva_fecha_str = data.get("proxima_ejecucion")

        if not nueva_fecha_str:
            return jsonify({"success": False, "error": "Falta proxima_ejecucion"}), 400

        # Obtener el plan
        plan = PlanMantenimiento.query.get_or_404(plan_id)

        # Convertir la fecha string a datetime
        try:
            # Intentar parsear como fecha completa ISO
            nueva_fecha = datetime.fromisoformat(nueva_fecha_str.replace("Z", "+00:00"))
        except:
            try:
                # Intentar parsear como solo fecha YYYY-MM-DD
                nueva_fecha = datetime.strptime(nueva_fecha_str, "%Y-%m-%d")
            except:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Formato de fecha inválido: {nueva_fecha_str}",
                        }
                    ),
                    400,
                )

        # Guardar fecha anterior para log
        fecha_anterior = plan.proxima_ejecucion

        # Actualizar la fecha
        plan.proxima_ejecucion = nueva_fecha

        # Guardar en la base de datos
        db.session.commit()

        print(
            f"✅ Plan {plan.codigo_plan}: Fecha actualizada de {fecha_anterior} a {nueva_fecha}"
        )

        return jsonify(
            {
                "success": True,
                "message": f"Fecha del plan {plan.codigo_plan} actualizada correctamente",
                "plan": {
                    "id": plan.id,
                    "codigo": plan.codigo_plan,
                    "fecha_anterior": (
                        fecha_anterior.isoformat() if fecha_anterior else None
                    ),
                    "fecha_nueva": nueva_fecha.isoformat(),
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error actualizando fecha: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
