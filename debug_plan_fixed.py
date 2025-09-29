#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico específico para el plan PM-2025-0001
Analiza por qué muestra 05/10/2025 en lugar de la fecha esperada

Autor: Debug Assistant
Fecha: 2025-09-28
"""

import sqlite3
from datetime import datetime, timedelta
import json


def debug_plan_pm_2025_0001():
    """
    Debuggea específicamente el plan PM-2025-0001
    """
    print("🔍 DIAGNÓSTICO DEL PLAN PM-2025-0001")
    print("=" * 50)

    # Conectar a la base de datos
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    # Obtener los datos completos del plan PM-2025-0001
    print("\n📋 DATOS DEL PLAN EN LA BASE DE DATOS:")
    cursor.execute(
        """
        SELECT id, codigo_plan, nombre, frecuencia, frecuencia_dias,
               ultima_ejecucion, proxima_ejecucion, estado, descripcion,
               tipo_frecuencia, intervalo_semanas, dias_semana,
               activo_id, generacion_automatica
        FROM plan_mantenimiento 
        WHERE codigo_plan = 'PM-2025-0001'
    """
    )

    plan = cursor.fetchone()
    if not plan:
        print("❌ Plan PM-2025-0001 no encontrado en la base de datos")
        return

    columns = [
        "id",
        "codigo_plan",
        "nombre",
        "frecuencia",
        "frecuencia_dias",
        "ultima_ejecucion",
        "proxima_ejecucion",
        "estado",
        "descripcion",
        "tipo_frecuencia",
        "intervalo_semanas",
        "dias_semana",
        "activo_id",
        "generacion_automatica",
    ]

    plan_dict = dict(zip(columns, plan))

    print(f"ID: {plan_dict['id']}")
    print(f"Código: {plan_dict['codigo_plan']}")
    print(f"Nombre: {plan_dict['nombre']}")
    print(f"Descripción: {plan_dict['descripcion']}")
    print(f"Frecuencia: {plan_dict['frecuencia']}")
    print(f"Frecuencia días: {plan_dict['frecuencia_dias']}")
    print(f"Tipo frecuencia: {plan_dict['tipo_frecuencia']}")
    print(f"Intervalo semanas: {plan_dict['intervalo_semanas']}")
    print(f"Días semana: {plan_dict['dias_semana']}")
    print(f"Última ejecución: {plan_dict['ultima_ejecucion']}")
    print(f"Próxima ejecución: {plan_dict['proxima_ejecucion']}")
    print(f"Estado: {plan_dict['estado']}")
    print(f"Generación automática: {plan_dict['generacion_automatica']}")
    print(f"Activo ID: {plan_dict['activo_id']}")

    # Analizar la fecha problemática
    print("\n🎯 ANÁLISIS DE LA FECHA PROBLEMÁTICA:")
    print(f"Fecha actual en BD: {plan_dict['proxima_ejecucion']}")

    if plan_dict["proxima_ejecucion"]:
        try:
            fecha_bd = datetime.strptime(
                plan_dict["proxima_ejecucion"], "%Y-%m-%d %H:%M:%S"
            )
            print(f"Fecha parseada: {fecha_bd.strftime('%A %d/%m/%Y')}")
            print(f"Día de la semana: {fecha_bd.weekday()} (0=Lunes)")
        except ValueError as e:
            print(f"Error parseando fecha: {e}")

    # Analizar la frecuencia semanal
    print("\n🔄 ANÁLISIS DE FRECUENCIA SEMANAL:")

    if plan_dict["tipo_frecuencia"] == "semanal" and plan_dict["dias_semana"]:
        try:
            dias_json = plan_dict["dias_semana"]
            print(f"Días configurados (raw): {dias_json}")

            # Si es JSON, parsearlo
            if dias_json.startswith("[") or dias_json.startswith("{"):
                dias_data = json.loads(dias_json)
                print(f"Días parseados (JSON): {dias_data}")
            else:
                # Si es string simple
                dias_data = dias_json.split(",")
                print(f"Días parseados (split): {dias_data}")

            # Mapeo de días
            dias_nombres = {
                "lunes": 0,
                "martes": 1,
                "miércoles": 2,
                "jueves": 3,
                "viernes": 4,
                "sábado": 5,
                "domingo": 6,
            }

            dias_numericos = []
            for dia in dias_data:
                dia_clean = dia.strip().lower()
                if dia_clean in dias_nombres:
                    dias_numericos.append(dias_nombres[dia_clean])

            print(f"Días numéricos (0=Lunes): {sorted(dias_numericos)}")

            # Calcular próxima ejecución desde hoy
            hoy = datetime.now()
            print(f"\n📅 CÁLCULO DESDE HOY ({hoy.strftime('%A %d/%m/%Y')}):")

            proxima = calcular_proxima_semanal(hoy, dias_numericos)
            print(
                f"  → Próxima calculada: {proxima.strftime('%A %d/%m/%Y')} ({proxima.weekday()})"
            )

            # Comparar con la BD
            if plan_dict["proxima_ejecucion"]:
                fecha_bd = datetime.strptime(
                    plan_dict["proxima_ejecucion"], "%Y-%m-%d %H:%M:%S"
                )
                if proxima.date() != fecha_bd.date():
                    print(
                        f"  ❌ DISCREPANCIA: BD={fecha_bd.strftime('%d/%m/%Y')}, Calculada={proxima.strftime('%d/%m/%Y')}"
                    )
                else:
                    print(f"  ✅ COINCIDE: Ambas fechas son iguales")

        except Exception as e:
            print(f"❌ Error analizando frecuencia: {e}")

    # Verificar órdenes de trabajo relacionadas
    print("\n📝 ÓRDENES DE TRABAJO RELACIONADAS:")
    cursor.execute(
        """
        SELECT id, titulo, fecha_creacion, fecha_programada, estado
        FROM orden_trabajo 
        WHERE plan_mantenimiento_id = ?
        ORDER BY fecha_creacion DESC
        LIMIT 5
    """,
        (plan_dict["id"],),
    )

    ordenes = cursor.fetchall()
    if ordenes:
        for orden in ordenes:
            print(
                f"  Orden {orden[0]}: {orden[1]} - {orden[2]} → {orden[3]} ({orden[4]})"
            )
    else:
        print("  No hay órdenes de trabajo registradas")

    # Cerrar conexión
    conn.close()
    print("\n" + "=" * 50)


def calcular_proxima_semanal(fecha_base, dias_semana):
    """
    Replica la lógica del controlador para calcular próxima ejecución semanal
    """
    dias_ordenados = sorted(dias_semana)
    fecha_actual = fecha_base.replace(hour=6, minute=0, second=0, microsecond=0)
    dia_actual = fecha_actual.weekday()

    print(f"    Fecha base: {fecha_actual.strftime('%A %d/%m/%Y')} (día {dia_actual})")
    print(f"    Días objetivo: {dias_ordenados}")

    # Buscar el siguiente día válido en la semana actual
    for dia in dias_ordenados:
        if dia > dia_actual:
            dias_hasta = dia - dia_actual
            proxima_fecha = fecha_actual + timedelta(days=dias_hasta)
            print(f"    Encontrado día {dia} en {dias_hasta} días")
            return proxima_fecha

    # Si no hay días válidos en la semana actual, ir a la siguiente semana
    if dias_ordenados:
        primer_dia_siguiente = dias_ordenados[0]
        dias_hasta_siguiente_semana = 7 - dia_actual
        dias_adicionales = primer_dia_siguiente
        total_dias = dias_hasta_siguiente_semana + dias_adicionales

        proxima_fecha = fecha_actual + timedelta(days=total_dias)
        print(
            f"    Ir a siguiente semana: {dias_hasta_siguiente_semana} + {dias_adicionales} = {total_dias} días"
        )

        return proxima_fecha

    # Fallback
    return fecha_actual + timedelta(days=1)


if __name__ == "__main__":
    debug_plan_pm_2025_0001()
