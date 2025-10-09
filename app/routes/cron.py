"""
Endpoints para tareas programadas (cron jobs)
Protegidos con X-Appengine-Cron header
"""

from flask import Blueprint, request, jsonify, current_app
from app.extensions import db, csrf
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.models.usuario import Usuario
from app.models.inventario import Inventario
from datetime import datetime, timezone, timedelta
from sqlalchemy import and_, text
from sqlalchemy.orm import load_only
import logging

logger = logging.getLogger(__name__)

cron_bp = Blueprint("cron", __name__, url_prefix="/api/cron")


def _get_val(obj, name, default=None):
    """Obtiene valor de atributo o clave dict."""
    try:
        return getattr(obj, name)
    except Exception:
        try:
            return obj.get(name, default)
        except Exception:
            return default


def is_valid_cron_request():
    """
    Verifica que la petición viene de Cloud Scheduler/App Engine.

    En App Engine, el sistema añade el header "X-AppEngine-Cron: true" en las
    peticiones de cron. Además, el User-Agent suele comenzar con "AppEngine-Google".

    Algunos entornos/CLI pueden no exponer el header al invocar manualmente el job,
    por lo que permitimos también el User-Agent reconocido de App Engine.
    """
    # En desarrollo, permitir sin header
    if current_app.config.get("FLASK_ENV") == "development":
        return True

    # Headers esperados en producción
    cron_header = request.headers.get("X-AppEngine-Cron")
    cron_header_alt = request.headers.get("X-Appengine-Cron")
    user_agent = request.headers.get("User-Agent", "")

    # Aceptar si el header de cron es "true" (cualquiera de las variantes)
    if (cron_header and cron_header.lower() == "true") or (
        cron_header_alt and cron_header_alt.lower() == "true"
    ):
        return True

    # Como fallback, aceptar User-Agent típico de App Engine y Cloud Scheduler
    if user_agent.startswith("AppEngine-Google") or user_agent.startswith("Google-Cloud-Scheduler"):
        return True

    return False


@cron_bp.route("/generar-ordenes-preventivas", methods=["GET", "POST"])
def generar_ordenes_preventivas():
    """
    Genera órdenes de trabajo para planes de mantenimiento vencidos

    Ejecutado por Cloud Scheduler diariamente a las 00:00 AM

    Returns:
        JSON con resumen de órdenes generadas
    """
    # Verificar que la petición es válida
    if not is_valid_cron_request():
        logger.warning("Intento de acceso no autorizado a endpoint de cron")
        return (
            jsonify(
                {
                    "error": "Acceso no autorizado",
                    "mensaje": "Este endpoint solo puede ser llamado por Cloud Scheduler",
                }
            ),
            403,
        )

    try:
        logger.info("=== INICIO: Generación automática de órdenes preventivas ===")

        # Obtener fecha/hora actual (naive, para compatibilidad con SQLite/SQLAlchemy)
        ahora_utc = datetime.utcnow()

        # Buscar planes activos que necesitan ejecución (próxima_ejecucion <= ahora)
        # En desarrollo/testing no exigimos generacion_automatica para facilitar pruebas
        es_desarrollo = current_app.config.get("FLASK_ENV") in ("development", "testing") or current_app.config.get("ENV") == "development" or current_app.config.get("TESTING")

        columnas_necesarias = (
            PlanMantenimiento.id,
            PlanMantenimiento.estado,
            PlanMantenimiento.proxima_ejecucion,
            PlanMantenimiento.generacion_automatica,
            PlanMantenimiento.activo_id,
            PlanMantenimiento.descripcion,
            PlanMantenimiento.tareas,
            PlanMantenimiento.duracion_estimada,
            PlanMantenimiento.tipo_mantenimiento,
            PlanMantenimiento.frecuencia_dias,
            PlanMantenimiento.intervalo_meses,
            PlanMantenimiento.ultima_ejecucion,
        )

        # Usar with_entities para evitar seleccionar columnas faltantes como responsable_id
        base_query = db.session.query(
            PlanMantenimiento.id,
            PlanMantenimiento.estado,
            PlanMantenimiento.proxima_ejecucion,
            PlanMantenimiento.generacion_automatica,
            PlanMantenimiento.activo_id,
            PlanMantenimiento.descripcion,
            PlanMantenimiento.tareas,
            PlanMantenimiento.duracion_estimada,
            PlanMantenimiento.tipo_mantenimiento,
            PlanMantenimiento.frecuencia_dias,
            PlanMantenimiento.intervalo_meses,
            PlanMantenimiento.ultima_ejecucion,
        )

        if es_desarrollo:
            planes_rows = base_query.filter(
                and_(
                    PlanMantenimiento.estado == "Activo",
                    PlanMantenimiento.proxima_ejecucion <= ahora_utc,
                )
            ).all()
        else:
            planes_rows = base_query.filter(
                and_(
                    PlanMantenimiento.estado == "Activo",
                    PlanMantenimiento.generacion_automatica == True,
                    PlanMantenimiento.proxima_ejecucion <= ahora_utc,
                )
            ).all()

        # Mapear filas a dicts para uso posterior en creación de órdenes
        columnas = [
            "id",
            "estado",
            "proxima_ejecucion",
            "generacion_automatica",
            "activo_id",
            "descripcion",
            "tareas",
            "duracion_estimada",
            "tipo_mantenimiento",
            "frecuencia_dias",
            "intervalo_meses",
            "ultima_ejecucion",
        ]

        planes_vencidos = [
            {col: val for col, val in zip(columnas, row)} for row in planes_rows
        ]

        logger.info(f"Planes vencidos encontrados: {len(planes_vencidos)}")

        ordenes_creadas = []
        errores = []

        for plan in planes_vencidos:
            try:
                # Generar orden de trabajo
                orden = crear_orden_desde_plan(plan)

                if orden:
                    ordenes_creadas.append(
                        {
                            "orden_id": orden.id,
                            "numero_orden": orden.numero_orden,
                            "plan_id": _get_val(plan, "id"),
                            "activo": (Activo.query.get(_get_val(plan, "activo_id")).nombre if _get_val(plan, "activo_id") else "N/A"),
                            "descripcion": orden.descripcion,
                        }
                    )

                    logger.info(
                        f"✅ Orden creada: {orden.numero_orden} para plan {_get_val(plan, 'id')}"
                    )

                    # Enviar notificación (si está configurado)
                    enviar_notificacion_orden_creada(orden, plan)

            except Exception as e:
                plan_id_safe = _get_val(plan, "id")
                error_msg = f"Error procesando plan {plan_id_safe}: {str(e)}"
                logger.error(error_msg)
                errores.append({"plan_id": plan_id_safe, "error": str(e)})

        # Commit de todos los cambios
        db.session.commit()

        # Preparar respuesta
        resumen = {
            "fecha_ejecucion": ahora_utc.isoformat(),
            "planes_revisados": len(planes_vencidos),
            "ordenes_creadas": len(ordenes_creadas),
            "errores": len(errores),
            "detalles": {"ordenes": ordenes_creadas, "errores": errores},
        }

        logger.info(
            f"=== FIN: {len(ordenes_creadas)} órdenes creadas, {len(errores)} errores ==="
        )

        return jsonify(resumen), 200

    except Exception as e:
        logger.exception("Error crítico en generación de órdenes")
        db.session.rollback()
        return (
            jsonify({"error": "Error en generación de órdenes", "mensaje": str(e)}),
            500,
        )


def crear_orden_desde_plan(plan):
    """
    Crea una orden de trabajo a partir de un plan de mantenimiento

    Args:
        plan: PlanMantenimiento instance

    Returns:
        OrdenTrabajo: Nueva orden creada
    """
    # Generar número de orden único
    ultimo_numero = db.session.query(db.func.max(OrdenTrabajo.id)).scalar() or 0
    numero_orden = f"OT-{ultimo_numero + 1:06d}"

    # Crear descripción basada en el plan
    tipo = _get_val(plan, "tipo_mantenimiento") or "Preventivo"
    desc_base = _get_val(plan, "descripcion") or ""
    tareas = _get_val(plan, "tareas") or None
    descripcion = f"Mantenimiento {tipo}: {desc_base}"
    if tareas:
        descripcion += f"\n\nTareas:\n{tareas}"

    # Crear orden
    # Inserción directa por SQL para evitar cargas ORM que puedan tocar PlanMantenimiento
    vals = {
        "numero_orden": numero_orden,
        "tipo": "Mantenimiento Preventivo",
        "prioridad": (_get_val(plan, "prioridad") or "Media"),
        "estado": "Pendiente",
        "descripcion": descripcion,
        "activo_id": _get_val(plan, "activo_id"),
        "tecnico_id": None,
        "tiempo_estimado": _get_val(plan, "duracion_estimada"),
        "fecha_programada": datetime.now(timezone.utc).date(),
        "plan_mantenimiento_id": _get_val(plan, "id"),
        "fecha_creacion": datetime.now(timezone.utc),
    }

    insert_sql = text(
        """
        INSERT INTO orden_trabajo (
            numero_orden, tipo, prioridad, estado, descripcion,
            activo_id, tecnico_id, tiempo_estimado, fecha_programada,
            plan_mantenimiento_id, fecha_creacion
        ) VALUES (
            :numero_orden, :tipo, :prioridad, :estado, :descripcion,
            :activo_id, :tecnico_id, :tiempo_estimado, :fecha_programada,
            :plan_mantenimiento_id, :fecha_creacion
        ) RETURNING id
        """
    )

    nuevo_id = db.session.execute(insert_sql, vals).scalar()
    nueva_orden = OrdenTrabajo.query.get(nuevo_id)

    # Actualizar próxima ejecución del plan
    # Actualizar próxima ejecución del plan (solo si es instancia del modelo)
    try:
        plan.ultima_ejecucion = datetime.now(timezone.utc).date()
    except Exception:
        pass

    # Calcular próxima ejecución según frecuencia
    freq_dias = _get_val(plan, "frecuencia_dias")
    freq_meses = _get_val(plan, "frecuencia_meses") or _get_val(plan, "intervalo_meses")
    try:
        if freq_dias:
            plan.proxima_ejecucion = plan.ultima_ejecucion + timedelta(days=freq_dias)
        elif freq_meses:
            # Aproximación: 1 mes = 30 días
            dias = int(freq_meses) * 30
            plan.proxima_ejecucion = plan.ultima_ejecucion + timedelta(days=dias)
    except Exception:
        pass

    return nueva_orden


def enviar_notificacion_orden_creada(orden, plan):
    """
    Envía notificación por email sobre orden creada

    Args:
        orden: OrdenTrabajo instance
        plan: PlanMantenimiento instance
    """
    try:
        # Verificar si el email está configurado
        if not current_app.config.get("MAIL_SERVER"):
            logger.info("Email no configurado, omitiendo notificación")
            return

        from flask_mail import Message, Mail

        mail = Mail(current_app)

        # Destinatarios
        destinatarios = []

        # Técnico responsable
        if orden.tecnico and orden.tecnico.email:
            destinatarios.append(orden.tecnico.email)

        # Administradores (desde configuración)
        admin_emails = current_app.config.get("ADMIN_EMAILS", "").split(",")
        destinatarios.extend([e.strip() for e in admin_emails if e.strip()])

        if not destinatarios:
            logger.warning("No hay destinatarios configurados para notificación")
            return

        # Crear mensaje
        asunto = f"Nueva Orden Preventiva: {orden.numero_orden}"

        cuerpo = f"""
Se ha generado automáticamente una nueva orden de trabajo preventivo:

ORDEN: {orden.numero_orden}
ACTIVO: {orden.activo.nombre if orden.activo else 'N/A'} ({orden.activo.codigo if orden.activo else 'N/A'})
TIPO: Mantenimiento {_get_val(plan, 'tipo_mantenimiento') or 'Preventivo'}
PRIORIDAD: {orden.prioridad}
TÉCNICO ASIGNADO: {orden.tecnico.nombre if orden.tecnico else 'Sin asignar'}

DESCRIPCIÓN:
{orden.descripcion}

TIEMPO ESTIMADO: {orden.tiempo_estimado} horas
FECHA PROGRAMADA: {orden.fecha_programada.strftime('%d/%m/%Y') if orden.fecha_programada else 'No programada'}

---
Esta orden fue generada automáticamente por el sistema de mantenimiento preventivo.
Accede al sistema para más detalles: {current_app.config.get('SERVER_URL', 'http://localhost:5000')}
"""

        msg = Message(subject=asunto, recipients=destinatarios, body=cuerpo)

        mail.send(msg)
        logger.info(f"Notificación enviada a: {', '.join(destinatarios)}")

    except Exception as e:
        logger.exception("Error enviando notificación")
        # No fallar si el email falla


@cron_bp.route("/verificar-alertas", methods=["GET", "POST"])
def verificar_alertas():
    """
    Verifica activos sin mantenimiento reciente y envía alertas

    Ejecutado por Cloud Scheduler semanalmente
    """
    if not is_valid_cron_request():
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        logger.info("=== INICIO: Verificación de alertas ===")

        # Fecha límite (activos sin mantenimiento en últimos 90 días)
        fecha_limite = datetime.now(timezone.utc).date() - timedelta(days=90)

        # Buscar activos críticos sin órdenes recientes
        from sqlalchemy import or_

        activos_sin_mantenimiento = Activo.query.filter(
            and_(
                Activo.estado.in_(["Operativo", "En Mantenimiento"]),
                or_(
                    Activo.ultimo_mantenimiento == None,
                    Activo.ultimo_mantenimiento < fecha_limite,
                ),
            )
        ).all()

        alertas_enviadas = []

        for activo in activos_sin_mantenimiento:
            # Enviar alerta
            enviar_alerta_mantenimiento(activo)
            alertas_enviadas.append(
                {
                    "activo_id": activo.id,
                    "codigo": activo.codigo,
                    "nombre": activo.nombre,
                    "ultimo_mantenimiento": (
                        activo.ultimo_mantenimiento.isoformat()
                        if activo.ultimo_mantenimiento
                        else None
                    ),
                }
            )

        logger.info(f"=== FIN: {len(alertas_enviadas)} alertas enviadas ===")

        return (
            jsonify(
                {
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "activos_revisados": Activo.query.count(),
                    "alertas_enviadas": len(alertas_enviadas),
                    "detalles": alertas_enviadas,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error en verificación de alertas")
        return jsonify({"error": str(e)}), 500


def enviar_alerta_mantenimiento(activo):
    """Envía alerta sobre activo que requiere mantenimiento"""
    try:
        if not current_app.config.get("MAIL_SERVER"):
            return

        from flask_mail import Message, Mail

        mail = Mail(current_app)

        admin_emails = current_app.config.get("ADMIN_EMAILS", "").split(",")
        destinatarios = [e.strip() for e in admin_emails if e.strip()]

        if not destinatarios:
            return

        msg = Message(
            subject=f"⚠️ Alerta: {activo.nombre} requiere mantenimiento",
            recipients=destinatarios,
            body=f"""
ALERTA DE MANTENIMIENTO

ACTIVO: {activo.nombre} ({activo.codigo})
UBICACIÓN: {activo.ubicacion or 'No especificada'}
ÚLTIMO MANTENIMIENTO: {activo.ultimo_mantenimiento.strftime('%d/%m/%Y') if activo.ultimo_mantenimiento else 'Nunca'}

Este activo lleva más de 90 días sin mantenimiento registrado.
Se recomienda programar una inspección o mantenimiento preventivo.

Accede al sistema: {current_app.config.get('SERVER_URL', 'http://localhost:5000')}
""",
        )

        mail.send(msg)
        logger.info(f"Alerta enviada para activo {activo.codigo}")

    except Exception as e:
        logger.exception(f"Error enviando alerta para activo {activo.id}")


@cron_bp.route("/crear-articulos-demo", methods=["GET", "POST"])
def crear_articulos_demo():
    """Crea artículos de inventario de demostración si no existen.

    Protegido por verificación de cron para permitir ejecuciones desde Cloud Scheduler
    o invocaciones manuales con el header correspondiente.
    """
    # Permitir invocación manual con token seguro opcional (solo para este endpoint)
    token = request.args.get("token")
    token_conf = current_app.config.get("CRON_SEED_TOKEN", "seed-demo")
    if token_conf and token == token_conf:
        pass  # token válido, continuar
    elif not is_valid_cron_request():
        logger.warning(
            "Intento de acceso no autorizado a endpoint de cron (crear_articulos_demo)"
        )
        return (
            jsonify(
                {
                    "error": "Acceso no autorizado",
                    "mensaje": "Este endpoint solo puede ser llamado por Cloud Scheduler",
                }
            ),
            403,
        )

    try:
        # Definir artículos de demo
        dataset = [
            {
                "codigo": "ART-001",
                "nombre": "Tornillo M8",
                "descripcion": "Tornillo métrico M8",
                "categoria": "Tornillería",
                "ubicacion": "Almacén A",
                "cantidad": 150,
                "cantidad_minima": 20,
                "unidad": "Unidad",
                "stock_actual": 150,
                "stock_minimo": 20,
                "unidad_medida": "UNI",
                "precio_promedio": 0.15,
                "proveedor_principal": "Proveedor Demo",
            },
            {
                "codigo": "ART-002",
                "nombre": "Arandela 8mm",
                "descripcion": "Arandela para tornillo 8mm",
                "categoria": "Tornillería",
                "ubicacion": "Almacén A",
                "cantidad": 300,
                "cantidad_minima": 50,
                "unidad": "Unidad",
                "stock_actual": 300,
                "stock_minimo": 50,
                "unidad_medida": "UNI",
                "precio_promedio": 0.05,
                "proveedor_principal": "Proveedor Demo",
            },
            {
                "codigo": "ART-003",
                "nombre": "Lubricante 1L",
                "descripcion": "Lubricante universal 1 litro",
                "categoria": "Consumibles",
                "ubicacion": "Almacén B",
                "cantidad": 25,
                "cantidad_minima": 5,
                "unidad": "Litro",
                "stock_actual": 25,
                "stock_minimo": 5,
                "unidad_medida": "LT",
                "precio_promedio": 9.90,
                "proveedor_principal": "Proveedor Demo",
            },
        ]

        # Consultar existentes por código
        codigos = [d["codigo"] for d in dataset]
        # Intentar consultar existentes; si la tabla no existe, crearla y continuar
        try:
            existentes = {
                inv.codigo
                for inv in Inventario.query.filter(Inventario.codigo.in_(codigos)).all()
            }
        except Exception as e:
            logger.warning(f"Tabla inventario inexistente o error consultando existentes: {e}")
            try:
                # Crear la tabla de inventario si no existe
                Inventario.__table__.create(db.engine, checkfirst=True)
                existentes = set()
            except Exception as ce:
                logger.exception("No se pudo crear la tabla inventario")
                raise ce

        creados = []
        for d in dataset:
            if d["codigo"] in existentes:
                continue

            art = Inventario(
                codigo=d["codigo"],
                nombre=d.get("nombre"),
                descripcion=d.get("descripcion"),
                categoria=d.get("categoria"),
                ubicacion=d.get("ubicacion"),
                cantidad=d.get("cantidad"),
                cantidad_minima=d.get("cantidad_minima"),
                unidad=d.get("unidad"),
                stock_actual=d.get("stock_actual"),
                stock_minimo=d.get("stock_minimo"),
                unidad_medida=d.get("unidad_medida"),
                precio_promedio=d.get("precio_promedio"),
                proveedor_principal=d.get("proveedor_principal"),
            )
            # Asegurar visibilidad en listados: activo=True
            try:
                art.activo = True
            except Exception:
                # Si el atributo no está mapeado por algún motivo, continuar
                pass

            db.session.add(art)
            creados.append({"codigo": d["codigo"], "nombre": d.get("nombre")})

        # Intentar commit por ORM; si falla, usar inserción SQL mínima segura
        try:
            # Activar también artículos existentes por código, para garantizar visibilidad
            try:
                db.session.query(Inventario).filter(Inventario.codigo.in_(codigos)).update({"activo": True}, synchronize_session=False)
            except Exception as upd_err:
                logger.warning(f"No se pudo activar artículos demo por ORM: {upd_err}")

            db.session.commit()
            logger.info(f"Artículos demo creados (ORM): {len(creados)}")
            return (
                jsonify({"success": True, "total_creados": len(creados), "creados": creados}),
                200,
            )
        except Exception as orm_err:
            logger.warning(f"Fallo commit ORM al crear artículos demo: {orm_err}. Intentando SQL directo mínimo.")
            db.session.rollback()
            insert_sql = text(
                "INSERT INTO inventario (codigo, descripcion, activo) VALUES (:codigo, :descripcion, :activo)"
            )
            insertados = 0
            for d in dataset:
                try:
                    db.session.execute(insert_sql, {"codigo": d["codigo"], "descripcion": d.get("descripcion"), "activo": True})
                    insertados += 1
                except Exception as se:
                    # Ignorar errores por duplicados u otros puntuales, seguir con el resto
                    logger.warning(f"Error insertando artículo {d['codigo']} por SQL: {se}")
                    continue
            try:
                db.session.commit()
                # Asegurar activación por si ya existían con activo NULL/FALSE
                update_sql = text("UPDATE inventario SET activo = TRUE WHERE codigo = :codigo")
                for d in dataset:
                    try:
                        db.session.execute(update_sql, {"codigo": d["codigo"]})
                    except Exception as ue:
                        logger.warning(f"Error activando artículo {d['codigo']}: {ue}")
                db.session.commit()
                logger.info(f"Artículos demo creados (SQL): {insertados}")
                return (
                    jsonify({"success": True, "total_creados": insertados}),
                    200,
                )
            except Exception as sql_err:
                db.session.rollback()
                logger.exception(f"Error commit por SQL directo mínimo: {sql_err}")
                return jsonify({"success": False, "error": str(sql_err)}), 500
    except Exception as e:
        db.session.rollback()
        logger.exception("Error creando artículos demo")
        return jsonify({"success": False, "error": str(e)}), 500


@cron_bp.route("/test", methods=["GET"])
def test_cron():
    """
    Endpoint de prueba para verificar que el cron funciona
    Solo en desarrollo
    """
    if current_app.config.get("FLASK_ENV") != "development":
        return jsonify({"error": "Solo disponible en desarrollo"}), 403

    return (
        jsonify(
            {
                "mensaje": "Endpoint de cron funcionando",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cron_header": request.headers.get("X-Appengine-Cron", "No presente"),
            }
        ),
        200,
    )


@cron_bp.route("/db-fix", methods=["GET", "POST"])
def aplicar_parches_db():
    """
    Parche de base de datos para agregar columnas faltantes en producción.

    Protegido por verificación de cron. Ejecuta ALTER TABLE con IF NOT EXISTS
    para las tablas plan_mantenimiento y activo.
    """
    if not is_valid_cron_request():
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        logger.info("=== INICIO: Parche DB (agregar columnas faltantes) ===")

        # Forzar el esquema público para evitar desalineaciones de search_path
        try:
            db.session.execute(text("SET search_path TO public"))
        except Exception as e:
            logger.exception("No se pudo fijar search_path a public")

        comandos = [
            # plan_mantenimiento
            "ALTER TABLE plan_mantenimiento ADD COLUMN IF NOT EXISTS tipo_mantenimiento VARCHAR(50);",
            "ALTER TABLE plan_mantenimiento ADD COLUMN IF NOT EXISTS tareas TEXT;",
            "ALTER TABLE plan_mantenimiento ADD COLUMN IF NOT EXISTS duracion_estimada DOUBLE PRECISION;",
            "ALTER TABLE public.plan_mantenimiento ADD COLUMN IF NOT EXISTS responsable_id INTEGER;",
            "CREATE INDEX IF NOT EXISTS idx_plan_mantenimiento_responsable_id ON public.plan_mantenimiento (responsable_id);",
            # Ajuste de longitud de dias_semana
            "DO $$\nBEGIN\n    IF EXISTS (\n        SELECT 1 FROM information_schema.columns\n        WHERE table_name = 'plan_mantenimiento' AND column_name = 'dias_semana'\n    ) THEN\n        BEGIN\n            ALTER TABLE plan_mantenimiento ALTER COLUMN dias_semana TYPE VARCHAR(200);\n        EXCEPTION WHEN others THEN\n            NULL;\n        END;\n    END IF;\nEND $$;",
            # activo
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS tipo VARCHAR(50);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS marca VARCHAR(100);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS ubicacion VARCHAR(100);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS estado VARCHAR(50);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS prioridad VARCHAR(20);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS fecha_adquisicion TIMESTAMP;",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS ultimo_mantenimiento TIMESTAMP;",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS proximo_mantenimiento TIMESTAMP;",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS descripcion TEXT;",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS modelo VARCHAR(100);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS numero_serie VARCHAR(100);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS fabricante VARCHAR(100);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS proveedor VARCHAR(100);",
            "ALTER TABLE activo ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;",
            # inventario
            "ALTER TABLE public.inventario ADD COLUMN IF NOT EXISTS nombre VARCHAR(100);",
        ]

        ejecutados = []
        errores = []

        for cmd in comandos:
            try:
                db.session.execute(text(cmd))
                ejecutados.append(cmd.split(" ")[2])  # Nombre de tabla
            except Exception as e:
                logger.exception(f"Error ejecutando comando: {cmd}")
                errores.append({"cmd": cmd, "error": str(e)})

        db.session.commit()

        # Verificación explícita de columnas críticas y contexto de BD/esquema
        verificaciones = {}
        try:
            db_info = db.session.execute(text("SELECT current_database(), current_schema()"))
            db_name, db_schema = db_info.fetchone()
            verificaciones["current_database"] = db_name
            verificaciones["current_schema"] = db_schema

            existe_responsable = db.session.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'plan_mantenimiento' AND column_name = 'responsable_id')"
                )
            ).scalar()
            verificaciones["plan_mantenimiento.responsable_id"] = bool(existe_responsable)

            existe_tipo_mant = db.session.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'plan_mantenimiento' AND column_name = 'tipo_mantenimiento')"
                )
            ).scalar()
            verificaciones["plan_mantenimiento.tipo_mantenimiento"] = bool(existe_tipo_mant)

            existe_marca = db.session.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'activo' AND column_name = 'marca')"
                )
            ).scalar()
            verificaciones["activo.marca"] = bool(existe_marca)

            # Verificar columna faltante en inventario
            existe_nombre_inv = db.session.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'inventario' AND column_name = 'nombre')"
                )
            ).scalar()
            verificaciones["inventario.nombre"] = bool(existe_nombre_inv)

            logger.info(f"VERIFICACION columnas y contexto: {verificaciones}")
        except Exception as e:
            logger.exception("Error verificando columnas tras parche DB")
            verificaciones["error_verificacion"] = str(e)

        # Preparar al menos un plan candidato para pruebas automáticas (opcional y seguro)
        plan_candidato_id = None
        try:
            plan_candidato_id = db.session.execute(
                text(
                    "SELECT id FROM public.plan_mantenimiento WHERE estado='Activo' ORDER BY id LIMIT 1"
                )
            ).scalar()

            if plan_candidato_id:
                db.session.execute(
                    text(
                        "UPDATE public.plan_mantenimiento SET proxima_ejecucion = NOW() - INTERVAL '1 day', generacion_automatica = TRUE WHERE id = :pid"
                    ),
                    {"pid": plan_candidato_id},
                )
                db.session.commit()
                logger.info(
                    f"PLAN CANDIDATO preparado: id={plan_candidato_id} (proxima_ejecucion = ayer, generacion_automatica = TRUE)"
                )
            else:
                logger.info("No se encontró plan activo para preparar como candidato")
                # Si no hay ningún plan, crear uno de prueba automáticamente
                total_planes = db.session.execute(
                    text("SELECT COUNT(*) FROM public.plan_mantenimiento")
                ).scalar()
                if not total_planes:
                    logger.info("Creando plan de mantenimiento de prueba para validación")
                    # Intentar asociar un activo existente si lo hay
                    activo_prueba_id = db.session.execute(
                        text("SELECT id FROM public.activo ORDER BY id LIMIT 1")
                    ).scalar()

                    insert_plan_sql = text(
                        """
                        INSERT INTO public.plan_mantenimiento (
                            codigo_plan, nombre, descripcion, estado,
                            generacion_automatica, proxima_ejecucion,
                            tipo_mantenimiento, duracion_estimada, activo_id
                        ) VALUES (
                            'PM-AUTO-TEST', 'Plan Auto Test', 'Plan generado para validación automática', 'Activo',
                            TRUE, NOW() - INTERVAL '1 day',
                            'Preventivo', 2.0, :activo_id
                        ) RETURNING id
                        """
                    )
                    nuevo_plan_id = db.session.execute(
                        insert_plan_sql, {"activo_id": activo_prueba_id}
                    ).scalar()
                    db.session.commit()
                    plan_candidato_id = nuevo_plan_id
                    logger.info(
                        f"PLAN DE PRUEBA creado: id={nuevo_plan_id} (PM-AUTO-TEST)"
                    )
        except Exception as e:
            logger.exception("Error preparando plan candidato tras parche DB")

        logger.info(
            f"=== FIN: Parche DB aplicado. Comandos ejecutados: {len(ejecutados)}, errores: {len(errores)} ==="
        )

        return (
            jsonify(
                {
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "comandos_ejecutados": len(ejecutados),
                    "errores": errores,
                    "verificacion": verificaciones,
                    "plan_candidato_preparado": plan_candidato_id,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logger.exception("Error crítico aplicando parche DB")
        return jsonify({"error": str(e)}), 500


@cron_bp.route("/eliminar-plan-auto-test", methods=["GET", "POST"])
@csrf.exempt
def eliminar_plan_auto_test():
    """
    Elimina el plan auto test problemático que está generando órdenes continuamente
    
    Returns:
        JSON con resumen de la eliminación
    """
    # Verificar que la petición es válida
    if not is_valid_cron_request():
        logger.warning("Intento de acceso no autorizado a endpoint de eliminación")
        return (
            jsonify(
                {
                    "error": "Acceso no autorizado",
                    "mensaje": "Este endpoint solo puede ser llamado por Cloud Scheduler",
                }
            ),
            403,
        )

    try:
        logger.info("=== INICIO: Eliminación de plan auto test problemático ===")
        
        # Buscar planes auto test problemáticos
        planes_auto_test = PlanMantenimiento.query.filter(
            (PlanMantenimiento.codigo_plan == 'PM-AUTO-TEST') |
            (PlanMantenimiento.nombre.ilike('%auto%test%')) |
            (PlanMantenimiento.codigo_plan.ilike('%auto%test%'))
        ).all()
        
        logger.info(f"Planes auto test encontrados: {len(planes_auto_test)}")
        
        planes_eliminados = []
        errores = []
        
        for plan in planes_auto_test:
            try:
                logger.info(f"Procesando plan: {plan.codigo_plan} (ID: {plan.id})")
                
                # Contar órdenes relacionadas
                ordenes_relacionadas = OrdenTrabajo.query.filter(
                    OrdenTrabajo.descripcion.ilike(f'%{plan.codigo_plan}%')
                ).count()
                
                logger.info(f"Órdenes relacionadas encontradas: {ordenes_relacionadas}")
                
                # Información del plan antes de eliminar
                plan_info = {
                    "id": plan.id,
                    "codigo_plan": plan.codigo_plan,
                    "nombre": plan.nombre,
                    "estado": plan.estado,
                    "generacion_automatica": plan.generacion_automatica,
                    "ordenes_relacionadas": ordenes_relacionadas
                }
                
                # Eliminar el plan
                db.session.delete(plan)
                planes_eliminados.append(plan_info)
                
                logger.info(f"✅ Plan {plan.codigo_plan} eliminado exitosamente")
                
            except Exception as e:
                error_msg = f"Error eliminando plan {plan.codigo_plan}: {str(e)}"
                logger.error(error_msg)
                errores.append({"plan_id": plan.id, "codigo_plan": plan.codigo_plan, "error": str(e)})
        
        # Confirmar cambios
        db.session.commit()
        
        logger.info(f"=== FIN: Eliminación completada. {len(planes_eliminados)} planes eliminados ===")
        
        return (
            jsonify(
                {
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "planes_eliminados": len(planes_eliminados),
                    "detalles_planes": planes_eliminados,
                    "errores": errores,
                    "mensaje": f"Se eliminaron {len(planes_eliminados)} planes auto test problemáticos"
                }
            ),
            200,
        )
        
    except Exception as e:
        db.session.rollback()
        logger.exception("Error crítico eliminando planes auto test")
        return jsonify({"error": str(e)}), 500
