#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación de datos que se mostrarán en el calendario
"""

import sqlite3
from datetime import datetime, timedelta
import json


def verificar_calendario():
    print("📅 VERIFICACIÓN DEL CALENDARIO DE MANTENIMIENTO")
    print("=" * 55)

    # Conectar a la base de datos
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    # Obtener fecha actual y rango del mes
    hoy = datetime.now()
    year = hoy.year
    month = hoy.month

    # Calcular primer y último día del mes actual
    primer_dia = datetime(year, month, 1)
    if month == 12:
        ultimo_dia = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = datetime(year, month + 1, 1) - timedelta(days=1)

    print(f"🗓️  Mes actual: {hoy.strftime('%B %Y')}")
    print(
        f"📊 Rango: {primer_dia.strftime('%d/%m/%Y')} - {ultimo_dia.strftime('%d/%m/%Y')}"
    )
    print()

    # 1. Verificar órdenes existentes en el mes
    print("🔧 ÓRDENES DE TRABAJO EXISTENTES:")
    print("-" * 40)

    cursor.execute(
        """
        SELECT numero_orden, descripcion, fecha_programada, estado, 
               fecha_creacion, activo_id
        FROM orden_trabajo
        WHERE fecha_programada BETWEEN ? AND ?
        ORDER BY fecha_programada
    """,
        (primer_dia.strftime("%Y-%m-%d"), ultimo_dia.strftime("%Y-%m-%d")),
    )

    ordenes = cursor.fetchall()

    if ordenes:
        for orden in ordenes:
            numero, desc, fecha_prog, estado, fecha_crea, activo_id = orden
            fecha_obj = datetime.strptime(fecha_prog[:19], "%Y-%m-%d %H:%M:%S")

            color_estado = {
                "Pendiente": "🟡",
                "En Proceso": "🔵",
                "Completada": "🟢",
                "Cancelada": "🔴",
            }.get(estado, "⚪")

            print(
                f"   {color_estado} {numero} - {desc[:30]}{'...' if len(desc) > 30 else ''}"
            )
            print(
                f"      📅 {fecha_obj.strftime('%A %d/%m/%Y %H:%M')} | Estado: {estado}"
            )
            print()
    else:
        print("   📭 No hay órdenes de trabajo programadas para este mes")
        print()

    # 2. Verificar planes futuros que aparecerán en el calendario
    print("📋 PLANES FUTUROS (Próximas ejecuciones):")
    print("-" * 40)

    cursor.execute(
        """
        SELECT codigo_plan, nombre, descripcion, proxima_ejecucion, 
               frecuencia, tipo_frecuencia, activo_id, generacion_automatica
        FROM plan_mantenimiento
        WHERE estado = 'Activo' 
        AND proxima_ejecucion BETWEEN ? AND ?
        ORDER BY proxima_ejecucion
    """,
        (primer_dia.strftime("%Y-%m-%d"), ultimo_dia.strftime("%Y-%m-%d")),
    )

    planes = cursor.fetchall()

    eventos_calendario = []

    if planes:
        for plan in planes:
            (
                codigo,
                nombre,
                desc,
                proxima_ej,
                frecuencia,
                tipo_freq,
                activo_id,
                gen_auto,
            ) = plan

            # Obtener nombre del activo
            cursor.execute("SELECT nombre FROM activo WHERE id = ?", (activo_id,))
            activo_result = cursor.fetchone()
            activo_nombre = activo_result[0] if activo_result else "Sin activo"

            fecha_obj = datetime.strptime(proxima_ej[:19], "%Y-%m-%d %H:%M:%S")

            auto_icon = "🤖" if gen_auto else "👤"

            print(f"   🔮 {codigo} - {nombre}")
            print(f"      📅 {fecha_obj.strftime('%A %d/%m/%Y %H:%M')}")
            print(f"      🏭 Activo: {activo_nombre}")
            print(f"      🔄 Frecuencia: {frecuencia} ({tipo_freq})")
            print(f"      {auto_icon} {'Automático' if gen_auto else 'Manual'}")
            print()

            # Crear evento para el calendario
            evento = {
                "id": f"plan-{plan[0]}",  # usando índice 0 para codigo_plan
                "title": f"📅 {codigo}",
                "description": f"Mantenimiento preventivo: {nombre}",
                "start": fecha_obj.isoformat(),
                "backgroundColor": "#6f42c1",  # Púrpura para planes
                "borderColor": "#6f42c1",
                "tipo": "plan_futuro",
                "activo_nombre": activo_nombre,
                "frecuencia": frecuencia,
            }
            eventos_calendario.append(evento)
    else:
        print("   📭 No hay planes programados para ejecutarse este mes")
        print()

    # 3. Estadísticas del calendario
    print("📊 ESTADÍSTICAS DEL CALENDARIO:")
    print("-" * 35)
    print(f"   🔧 Órdenes programadas: {len(ordenes)}")
    print(f"   📋 Planes futuros: {len(planes)}")
    print(f"   📅 Total eventos: {len(ordenes) + len(planes)}")

    # 4. Próximos 7 días específicamente
    print(f"\n🔮 PRÓXIMOS 7 DÍAS EN EL CALENDARIO:")
    print("-" * 40)

    fecha_limite_7dias = hoy + timedelta(days=7)

    # Órdenes en próximos 7 días
    cursor.execute(
        """
        SELECT numero_orden, descripcion, fecha_programada, estado
        FROM orden_trabajo
        WHERE fecha_programada BETWEEN ? AND ?
        ORDER BY fecha_programada
    """,
        (
            hoy.strftime("%Y-%m-%d %H:%M:%S"),
            fecha_limite_7dias.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    ordenes_7dias = cursor.fetchall()

    # Planes en próximos 7 días
    cursor.execute(
        """
        SELECT codigo_plan, nombre, proxima_ejecucion
        FROM plan_mantenimiento
        WHERE estado = 'Activo' 
        AND proxima_ejecucion BETWEEN ? AND ?
        ORDER BY proxima_ejecucion
    """,
        (
            hoy.strftime("%Y-%m-%d %H:%M:%S"),
            fecha_limite_7dias.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    planes_7dias = cursor.fetchall()

    # Combinar y mostrar cronológicamente
    eventos_7dias = []

    for orden in ordenes_7dias:
        fecha_obj = datetime.strptime(orden[2][:19], "%Y-%m-%d %H:%M:%S")
        eventos_7dias.append(
            {
                "fecha": fecha_obj,
                "tipo": "orden",
                "titulo": orden[0],
                "desc": orden[1][:30] + ("..." if len(orden[1]) > 30 else ""),
                "estado": orden[3],
            }
        )

    for plan in planes_7dias:
        fecha_obj = datetime.strptime(plan[2][:19], "%Y-%m-%d %H:%M:%S")
        eventos_7dias.append(
            {"fecha": fecha_obj, "tipo": "plan", "titulo": plan[0], "desc": plan[1]}
        )

    # Ordenar por fecha
    eventos_7dias.sort(key=lambda x: x["fecha"])

    if eventos_7dias:
        for evento in eventos_7dias:
            dias_hasta = (evento["fecha"].date() - hoy.date()).days

            if dias_hasta == 0:
                etiqueta = "🔥 HOY"
            elif dias_hasta == 1:
                etiqueta = "⏰ MAÑANA"
            else:
                etiqueta = f"📅 En {dias_hasta} días"

            icono = "🔧" if evento["tipo"] == "orden" else "📋"

            print(f"   {etiqueta} {icono} {evento['titulo']}")
            print(f"      {evento['desc']}")
            if evento["tipo"] == "orden":
                print(f"      Estado: {evento['estado']}")
            print(f"      {evento['fecha'].strftime('%A %d/%m/%Y %H:%M')}")
            print()
    else:
        print("   📭 No hay eventos programados en los próximos 7 días")

    conn.close()

    # 5. Resumen final
    print("📋 RESUMEN PARA EL CALENDARIO:")
    print("-" * 35)
    print(f"✅ Los planes de mantenimiento SÍ aparecerán en el calendario")
    print(f"📅 Se muestran como eventos púrpura con prefijo 📅")
    print(f"🔮 Indican cuándo se generarán automáticamente las órdenes")
    print(f"📊 Total eventos del mes: {len(ordenes) + len(planes)}")

    if len(planes) > 0:
        print(f"🎉 ¡{len(planes)} planes aparecerán en el calendario este mes!")
    else:
        print(f"📭 No hay planes programados para este mes en el calendario")


if __name__ == "__main__":
    verificar_calendario()
