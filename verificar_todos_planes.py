#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación completa de todos los planes de mantenimiento
Analiza si todos los planes tienen configuraciones correctas
"""

import sqlite3
from datetime import datetime, timedelta
import ast
import json


def verificar_todos_los_planes():
    print("🔍 VERIFICACIÓN COMPLETA DE PLANES DE MANTENIMIENTO")
    print("=" * 60)

    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    # Obtener todos los planes
    cursor.execute(
        """
        SELECT id, codigo_plan, nombre, frecuencia, frecuencia_dias,
               ultima_ejecucion, proxima_ejecucion, estado, 
               tipo_frecuencia, intervalo_semanas, dias_semana,
               generacion_automatica
        FROM plan_mantenimiento
        ORDER BY codigo_plan
    """
    )

    planes = cursor.fetchall()

    if not planes:
        print("❌ No se encontraron planes de mantenimiento")
        return

    print(f"📊 Total de planes encontrados: {len(planes)}")
    print("\n" + "=" * 60)

    planes_ok = 0
    planes_problema = 0

    for i, plan in enumerate(planes, 1):
        (
            id_plan,
            codigo,
            nombre,
            frecuencia,
            freq_dias,
            ultima_ej,
            proxima_ej,
            estado,
            tipo_freq,
            intervalo_sem,
            dias_sem,
            gen_auto,
        ) = plan

        print(f"\n📋 PLAN {i}: {codigo} - {nombre}")
        print(f"   Estado: {estado}")
        print(
            f"   Generación automática: {'✅ Habilitada' if gen_auto else '❌ Deshabilitada'}"
        )
        print(f"   Frecuencia: {frecuencia} ({tipo_freq})")

        if proxima_ej:
            print(f"   Próxima ejecución: {proxima_ej}")
        else:
            print(f"   Próxima ejecución: ❌ No configurada")

        # Verificar problemas específicos
        problemas = []

        # 1. Verificar generación automática
        if not gen_auto:
            problemas.append("Generación automática deshabilitada")

        # 2. Verificar próxima ejecución
        if not proxima_ej:
            problemas.append("Próxima ejecución no configurada")

        # 3. Verificar configuración semanal
        if tipo_freq == "semanal" and dias_sem:
            try:
                # Intentar parsear días de la semana
                if isinstance(dias_sem, str):
                    if dias_sem.startswith("["):
                        dias_data = ast.literal_eval(dias_sem)
                    else:
                        dias_data = [d.strip() for d in dias_sem.split(",")]
                else:
                    dias_data = dias_sem

                print(f"   Días semana: {dias_data}")

                # Validar días
                dias_validos = [
                    "lunes",
                    "martes",
                    "miércoles",
                    "miercoles",
                    "jueves",
                    "viernes",
                    "sábado",
                    "sabado",
                    "domingo",
                ]
                for dia in dias_data:
                    if isinstance(dia, str) and dia.lower().strip() not in dias_validos:
                        problemas.append(f"Día no válido: '{dia}'")

                # Verificar que la próxima ejecución sea en un día válido
                if proxima_ej:
                    try:
                        fecha_prox = datetime.strptime(
                            proxima_ej[:19], "%Y-%m-%d %H:%M:%S"
                        )
                        dia_semana_num = fecha_prox.weekday()

                        # Mapear días a números
                        mapeo_dias = {
                            "lunes": 0,
                            "martes": 1,
                            "miércoles": 2,
                            "miercoles": 2,
                            "jueves": 3,
                            "viernes": 4,
                            "sábado": 5,
                            "sabado": 5,
                            "domingo": 6,
                        }

                        dias_nums = []
                        for dia in dias_data:
                            if isinstance(dia, str):
                                dia_clean = dia.lower().strip()
                                if dia_clean in mapeo_dias:
                                    dias_nums.append(mapeo_dias[dia_clean])

                        if dia_semana_num not in dias_nums:
                            nombres_dias = [
                                "Lunes",
                                "Martes",
                                "Miércoles",
                                "Jueves",
                                "Viernes",
                                "Sábado",
                                "Domingo",
                            ]
                            dia_nombre = nombres_dias[dia_semana_num]
                            problemas.append(
                                f"Próxima ejecución ({dia_nombre}) no está en días configurados"
                            )

                    except Exception as e:
                        problemas.append(f"Error parseando fecha: {e}")

            except Exception as e:
                problemas.append(f"Error parseando días semana: {e}")

        # 4. Verificar estado activo
        if estado != "Activo":
            problemas.append(f"Plan no está activo (estado: {estado})")

        # Mostrar resultado del plan
        if problemas:
            planes_problema += 1
            print(f"   🚨 PROBLEMAS DETECTADOS:")
            for problema in problemas:
                print(f"      • {problema}")
        else:
            planes_ok += 1
            print(f"   ✅ PLAN CORRECTO")

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    print(f"   ✅ Planes correctos: {planes_ok}")
    print(f"   🚨 Planes con problemas: {planes_problema}")
    print(f"   📝 Total analizado: {len(planes)}")

    if planes_problema == 0:
        print(f"\n🎉 ¡TODOS LOS PLANES ESTÁN CORRECTOS!")
    else:
        print(f"\n⚠️  {planes_problema} planes necesitan atención")

    conn.close()


if __name__ == "__main__":
    verificar_todos_los_planes()
