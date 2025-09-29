#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación detallada de las fechas de ejecución de todos los planes
"""

import sqlite3
from datetime import datetime, timedelta
import ast


def verificar_fechas_ejecucion():
    print("📅 VERIFICACIÓN DETALLADA DE FECHAS DE EJECUCIÓN")
    print("=" * 55)

    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    # Obtener todos los planes activos con generación automática
    cursor.execute(
        """
        SELECT codigo_plan, nombre, tipo_frecuencia, dias_semana, 
               proxima_ejecucion, generacion_automatica
        FROM plan_mantenimiento
        WHERE estado = 'Activo' AND generacion_automatica = 1
        ORDER BY codigo_plan
    """
    )

    planes = cursor.fetchall()

    if not planes:
        print("❌ No hay planes activos con generación automática")
        return

    hoy = datetime.now()
    print(f"🕒 Fecha actual: {hoy.strftime('%A %d/%m/%Y %H:%M')}")
    print(f"    Día de semana: {hoy.weekday()} (0=Lunes, 6=Domingo)")
    print()

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
    nombres_dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]

    for i, plan in enumerate(planes, 1):
        codigo, nombre, tipo_freq, dias_sem, proxima_ej, gen_auto = plan

        print(f"📋 PLAN {i}: {codigo} - {nombre}")
        print(f"   Tipo: {tipo_freq}")

        if proxima_ej:
            try:
                fecha_prox = datetime.strptime(proxima_ej[:19], "%Y-%m-%d %H:%M:%S")
                print(
                    f"   Próxima ejecución: {fecha_prox.strftime('%A %d/%m/%Y %H:%M')}"
                )

                # Calcular días hasta la próxima ejecución
                dias_diferencia = (fecha_prox.date() - hoy.date()).days

                if dias_diferencia < 0:
                    print(f"   ⚠️  ATRASADA: {abs(dias_diferencia)} días")
                elif dias_diferencia == 0:
                    print(f"   🔥 HOY: Se debe ejecutar hoy")
                elif dias_diferencia == 1:
                    print(f"   ⏰ MAÑANA: Se ejecuta en 1 día")
                else:
                    print(f"   ⏳ FUTURO: En {dias_diferencia} días")

                # Verificación específica por tipo
                if tipo_freq == "semanal" and dias_sem:
                    try:
                        if isinstance(dias_sem, str):
                            if dias_sem.startswith("["):
                                dias_data = ast.literal_eval(dias_sem)
                            else:
                                dias_data = [d.strip() for d in dias_sem.split(",")]
                        else:
                            dias_data = dias_sem

                        print(f"   Días configurados: {dias_data}")

                        # Verificar si la próxima fecha es correcta
                        dia_semana_proxima = fecha_prox.weekday()
                        nombre_dia_proxima = nombres_dias[dia_semana_proxima]

                        # Convertir días configurados a números
                        dias_nums = []
                        for dia in dias_data:
                            if isinstance(dia, str):
                                dia_clean = dia.lower().strip()
                                if dia_clean in mapeo_dias:
                                    dias_nums.append(mapeo_dias[dia_clean])

                        if dia_semana_proxima in dias_nums:
                            print(
                                f"   ✅ {nombre_dia_proxima} SÍ está en días configurados"
                            )
                        else:
                            print(
                                f"   ❌ {nombre_dia_proxima} NO está en días configurados"
                            )
                            print(
                                f"      Debería ser uno de: {[nombres_dias[d] for d in dias_nums]}"
                            )

                    except Exception as e:
                        print(f"   ❌ Error verificando días: {e}")

                elif tipo_freq == "diario":
                    # Para planes diarios, verificar que sea mañana o posterior
                    if dias_diferencia >= 0:
                        print(f"   ✅ Fecha diaria correcta")
                    else:
                        print(f"   ❌ Plan diario atrasado")

                elif tipo_freq == "mensual":
                    # Para planes mensuales, verificar que sea futuro
                    if dias_diferencia > 0:
                        print(f"   ✅ Fecha mensual correcta")
                    else:
                        print(f"   ⚠️  Verificar plan mensual")

            except Exception as e:
                print(f"   ❌ Error parseando fecha: {e}")
        else:
            print(f"   ❌ Sin próxima ejecución configurada")

        print()  # Línea en blanco entre planes

    conn.close()

    # Resumen de próximas ejecuciones
    print("🔮 PRÓXIMAS EJECUCIONES EN LOS PRÓXIMOS 7 DÍAS:")
    print("-" * 50)

    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    fecha_limite = hoy + timedelta(days=7)

    cursor.execute(
        """
        SELECT codigo_plan, nombre, proxima_ejecucion
        FROM plan_mantenimiento
        WHERE estado = 'Activo' 
        AND generacion_automatica = 1
        AND proxima_ejecucion BETWEEN ? AND ?
        ORDER BY proxima_ejecucion
    """,
        (hoy.strftime("%Y-%m-%d %H:%M:%S"), fecha_limite.strftime("%Y-%m-%d %H:%M:%S")),
    )

    proximas = cursor.fetchall()

    if proximas:
        for plan in proximas:
            codigo, nombre, fecha_ej = plan
            fecha_obj = datetime.strptime(fecha_ej[:19], "%Y-%m-%d %H:%M:%S")
            dias_hasta = (fecha_obj.date() - hoy.date()).days

            if dias_hasta == 0:
                etiqueta = "🔥 HOY"
            elif dias_hasta == 1:
                etiqueta = "⏰ MAÑANA"
            else:
                etiqueta = f"📅 En {dias_hasta} días"

            print(f"   {etiqueta} - {codigo}: {nombre}")
            print(f"      {fecha_obj.strftime('%A %d/%m/%Y %H:%M')}")
    else:
        print("   📭 No hay ejecuciones programadas en los próximos 7 días")

    conn.close()


if __name__ == "__main__":
    verificar_fechas_ejecucion()
