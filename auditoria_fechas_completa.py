from app import create_app
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.controllers.planes_controller import calcular_proxima_ejecucion
from datetime import datetime, timedelta
import json


def revisar_calculo_fechas():
    """Auditoría completa del cálculo de fechas en planes"""
    app = create_app()

    with app.app_context():
        print("🔍 AUDITORÍA DE CÁLCULO DE FECHAS - PLANES DE MANTENIMIENTO")
        print("=" * 70)

        # 1. Obtener todos los planes
        planes = PlanMantenimiento.query.all()
        print(f"📋 Total de planes encontrados: {len(planes)}")

        if not planes:
            print("⚠️ No hay planes en la base de datos")
            return

        problemas_encontrados = []

        print("\n📊 ANÁLISIS POR PLAN:")
        print("-" * 50)

        for i, plan in enumerate(planes, 1):
            print(f"\n{i}. Plan: {plan.codigo_plan}")
            print(f"   Nombre: {plan.nombre}")
            print(f"   Estado: {plan.estado}")
            print(f"   Tipo frecuencia: {plan.tipo_frecuencia}")

            # Información de configuración según tipo
            if plan.tipo_frecuencia == "semanal":
                print(f"   Días semana: {plan.dias_semana}")
                print(f"   Intervalo semanas: {plan.intervalo_semanas}")

                # Verificar configuración
                if plan.dias_semana:
                    try:
                        if isinstance(plan.dias_semana, str):
                            dias = json.loads(plan.dias_semana)
                        else:
                            dias = plan.dias_semana
                        print(f"   Días configurados: {dias}")

                        # Verificar que los días sean válidos
                        dias_validos = [
                            "lunes",
                            "martes",
                            "miercoles",
                            "jueves",
                            "viernes",
                            "sabado",
                            "domingo",
                        ]
                        for dia in dias:
                            if dia.lower() not in dias_validos:
                                problemas_encontrados.append(
                                    f"Plan {plan.codigo_plan}: Día inválido '{dia}'"
                                )

                    except Exception as e:
                        problemas_encontrados.append(
                            f"Plan {plan.codigo_plan}: Error parsing días_semana: {e}"
                        )
                        print(f"   ❌ Error en días_semana: {e}")

            elif plan.tipo_frecuencia == "mensual":
                print(f"   Tipo mensual: {plan.tipo_mensual}")
                print(f"   Día mes: {plan.dia_mes}")
                print(f"   Semana mes: {plan.semana_mes}")
                print(f"   Día semana mes: {plan.dia_semana_mes}")
                print(f"   Intervalo meses: {plan.intervalo_meses}")

            elif plan.tipo_frecuencia == "diaria":
                print(f"   Frecuencia: {plan.frecuencia}")
                print(f"   Días frecuencia: {plan.frecuencia_dias}")

            # Fechas actuales
            print(f"   Última ejecución: {plan.ultima_ejecucion}")
            print(f"   Próxima ejecución: {plan.proxima_ejecucion}")

            if plan.proxima_ejecucion:
                dia_semana = plan.proxima_ejecucion.strftime("%A")
                print(f"   Día programado: {dia_semana}")

                # Verificar si la fecha es coherente con la configuración
                if plan.tipo_frecuencia == "semanal" and plan.dias_semana:
                    try:
                        if isinstance(plan.dias_semana, str):
                            dias_config = json.loads(plan.dias_semana)
                        else:
                            dias_config = plan.dias_semana

                        # Mapeo español -> inglés para verificación
                        mapeo_dias = {
                            "lunes": "Monday",
                            "martes": "Tuesday",
                            "miercoles": "Wednesday",
                            "jueves": "Thursday",
                            "viernes": "Friday",
                            "sabado": "Saturday",
                            "domingo": "Sunday",
                        }

                        dias_esperados = [
                            mapeo_dias.get(d.lower()) for d in dias_config
                        ]

                        if dia_semana not in dias_esperados:
                            problema = f"Plan {plan.codigo_plan}: Día programado '{dia_semana}' no coincide con configuración {dias_config}"
                            problemas_encontrados.append(problema)
                            print(f"   ❌ {problema}")
                        else:
                            print(f"   ✅ Día coherente con configuración")

                    except Exception as e:
                        print(f"   ⚠️ No se pudo verificar coherencia: {e}")

            # Probar recálculo
            try:
                datos_plan = {
                    "tipo_frecuencia": plan.tipo_frecuencia,
                    "intervalo_semanas": plan.intervalo_semanas,
                    "dias_semana": (
                        json.loads(plan.dias_semana)
                        if plan.dias_semana and isinstance(plan.dias_semana, str)
                        else plan.dias_semana
                    ),
                    "tipo_mensual": plan.tipo_mensual,
                    "dia_mes": plan.dia_mes,
                    "semana_mes": plan.semana_mes,
                    "dia_semana_mes": plan.dia_semana_mes,
                    "intervalo_meses": plan.intervalo_meses,
                    "frecuencia": plan.frecuencia,
                }

                ahora = datetime.now()
                nueva_fecha = calcular_proxima_ejecucion(datos_plan, ahora)
                print(
                    f"   🧮 Recálculo desde ahora: {nueva_fecha} ({nueva_fecha.strftime('%A')})"
                )

                if (
                    abs((nueva_fecha - plan.proxima_ejecucion).days) > 7
                    and plan.estado == "Activo"
                ):
                    problema = f"Plan {plan.codigo_plan}: Gran diferencia entre fecha actual ({plan.proxima_ejecucion}) y recálculo ({nueva_fecha})"
                    problemas_encontrados.append(problema)
                    print(f"   ⚠️ {problema}")

            except Exception as e:
                problema = f"Plan {plan.codigo_plan}: Error en recálculo: {e}"
                problemas_encontrados.append(problema)
                print(f"   ❌ {problema}")

        # 2. Revisar órdenes generadas vs planes
        print(f"\n🔍 VERIFICACIÓN DE ÓRDENES GENERADAS:")
        print("-" * 40)

        ordenes_preventivas = OrdenTrabajo.query.filter(
            OrdenTrabajo.tipo == "Mantenimiento Preventivo"
        ).all()

        print(f"📋 Órdenes preventivas encontradas: {len(ordenes_preventivas)}")

        for orden in ordenes_preventivas:
            print(f"\n   Orden: {orden.numero_orden}")
            print(f"   Fecha programada: {orden.fecha_programada}")
            if orden.fecha_programada:
                print(f"   Día: {orden.fecha_programada.strftime('%A')}")
            print(f"   Descripción: {orden.descripcion}")

            # Verificar si coincide con algún plan
            plan_relacionado = None
            for plan in planes:
                if plan.codigo_plan in orden.descripcion:
                    plan_relacionado = plan
                    break

            if plan_relacionado:
                print(f"   🔗 Plan relacionado: {plan_relacionado.codigo_plan}")
                if (
                    plan_relacionado.tipo_frecuencia == "semanal"
                    and plan_relacionado.dias_semana
                ):
                    try:
                        dias_config = (
                            json.loads(plan_relacionado.dias_semana)
                            if isinstance(plan_relacionado.dias_semana, str)
                            else plan_relacionado.dias_semana
                        )
                        mapeo_dias = {
                            "lunes": "Monday",
                            "martes": "Tuesday",
                            "miercoles": "Wednesday",
                            "jueves": "Thursday",
                            "viernes": "Friday",
                            "sabado": "Saturday",
                            "domingo": "Sunday",
                        }
                        dias_esperados = [
                            mapeo_dias.get(d.lower()) for d in dias_config
                        ]
                        dia_orden = (
                            orden.fecha_programada.strftime("%A")
                            if orden.fecha_programada
                            else None
                        )

                        if dia_orden and dia_orden not in dias_esperados:
                            problema = f"Orden {orden.numero_orden}: Día '{dia_orden}' no coincide con plan {dias_config}"
                            problemas_encontrados.append(problema)
                            print(f"   ❌ {problema}")
                        else:
                            print(f"   ✅ Orden coherente con plan")
                    except:
                        print(f"   ⚠️ No se pudo verificar coherencia con plan")
            else:
                print(f"   ⚠️ No se encontró plan relacionado")

        # 3. Resumen de problemas
        print(f"\n🎯 RESUMEN DE AUDITORÍA:")
        print("=" * 50)
        print(f"✅ Planes analizados: {len(planes)}")
        print(f"✅ Órdenes preventivas: {len(ordenes_preventivas)}")
        print(f"❌ Problemas encontrados: {len(problemas_encontrados)}")

        if problemas_encontrados:
            print(f"\n🚨 PROBLEMAS DETECTADOS:")
            for i, problema in enumerate(problemas_encontrados, 1):
                print(f"   {i}. {problema}")
        else:
            print(f"\n🎉 ¡No se encontraron problemas en el cálculo de fechas!")

        return problemas_encontrados


if __name__ == "__main__":
    problemas = revisar_calculo_fechas()

    if problemas:
        print(f"\n⚠️ Se encontraron {len(problemas)} problemas que requieren atención.")
    else:
        print(f"\n✅ Todos los cálculos de fechas están correctos.")
