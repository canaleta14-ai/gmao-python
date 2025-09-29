#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulación del API del calendario para mostrar exactamente lo que se verá
"""

import sqlite3
from datetime import datetime, timedelta
import json


def simular_api_calendario():
    print("📱 SIMULACIÓN DEL API DEL CALENDARIO")
    print("=" * 45)

    # Conectar a la base de datos
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    # Simular parámetros como lo haría la aplicación web
    hoy = datetime.now()
    year = hoy.year
    month = hoy.month

    print(f"🎯 Simulando API para: {hoy.strftime('%B %Y')}")
    print(f"📊 URL simulada: /calendario/api/ordenes?year={year}&month={month}")
    print()

    # Calcular rango del mes (igual que en el API real)
    primer_dia = datetime(year, month, 1)
    if month == 12:
        ultimo_dia = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = datetime(year, month + 1, 1) - timedelta(days=1)

    # 1. Obtener órdenes (como en el API real)
    cursor.execute(
        """
        SELECT id, numero_orden, descripcion, fecha_programada, estado, 
               prioridad, activo_id
        FROM orden_trabajo
        WHERE fecha_programada >= ? AND fecha_programada <= ?
    """,
        (primer_dia.strftime("%Y-%m-%d"), ultimo_dia.strftime("%Y-%m-%d")),
    )

    ordenes = cursor.fetchall()

    # 2. Obtener planes futuros (como en el API real)
    cursor.execute(
        """
        SELECT id, codigo_plan, nombre, descripcion, proxima_ejecucion, 
               frecuencia, activo_id
        FROM plan_mantenimiento
        WHERE estado = 'Activo' 
        AND proxima_ejecucion >= ? AND proxima_ejecucion <= ?
    """,
        (primer_dia.strftime("%Y-%m-%d"), ultimo_dia.strftime("%Y-%m-%d")),
    )

    planes = cursor.fetchall()

    eventos = []

    # 3. Procesar órdenes (como en el API real)
    print("🔧 ÓRDENES DE TRABAJO EN EL CALENDARIO:")
    print("-" * 40)

    for orden in ordenes:
        id_orden, numero, desc, fecha_prog, estado, prioridad, activo_id = orden

        # Colores como en el código real
        color = {
            "Pendiente": "#ffc107",  # Amarillo
            "En Proceso": "#17a2b8",  # Azul
            "Completada": "#28a745",  # Verde
            "Cancelada": "#dc3545",  # Rojo
        }.get(
            estado, "#6c757d"
        )  # Gris por defecto

        evento_orden = {
            "id": f"orden-{id_orden}",
            "title": f"{numero}",
            "description": desc[:50] + ("..." if len(desc) > 50 else ""),
            "start": fecha_prog,
            "backgroundColor": color,
            "borderColor": color,
            "tipo": "orden",
            "estado": estado,
            "prioridad": prioridad,
            "activo_id": activo_id,
        }

        eventos.append(evento_orden)
        print(f"   📋 {numero}: {desc[:30]}{'...' if len(desc) > 30 else ''}")
        print(f"      📅 {fecha_prog} | {estado} | Color: {color}")

    if not ordenes:
        print("   📭 No hay órdenes de trabajo para este mes")

    print()

    # 4. Procesar planes futuros (como en el API real)
    print("🔮 PLANES FUTUROS EN EL CALENDARIO:")
    print("-" * 38)

    for plan in planes:
        id_plan, codigo, nombre, desc, proxima_ej, frecuencia, activo_id = plan

        # Obtener activo (como en el API real)
        cursor.execute("SELECT nombre FROM activo WHERE id = ?", (activo_id,))
        activo_result = cursor.fetchone()
        activo_nombre = activo_result[0] if activo_result else "Sin activo"

        evento_plan = {
            "id": f"plan-{id_plan}",
            "title": f"📅 {codigo}",
            "description": f"Mantenimiento preventivo: {nombre}",
            "start": proxima_ej,
            "backgroundColor": "#6f42c1",  # Púrpura para planes
            "borderColor": "#6f42c1",
            "tipo": "plan_futuro",
            "activo_nombre": activo_nombre,
            "frecuencia": frecuencia,
        }

        eventos.append(evento_plan)

        fecha_obj = datetime.strptime(proxima_ej[:19], "%Y-%m-%d %H:%M:%S")
        print(f"   📋 📅 {codigo}: {nombre}")
        print(f"      📅 {fecha_obj.strftime('%A %d/%m/%Y %H:%M')}")
        print(f"      🏭 {activo_nombre} | {frecuencia} | Color: #6f42c1 (púrpura)")

    if not planes:
        print("   📭 No hay planes futuros para este mes")

    print()

    # 5. Simular respuesta JSON del API
    respuesta_api = {
        "success": True,
        "eventos": eventos,
        "mes": month,
        "anio": year,
        "total_ordenes": len(ordenes),
        "total_planes": len(planes),
    }

    print("📱 RESPUESTA DEL API (JSON):")
    print("-" * 30)
    print(f"{{")
    print(f'  "success": {str(respuesta_api["success"]).lower()},')
    print(f'  "mes": {respuesta_api["mes"]},')
    print(f'  "anio": {respuesta_api["anio"]},')
    print(f'  "total_ordenes": {respuesta_api["total_ordenes"]},')
    print(f'  "total_planes": {respuesta_api["total_planes"]},')
    print(f'  "eventos": [')

    for i, evento in enumerate(eventos):
        print(f"    {{")
        print(f'      "id": "{evento["id"]}",')
        print(f'      "title": "{evento["title"]}",')
        print(f'      "description": "{evento["description"]}",')
        print(f'      "start": "{evento["start"]}",')
        print(f'      "backgroundColor": "{evento["backgroundColor"]}",')
        print(f'      "tipo": "{evento["tipo"]}"')
        if i < len(eventos) - 1:
            print(f"    }},")
        else:
            print(f"    }}")

    print(f"  ]")
    print(f"}}")
    print()

    # 6. Cómo se verá en el calendario
    print("👀 CÓMO SE VERÁ EN EL CALENDARIO:")
    print("-" * 35)

    if eventos:
        for evento in eventos:
            if evento["tipo"] == "orden":
                icono = "🔧"
                tipo_desc = "Orden de trabajo"
            else:
                icono = "📅"
                tipo_desc = "Plan de mantenimiento"

            fecha_obj = datetime.strptime(evento["start"][:19], "%Y-%m-%d %H:%M:%S")

            print(f"   {icono} {evento['title']}")
            print(f"      📅 {fecha_obj.strftime('%A %d/%m %H:%M')}")
            print(f"      📝 {evento['description']}")
            print(f"      🎨 Color: {evento['backgroundColor']}")
            print(f"      🏷️  Tipo: {tipo_desc}")
            print()
    else:
        print("   📭 El calendario estará vacío para este mes")

    conn.close()

    # 7. Resumen final
    print("📋 RESUMEN FINAL:")
    print("-" * 20)
    print(f"✅ Los planes SÍ aparecerán en el calendario")
    print(f"📅 Se mostrarán con el prefijo '📅' en el título")
    print(f"🟣 Color púrpura (#6f42c1) para distinguirlos")
    print(f"🔮 Indican cuándo se generarán automáticamente")
    print(
        f"📊 Este mes: {len(ordenes)} órdenes + {len(planes)} planes = {len(eventos)} eventos"
    )


if __name__ == "__main__":
    simular_api_calendario()
