#!/usr/bin/env python3
"""
Verificar el plan PM-2025-0001 y su configuración de frecuencia
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.plan_mantenimiento import PlanMantenimiento
from app.extensions import db
from datetime import datetime, timedelta


def verificar_plan():
    """Verificar configuración del plan PM-2025-0001"""

    app = create_app()

    with app.app_context():
        print("🔍 VERIFICANDO PLAN PM-2025-0001")
        print("=" * 50)

        plan = PlanMantenimiento.query.filter_by(codigo_plan="PM-2025-0001").first()
        if not plan:
            print("❌ Plan no encontrado")
            return False

        print(f"📋 Plan encontrado:")
        print(f"   • Código: {plan.codigo_plan}")
        print(f"   • Nombre: {plan.nombre}")
        print(f"   • Descripción: {plan.descripcion}")
        print(f"   • Estado: {plan.estado}")
        print(f"   • Frecuencia: {plan.frecuencia}")
        print(f"   • Frecuencia días: {plan.frecuencia_dias}")
        print(f"   • Días semana (raw): {repr(plan.dias_semana)}")
        print(f"   • Intervalo semanas: {plan.intervalo_semanas}")
        print(f"   • Última ejecución: {plan.ultima_ejecucion}")
        print(f"   • Próxima ejecución: {plan.proxima_ejecucion}")
        print(f"   • Generación automática: {plan.generacion_automatica}")

        # Analizar los días de la semana
        if plan.dias_semana:
            try:
                # Si es string, intentar evaluar
                if isinstance(plan.dias_semana, str):
                    dias_lista = (
                        eval(plan.dias_semana)
                        if plan.dias_semana.startswith("[")
                        else plan.dias_semana.split(",")
                    )
                else:
                    dias_lista = plan.dias_semana

                print(f"\n📅 Análisis de días de la semana:")
                print(f"   • Tipo: {type(dias_lista)}")
                print(f"   • Días configurados: {dias_lista}")

                # Mapeo de días
                dias_semana_map = {
                    "lunes": 0,
                    "martes": 1,
                    "miercoles": 2,
                    "jueves": 3,
                    "viernes": 4,
                    "sabado": 5,
                    "domingo": 6,
                }

                dias_numericos = []
                for dia in dias_lista:
                    if isinstance(dia, str):
                        dia_num = dias_semana_map.get(dia.lower())
                        if dia_num is not None:
                            dias_numericos.append(dia_num)
                            print(
                                f"   • {dia} → {dia_num} ({'Lun Mar Mié Jue Vie Sáb Dom'.split()[dia_num]})"
                            )

                print(f"   • Días numéricos: {dias_numericos}")

            except Exception as e:
                print(f"   ❌ Error al analizar días: {e}")

        # Simular cálculo de próxima ejecución
        print(f"\n🔄 Simulando cálculo de próxima ejecución:")
        fecha_actual = datetime(2025, 9, 28)  # Fecha actual del contexto
        print(f"   • Fecha base: {fecha_actual.strftime('%Y-%m-%d %A')}")

        # Días de la semana en español
        dias_semana = [
            "lunes",
            "martes",
            "miércoles",
            "jueves",
            "viernes",
            "sábado",
            "domingo",
        ]
        dia_actual_es = dias_semana[fecha_actual.weekday()]
        print(f"   • Día actual: {dia_actual_es} (weekday={fecha_actual.weekday()})")

        return True


if __name__ == "__main__":
    verificar_plan()
