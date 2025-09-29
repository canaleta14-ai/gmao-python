from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db
from datetime import datetime, timedelta
from flask import request
from sqlalchemy import func
import calendar


def calcular_proxima_ejecucion(data, fecha_base=None):
    """
    Calcula la próxima ejecución basada en la configuración de frecuencia
    """
    if fecha_base is None:
        fecha_base = datetime.now()

    tipo_frecuencia = data.get("tipo_frecuencia", "mensual")

    if tipo_frecuencia == "mensual":
        tipo_mensual = data.get("tipo_mensual", "dia_semana_mes")
        intervalo_meses = int(data.get("intervalo_meses", 1))

        if tipo_mensual == "dia_mes":
            # Día específico del mes (ej: día 15 de cada mes)
            dia_mes = int(data.get("dia_mes", 1))

            # Calcular el próximo mes
            fecha_objetivo = fecha_base.replace(day=1) + timedelta(days=32)
            fecha_objetivo = fecha_objetivo.replace(day=1)  # Primer día del próximo mes

            # Ajustar el día específico
            ultimo_dia_mes = calendar.monthrange(
                fecha_objetivo.year, fecha_objetivo.month
            )[1]
            dia_final = min(dia_mes, ultimo_dia_mes)

            proxima_ejecucion = fecha_objetivo.replace(day=dia_final)

        elif tipo_mensual == "dia_semana_mes":
            # Día específico de una semana específica (ej: primer sábado de cada mes)
            semana_mes = int(data.get("semana_mes", 1))  # 1-4
            dia_semana_mes = data.get("dia_semana_mes", "sabado")

            # Mapeo de días de la semana - soporta tanto nombres como números
            dias_semana_map = {
                "lunes": 0,
                "1": 0,
                "martes": 1,
                "2": 1,
                "miercoles": 2,
                "3": 2,
                "jueves": 3,
                "4": 3,
                "viernes": 4,
                "5": 4,
                "sabado": 5,
                "6": 5,
                "domingo": 6,
                "0": 6,
            }

            dia_semana_num = dias_semana_map.get(
                dia_semana_mes.lower(), 5
            )  # Default: sábado

            # Intentar calcular para el mes actual primero
            año_objetivo = fecha_base.year
            mes_objetivo = fecha_base.month

            # Encontrar el primer día del mes objetivo
            primer_dia_mes = datetime(año_objetivo, mes_objetivo, 1)

            # Encontrar el primer día de la semana deseada en ese mes
            dias_hasta_target = (dia_semana_num - primer_dia_mes.weekday()) % 7
            primera_ocurrencia = primer_dia_mes + timedelta(days=dias_hasta_target)

            # Calcular la semana específica (1-4)
            semanas_adicionales = (semana_mes - 1) * 7
            proxima_ejecucion = primera_ocurrencia + timedelta(days=semanas_adicionales)

            # Verificar que la fecha esté dentro del mes y sea futura
            if (
                proxima_ejecucion.month != mes_objetivo
                or proxima_ejecucion.date() <= fecha_base.date()
            ):
                # Si nos pasamos del mes o la fecha ya pasó, calcular para el próximo mes
                if mes_objetivo == 12:
                    año_objetivo = fecha_base.year + 1
                    mes_objetivo = 1
                else:
                    año_objetivo = fecha_base.year
                    mes_objetivo = fecha_base.month + intervalo_meses

                # Recalcular para el próximo mes
                primer_dia_mes = datetime(año_objetivo, mes_objetivo, 1)
                dias_hasta_target = (dia_semana_num - primer_dia_mes.weekday()) % 7
                primera_ocurrencia = primer_dia_mes + timedelta(days=dias_hasta_target)
                semanas_adicionales = (semana_mes - 1) * 7
                proxima_ejecucion = primera_ocurrencia + timedelta(
                    days=semanas_adicionales
                )

                # Verificar que la fecha esté dentro del mes
                if proxima_ejecucion.month != mes_objetivo:
                    # Si nos pasamos del mes, usar la última ocurrencia válida
                    proxima_ejecucion = primera_ocurrencia + timedelta(
                        days=(semana_mes - 2) * 7
                    )
                    if proxima_ejecucion.month != mes_objetivo:
                        proxima_ejecucion = primera_ocurrencia

    elif tipo_frecuencia == "semanal":
        # Lógica para frecuencia semanal con días específicos
        intervalo_semanas = int(data.get("intervalo_semanas", 1))
        dias_semana = data.get("dias_semana", [])

        if not dias_semana:
            # Si no hay días específicos, usar la lógica simple de sumar semanas
            proxima_ejecucion = fecha_base + timedelta(weeks=intervalo_semanas)
        else:
            # Mapeo de días de la semana (el frontend envía nombres en español)
            dias_semana_map = {
                "lunes": 0,
                "martes": 1,
                "miercoles": 2,
                "jueves": 3,
                "viernes": 4,
                "sabado": 5,
                "domingo": 6,
            }

            # Convertir nombres a números
            dias_numericos = []
            for dia in dias_semana:
                if isinstance(dia, str):
                    dia_num = dias_semana_map.get(dia.lower())
                    if dia_num is not None:
                        dias_numericos.append(dia_num)

            if not dias_numericos:
                # Fallback si no se pueden convertir los días
                proxima_ejecucion = fecha_base + timedelta(weeks=intervalo_semanas)
            else:
                # Encontrar el próximo día de la semana especificado
                dia_actual = fecha_base.weekday()
                print(
                    f"DEBUG semanal - dia_actual: {dia_actual}, fecha_base: {fecha_base}"
                )
                print(f"DEBUG semanal - dias_numericos: {dias_numericos}")

                # Buscar el próximo día válido
                proxima_ejecucion = None

                # 1. Buscar en esta semana (solo días futuros)
                for dia_objetivo in dias_numericos:
                    if dia_objetivo > dia_actual:
                        dias_hasta = dia_objetivo - dia_actual
                        proxima_ejecucion = fecha_base + timedelta(days=dias_hasta)
                        print(
                            f"DEBUG semanal - ESTA SEMANA: día {dia_objetivo}, en {dias_hasta} días"
                        )
                        break

                # 2. Si no se encontró en esta semana, ir a próxima semana
                if proxima_ejecucion is None:
                    primer_dia = min(dias_numericos)
                    # Días hasta lunes de próxima semana + días desde lunes hasta día objetivo
                    dias_hasta_lunes_siguiente = 7 - dia_actual
                    dias_total = dias_hasta_lunes_siguiente + primer_dia
                    proxima_ejecucion = fecha_base + timedelta(days=dias_total)
                    print(
                        f"DEBUG semanal - PRÓXIMA SEMANA: día {primer_dia}, en {dias_total} días"
                    )

                print(
                    f"DEBUG semanal - RESULTADO: {proxima_ejecucion.strftime('%Y-%m-%d %A')}"
                )

                # Si se especificó intervalo de semanas > 1, ajustar
                if intervalo_semanas > 1:
                    semanas_adicionales = (intervalo_semanas - 1) * 7
                    proxima_ejecucion = proxima_ejecucion + timedelta(
                        days=semanas_adicionales
                    )

                # IMPORTANTE: Limpiar la hora para que sea medianoche del día calculado
                proxima_ejecucion = proxima_ejecucion.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )

    elif tipo_frecuencia == "diaria":
        # Lógica para frecuencia diaria
        proxima_ejecucion = fecha_base + timedelta(days=1)

    else:
        # Fallback a lógica simple
        frecuencias_dias = {
            "Diario": 1,
            "Semanal": 7,
            "Quincenal": 15,
            "Mensual": 30,
            "Trimestral": 90,
            "Anual": 365,
        }
        dias = frecuencias_dias.get(data.get("frecuencia", "Mensual"), 30)
        proxima_ejecucion = fecha_base + timedelta(days=dias)

    return proxima_ejecucion


def generar_codigo_plan():
    """Generar código único para plan de mantenimiento en formato PM-YYYY-NNNN"""
    año_actual = datetime.now().year
    prefijo = f"PM-{año_actual}-"

    # Buscar el último código del año actual
    ultimo_plan = (
        PlanMantenimiento.query.filter(
            PlanMantenimiento.codigo_plan.like(f"{prefijo}%")
        )
        .order_by(PlanMantenimiento.codigo_plan.desc())
        .first()
    )

    if ultimo_plan:
        # Extraer el número secuencial del último código
        try:
            ultimo_numero = int(ultimo_plan.codigo_plan.split("-")[-1])
            siguiente_numero = ultimo_numero + 1
        except (ValueError, IndexError):
            siguiente_numero = 1
    else:
        siguiente_numero = 1

    # Formatear con 4 dígitos
    codigo = f"{prefijo}{siguiente_numero:04d}"

    # Verificar que el código no exista (por seguridad)
    while PlanMantenimiento.query.filter_by(codigo_plan=codigo).first():
        siguiente_numero += 1
        codigo = f"{prefijo}{siguiente_numero:04d}"

    return codigo


def listar_planes():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search = request.args.get("q", "", type=str)

    query = PlanMantenimiento.query

    # Aplicar filtros de búsqueda
    if search:
        query = query.filter(
            db.or_(
                PlanMantenimiento.codigo_plan.ilike(f"%{search}%"),
                PlanMantenimiento.nombre.ilike(f"%{search}%"),
                PlanMantenimiento.frecuencia.ilike(f"%{search}%"),
            )
        )

    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    planes = pagination.items

    planes_data = [
        {
            "id": p.id,
            "codigo": p.codigo_plan,
            "nombre": p.nombre,
            "equipo": p.activo.nombre if p.activo else "Sin asignar",
            "frecuencia": p.frecuencia,
            "ultima_ejecucion": (
                p.ultima_ejecucion.strftime("%d/%m/%Y") if p.ultima_ejecucion else None
            ),
            "proxima_ejecucion": (
                p.proxima_ejecucion.strftime("%d/%m/%Y")
                if p.proxima_ejecucion
                else None
            ),
            "estado": p.estado,
        }
        for p in planes
    ]

    return {
        "items": planes_data,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


def crear_plan(data):
    # Debug: Imprimir los datos recibidos
    print(f"DEBUG crear_plan - Datos recibidos: {data}")

    # Generar código automático si no se proporciona
    codigo_plan = data.get("codigo", "").strip() if data.get("codigo") else ""
    if not codigo_plan:
        codigo_plan = generar_codigo_plan()
    else:
        # Verificar que el código no esté duplicado si se proporciona manualmente
        plan_existente = PlanMantenimiento.query.filter_by(
            codigo_plan=codigo_plan
        ).first()
        if plan_existente:
            raise ValueError(f"Ya existe un plan con el código '{codigo_plan}'")

    # Calcular la próxima ejecución usando la nueva función
    print(f"DEBUG crear_plan - Calculando próxima ejecución con: {data}")
    proxima_ejecucion = calcular_proxima_ejecucion(data)
    print(f"DEBUG crear_plan - Próxima ejecución calculada: {proxima_ejecucion}")

    # Mantener compatibilidad con el campo frecuencia_dias para frecuencias simples
    frecuencias_dias = {
        "Diario": 1,
        "Semanal": 7,
        "Quincenal": 15,
        "Mensual": 30,
        "Trimestral": 90,
        "Anual": 365,
    }
    dias = frecuencias_dias.get(data.get("frecuencia", "Mensual"), 30)

    nuevo_plan = PlanMantenimiento(
        codigo_plan=codigo_plan,
        nombre=data["nombre"],
        frecuencia=data.get("frecuencia", "Mensual"),
        frecuencia_dias=dias,
        proxima_ejecucion=proxima_ejecucion,
        estado="Activo",
        descripcion=data.get("descripcion"),
        instrucciones=data.get("instrucciones"),
        tiempo_estimado=(
            float(data.get("tiempo_estimado"))
            if data.get("tiempo_estimado") and str(data.get("tiempo_estimado")).strip()
            else None
        ),
        activo_id=data.get("activo_id"),
        # Nuevos campos para configuración específica
        tipo_frecuencia=data.get("tipo_frecuencia"),
        intervalo_semanas=(
            int(data.get("intervalo_semanas"))
            if data.get("intervalo_semanas")
            and str(data.get("intervalo_semanas")).strip()
            else None
        ),
        dias_semana=(
            str(data.get("dias_semana", [])) if data.get("dias_semana") else None
        ),
        tipo_mensual=data.get("tipo_mensual"),
        dia_mes=(
            int(data.get("dia_mes"))
            if data.get("dia_mes") and str(data.get("dia_mes")).strip()
            else None
        ),
        semana_mes=(
            int(data.get("semana_mes"))
            if data.get("semana_mes") and str(data.get("semana_mes")).strip()
            else None
        ),
        dia_semana_mes=(
            data.get("dia_semana_mes")
            if data.get("dia_semana_mes") and str(data.get("dia_semana_mes")).strip()
            else None
        ),
        intervalo_meses=(
            int(data.get("intervalo_meses"))
            if data.get("intervalo_meses") and str(data.get("intervalo_meses")).strip()
            else None
        ),
        frecuencia_personalizada=data.get("frecuencia_personalizada"),
        # Campo de generación automática
        generacion_automatica=data.get("generacion_automatica", True),
    )

    db.session.add(nuevo_plan)
    db.session.commit()
    return nuevo_plan


def obtener_plan_por_id(plan_id):
    """Obtener un plan de mantenimiento por su ID"""
    plan = PlanMantenimiento.query.get_or_404(plan_id)
    return {
        "id": plan.id,
        "codigo_plan": plan.codigo_plan,
        "nombre": plan.nombre,
        "frecuencia": plan.frecuencia,
        "frecuencia_dias": plan.frecuencia_dias,
        "descripcion": plan.descripcion,
        "instrucciones": plan.instrucciones,
        "tiempo_estimado": plan.tiempo_estimado,
        "activo_id": plan.activo_id,
        "activo_nombre": plan.activo.nombre if plan.activo else None,
        "estado": plan.estado,
        "ultima_ejecucion": (
            plan.ultima_ejecucion.strftime("%Y-%m-%d")
            if plan.ultima_ejecucion
            else None
        ),
        "proxima_ejecucion": (
            plan.proxima_ejecucion.strftime("%Y-%m-%d")
            if plan.proxima_ejecucion
            else None
        ),
        "generacion_automatica": plan.generacion_automatica,
    }


def editar_plan(plan_id, data):
    """Editar un plan de mantenimiento existente"""
    plan = PlanMantenimiento.query.get_or_404(plan_id)

    # Verificar código duplicado si se cambió
    if data.get("codigo") and data["codigo"] != plan.codigo_plan:
        plan_existente = PlanMantenimiento.query.filter(
            PlanMantenimiento.codigo_plan == data["codigo"],
            PlanMantenimiento.id != plan_id,
        ).first()
        if plan_existente:
            raise ValueError(f"Ya existe otro plan con el código '{data['codigo']}'")
        plan.codigo_plan = data["codigo"]

    # Actualizar campos
    if "nombre" in data:
        plan.nombre = data["nombre"]
    if "frecuencia" in data:
        plan.frecuencia = data["frecuencia"]
        # Recalcular frecuencia_dias y próxima ejecución
        frecuencias_dias = {
            "Diario": 1,
            "Semanal": 7,
            "Quincenal": 15,
            "Mensual": 30,
            "Trimestral": 90,
            "Anual": 365,
        }
        plan.frecuencia_dias = frecuencias_dias.get(data["frecuencia"], 30)
        # Actualizar próxima ejecución basada en la nueva frecuencia
        plan.proxima_ejecucion = datetime.now() + timedelta(days=plan.frecuencia_dias)

    if "descripcion" in data:
        plan.descripcion = data["descripcion"]
    if "instrucciones" in data:
        plan.instrucciones = data["instrucciones"]
    if "tiempo_estimado" in data:
        plan.tiempo_estimado = (
            float(data["tiempo_estimado"])
            if data["tiempo_estimado"] and str(data["tiempo_estimado"]).strip()
            else None
        )
    if "activo_id" in data:
        plan.activo_id = data["activo_id"]

    # Actualizar campos de configuración específica
    if "tipo_frecuencia" in data:
        plan.tipo_frecuencia = data["tipo_frecuencia"]
    if "intervalo_semanas" in data:
        plan.intervalo_semanas = (
            int(data["intervalo_semanas"])
            if data["intervalo_semanas"] and str(data["intervalo_semanas"]).strip()
            else None
        )
    if "dias_semana" in data:
        plan.dias_semana = str(data["dias_semana"]) if data["dias_semana"] else None
    if "tipo_mensual" in data:
        plan.tipo_mensual = data["tipo_mensual"]
    if "dia_mes" in data:
        plan.dia_mes = (
            int(data["dia_mes"])
            if data["dia_mes"] and str(data["dia_mes"]).strip()
            else None
        )
    if "semana_mes" in data:
        plan.semana_mes = (
            int(data["semana_mes"])
            if data["semana_mes"] and str(data["semana_mes"]).strip()
            else None
        )
    if "dia_semana_mes" in data:
        plan.dia_semana_mes = (
            data["dia_semana_mes"]
            if data["dia_semana_mes"] and str(data["dia_semana_mes"]).strip()
            else None
        )
    if "intervalo_meses" in data:
        plan.intervalo_meses = (
            int(data["intervalo_meses"])
            if data["intervalo_meses"] and str(data["intervalo_meses"]).strip()
            else None
        )
    if "frecuencia_personalizada" in data:
        plan.frecuencia_personalizada = data["frecuencia_personalizada"]

    # Actualizar generación automática
    if "generacion_automatica" in data:
        plan.generacion_automatica = data["generacion_automatica"]

    db.session.commit()
    return plan


def eliminar_plan(plan_id):
    """Eliminar un plan de mantenimiento"""
    plan = PlanMantenimiento.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    return True


def obtener_estadisticas_planes():
    """Obtener estadísticas de planes de mantenimiento"""
    from datetime import datetime, timedelta

    ahora = datetime.now()
    proximos_7_dias = ahora + timedelta(days=7)

    # Planes por estado
    activos = PlanMantenimiento.query.filter_by(estado="Activo").count()
    inactivos = PlanMantenimiento.query.filter_by(estado="Inactivo").count()
    pausados = PlanMantenimiento.query.filter_by(estado="Pausado").count()

    # Planes próximos (próximos 7 días)
    proximos = PlanMantenimiento.query.filter(
        PlanMantenimiento.estado == "Activo",
        PlanMantenimiento.proxima_ejecucion.between(ahora, proximos_7_dias),
    ).count()

    # Planes vencidos (fecha pasada)
    vencidos = PlanMantenimiento.query.filter(
        PlanMantenimiento.estado == "Activo",
        PlanMantenimiento.proxima_ejecucion < ahora,
    ).count()

    # Para "completados" vamos a usar los inactivos por ahora
    completados = inactivos

    return {
        "planes_activos": activos,
        "planes_proximos": proximos,
        "planes_vencidos": vencidos,
        "planes_completados": completados,
        "total_planes": activos + inactivos + pausados,
    }


def generar_ordenes_automaticas():
    """
    Genera órdenes de trabajo automáticamente para planes vencidos
    """
    from app.models.orden_trabajo import OrdenTrabajo
    from app.models.activo import Activo

    print("🔄 Iniciando generación automática de órdenes...")

    ahora = datetime.now()
    ordenes_generadas = []

    # Buscar planes vencidos que estén activos Y tengan generación automática habilitada
    planes_vencidos = PlanMantenimiento.query.filter(
        PlanMantenimiento.estado == "Activo",
        PlanMantenimiento.proxima_ejecucion <= ahora,
        PlanMantenimiento.generacion_automatica
        == True,  # Solo planes con generación automática
    ).all()

    print(f"📋 Encontrados {len(planes_vencidos)} planes vencidos")

    for plan in planes_vencidos:
        try:
            # Verificar si ya existe una orden pendiente para este plan
            orden_existente = OrdenTrabajo.query.filter(
                OrdenTrabajo.tipo == "Mantenimiento Preventivo",
                OrdenTrabajo.activo_id == plan.activo_id,
                OrdenTrabajo.descripcion.contains(f"Plan: {plan.codigo_plan}"),
                OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
            ).first()

            if orden_existente:
                print(f"⚠️ Ya existe orden pendiente para plan {plan.codigo_plan}")
                continue

            # Obtener información del activo
            activo = None
            if plan.activo_id:
                activo = Activo.query.get(plan.activo_id)

            # Crear nueva orden de trabajo
            nueva_orden = OrdenTrabajo(
                tipo="Mantenimiento Preventivo",
                prioridad="Media",  # Puede ajustarse según el plan
                estado="Pendiente",
                descripcion=f"Mantenimiento preventivo - Plan: {plan.codigo_plan} - {plan.nombre}",
                fecha_creacion=ahora,
                fecha_programada=ahora.date(),
                activo_id=plan.activo_id,
                tiempo_estimado=(
                    plan.tiempo_estimado if hasattr(plan, "tiempo_estimado") else None
                ),
                observaciones=f"Orden generada automáticamente desde plan preventivo.\n\nInstrucciones:\n{plan.instrucciones or 'Sin instrucciones específicas'}",
            )

            # Generar número de orden único
            nueva_orden.numero_orden = generar_numero_orden()

            db.session.add(nueva_orden)

            # Actualizar fecha de última ejecución y calcular próxima
            plan.ultima_ejecucion = ahora

            # Recalcular próxima ejecución
            datos_plan = {
                "tipo_frecuencia": plan.tipo_frecuencia,
                "intervalo_dias": plan.frecuencia_dias,
                "intervalo_semanas": plan.intervalo_semanas,
                "dias_semana": plan.dias_semana,
                "tipo_mensual": plan.tipo_mensual,
                "dia_mes": plan.dia_mes,
                "semana_mes": plan.semana_mes,
                "dia_semana_mes": plan.dia_semana_mes,
                "intervalo_meses": plan.intervalo_meses,
                "frecuencia": plan.frecuencia,
            }

            try:
                nueva_proxima = calcular_proxima_ejecucion(datos_plan, ahora)
                plan.proxima_ejecucion = nueva_proxima
                print(
                    f"✅ Plan {plan.codigo_plan}: próxima ejecución actualizada a {nueva_proxima}"
                )
            except Exception as e:
                print(
                    f"⚠️ Error calculando próxima ejecución para plan {plan.codigo_plan}: {e}"
                )
                # Si hay error, programar para el próximo día por defecto
                if plan.tipo_frecuencia == "diaria" or plan.frecuencia == "Diario":
                    plan.proxima_ejecucion = ahora + timedelta(days=1)
                else:
                    plan.proxima_ejecucion = ahora + timedelta(
                        days=7
                    )  # Por defecto semanal

            ordenes_generadas.append(
                {
                    "numero_orden": nueva_orden.numero_orden,
                    "plan_codigo": plan.codigo_plan,
                    "activo_nombre": activo.nombre if activo else "Sin activo",
                    "descripcion": nueva_orden.descripcion,
                }
            )

        except Exception as e:
            print(f"❌ Error generando orden para plan {plan.codigo_plan}: {e}")
            db.session.rollback()
            continue

    # Guardar todos los cambios
    try:
        db.session.commit()
        print(f"🎉 Generación completada: {len(ordenes_generadas)} órdenes creadas")
    except Exception as e:
        print(f"❌ Error guardando cambios: {e}")
        db.session.rollback()
        return {"success": False, "error": str(e)}

    return {
        "success": True,
        "ordenes_generadas": len(ordenes_generadas),
        "detalles": ordenes_generadas,
    }


def generar_numero_orden():
    """Generar un número de orden único"""
    from app.models.orden_trabajo import OrdenTrabajo

    # Obtener el último ID para generar el número
    ultimo_numero = db.session.query(db.func.max(OrdenTrabajo.id)).scalar() or 0
    numero_orden = f"OT-{ultimo_numero + 1:06d}"

    return numero_orden


def generar_ordenes_manuales(usuario="Sistema"):
    """
    Genera órdenes de trabajo manualmente para el día siguiente
    Solo incluye planes que NO tengan generación automática activada
    """
    from app.models.orden_trabajo import OrdenTrabajo
    from app.models.activo import Activo

    print("🔄 Iniciando generación MANUAL de órdenes...")

    # Calcular fecha objetivo (día siguiente)
    ahora = datetime.now()
    fecha_objetivo = ahora + timedelta(days=1)

    ordenes_generadas = []

    # Buscar planes que estén activos y NO tengan generación automática
    planes_manuales = PlanMantenimiento.query.filter(
        PlanMantenimiento.estado == "Activo",
        PlanMantenimiento.generacion_automatica
        == False,  # Solo planes SIN generación automática
        PlanMantenimiento.proxima_ejecucion <= fecha_objetivo,
    ).all()

    print(f"📋 Encontrados {len(planes_manuales)} planes para generación manual")

    for plan in planes_manuales:
        try:
            # Verificar si ya existe una orden pendiente para este plan
            orden_existente = OrdenTrabajo.query.filter(
                OrdenTrabajo.tipo == "Mantenimiento Preventivo",
                OrdenTrabajo.activo_id == plan.activo_id,
                OrdenTrabajo.descripcion.contains(f"Plan: {plan.codigo_plan}"),
                OrdenTrabajo.estado.in_(["Pendiente", "En Proceso"]),
            ).first()

            if orden_existente:
                print(f"⚠️ Ya existe orden pendiente para plan {plan.codigo_plan}")
                continue

            # Obtener información del activo
            activo = None
            if plan.activo_id:
                activo = Activo.query.get(plan.activo_id)

            # Crear nueva orden de trabajo
            nueva_orden = OrdenTrabajo(
                tipo="Mantenimiento Preventivo",
                prioridad="Media",
                estado="Pendiente",
                descripcion=f"Mantenimiento preventivo MANUAL - Plan: {plan.codigo_plan} - {plan.nombre}",
                fecha_creacion=ahora,
                fecha_programada=fecha_objetivo.date(),
                activo_id=plan.activo_id,
                tiempo_estimado=(
                    plan.tiempo_estimado if hasattr(plan, "tiempo_estimado") else None
                ),
                observaciones=f"Orden generada MANUALMENTE por {usuario}.\n\nInstrucciones:\n{plan.instrucciones or 'Sin instrucciones específicas'}",
            )

            # Generar número de orden único
            nuevo_numero = generar_numero_orden()
            nueva_orden.numero_orden = nuevo_numero

            # Agregar orden a la sesión
            db.session.add(nueva_orden)

            print(f"✅ Orden creada: {nuevo_numero} para plan {plan.codigo_plan}")

            # Actualizar próxima ejecución del plan
            try:
                # Usar la configuración del plan para calcular próxima ejecución
                configuracion = {
                    "tipo_frecuencia": plan.tipo_frecuencia,
                    "dias_semana": (
                        json.loads(plan.dias_semana) if plan.dias_semana else []
                    ),
                    "intervalo_semanas": plan.intervalo_semanas or 1,
                    "tipo_mensual": plan.tipo_mensual,
                    "dia_mes": plan.dia_mes,
                    "semana_mes": plan.semana_mes,
                    "dia_semana_mes": plan.dia_semana_mes,
                    "intervalo_meses": plan.intervalo_meses or 1,
                }

                nueva_proxima = calcular_proxima_ejecucion(configuracion, ahora)
                plan.proxima_ejecucion = nueva_proxima
                plan.ultima_ejecucion = ahora

                print(
                    f"📅 Próxima ejecución actualizada: {nueva_proxima.strftime('%Y-%m-%d')}"
                )

            except Exception as e:
                print(
                    f"⚠️ Error calculando próxima ejecución para plan {plan.codigo_plan}: {e}"
                )
                # Fallback por defecto
                if plan.tipo_frecuencia == "diaria" or plan.frecuencia == "Diario":
                    plan.proxima_ejecucion = ahora + timedelta(days=1)
                else:
                    plan.proxima_ejecucion = ahora + timedelta(days=7)

            ordenes_generadas.append(
                {
                    "numero_orden": nueva_orden.numero_orden,
                    "plan_codigo": plan.codigo_plan,
                    "activo_nombre": activo.nombre if activo else "Sin activo",
                    "descripcion": nueva_orden.descripcion,
                }
            )

        except Exception as e:
            print(f"❌ Error generando orden para plan {plan.codigo_plan}: {e}")
            db.session.rollback()
            continue

    # Guardar todos los cambios
    try:
        db.session.commit()
        print(
            f"🎉 Generación MANUAL completada: {len(ordenes_generadas)} órdenes creadas"
        )
    except Exception as e:
        print(f"❌ Error guardando cambios: {e}")
        db.session.rollback()
        return {"success": False, "error": str(e)}

    return {
        "success": True,
        "tipo": "manual",
        "ordenes_generadas": len(ordenes_generadas),
        "detalles": ordenes_generadas,
        "usuario": usuario,
    }
