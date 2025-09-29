#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis específico del problema de frecuencia del plan PM-2025-0001
"""

from datetime import datetime, timedelta
import ast


def analizar_problema():
    print("🔍 ANÁLISIS DEL PROBLEMA PM-2025-0001")
    print("=" * 50)

    # Datos del plan desde la BD
    datos_plan = {
        "codigo": "PM-2025-0001",
        "nombre": "Horno",
        "dias_semana": "['lunes', 'miercoles', 'viernes']",
        "proxima_ejecucion": "2025-10-05 13:17:47.838323",
        "tipo_frecuencia": "semanal",
        "generacion_automatica": 0,
    }

    print(f"Plan: {datos_plan['codigo']} - {datos_plan['nombre']}")
    print(f"Días configurados: {datos_plan['dias_semana']}")
    print(f"Próxima ejecución BD: {datos_plan['proxima_ejecucion']}")
    print(
        f"Generación automática: {datos_plan['generacion_automatica']} (❌ DESHABILITADA)"
    )

    # Parsear días de la semana
    try:
        dias_lista = ast.literal_eval(datos_plan["dias_semana"])
        print(f"Días parseados: {dias_lista}")
    except Exception as e:
        print(f"Error parseando días: {e}")
        return

    # Mapear días a números
    mapeo_dias = {
        "lunes": 0,
        "martes": 1,
        "miércoles": 2,
        "miercoles": 2,
        "jueves": 3,
        "viernes": 4,
        "sábado": 5,
        "domingo": 6,
    }

    dias_numericos = []
    for dia in dias_lista:
        dia_lower = dia.lower().strip()
        if dia_lower in mapeo_dias:
            dias_numericos.append(mapeo_dias[dia_lower])
        else:
            print(f"⚠️  Día no reconocido: '{dia}'")

    dias_numericos.sort()
    print(f"Días numéricos: {dias_numericos} (0=Lunes, 4=Viernes)")

    # Nombres de días para mostrar
    nombres_dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]
    dias_nombres = [nombres_dias[d] for d in dias_numericos]
    print(f"Días objetivo: {', '.join(dias_nombres)}")

    # Analizar fecha actual en BD
    try:
        fecha_bd = datetime.strptime(
            datos_plan["proxima_ejecucion"][:19], "%Y-%m-%d %H:%M:%S"
        )
        print(f"\n📅 FECHA PROBLEMÁTICA EN BD:")
        print(f"Fecha: {fecha_bd.strftime('%A %d/%m/%Y %H:%M')}")
        print(f"Día semana: {fecha_bd.weekday()} ({nombres_dias[fecha_bd.weekday()]})")

        # Verificar si el día está en la lista objetivo
        if fecha_bd.weekday() in dias_numericos:
            print(
                f"✅ El día {nombres_dias[fecha_bd.weekday()]} SÍ está en los días objetivo"
            )
        else:
            print(
                f"❌ El día {nombres_dias[fecha_bd.weekday()]} NO está en los días objetivo"
            )

    except Exception as e:
        print(f"Error parseando fecha BD: {e}")
        return

    # Calcular qué debería ser la próxima fecha
    print(f"\n🧮 CÁLCULO CORRECTO DESDE HOY:")
    hoy = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    print(f"Hoy: {hoy.strftime('%A %d/%m/%Y %H:%M')} (día {hoy.weekday()})")

    proxima_correcta = calcular_proxima_ejecucion(hoy, dias_numericos)
    print(
        f"Próxima correcta: {proxima_correcta.strftime('%A %d/%m/%Y %H:%M')} (día {proxima_correcta.weekday()})"
    )

    # Comparar fechas
    print(f"\n🔍 COMPARACIÓN:")
    print(f"BD dice:      {fecha_bd.strftime('%A %d/%m/%Y')} ({fecha_bd.weekday()})")
    print(
        f"Debería ser:  {proxima_correcta.strftime('%A %d/%m/%Y')} ({proxima_correcta.weekday()})"
    )

    diferencia_dias = (fecha_bd.date() - proxima_correcta.date()).days
    if diferencia_dias == 0:
        print(f"✅ Las fechas COINCIDEN")
    else:
        print(f"❌ DISCREPANCIA: {abs(diferencia_dias)} días de diferencia")
        if diferencia_dias > 0:
            print(f"   BD está {diferencia_dias} días ADELANTE")
        else:
            print(f"   BD está {abs(diferencia_dias)} días ATRÁS")

    # Teorías sobre el problema
    print(f"\n💡 POSIBLES CAUSAS:")
    print(
        f"1. ❌ Generación automática DESHABILITADA (valor: {datos_plan['generacion_automatica']})"
    )
    print(f"2. 🔄 El cálculo se hizo desde una fecha base incorrecta")
    print(f"3. 🐛 Bug en la lógica de cálculo semanal")
    print(f"4. 📅 La fecha se calculó manualmente y no se actualizó")


def calcular_proxima_ejecucion(fecha_base, dias_objetivo):
    """
    Calcula la próxima ejecución para días específicos de la semana
    """
    dias_ordenados = sorted(dias_objetivo)
    dia_actual = fecha_base.weekday()

    # Buscar siguiente día en la semana actual
    for dia in dias_ordenados:
        if dia > dia_actual:
            diferencia = dia - dia_actual
            return fecha_base + timedelta(days=diferencia)

    # Si no hay más días esta semana, ir a la próxima semana
    primer_dia_proxima = dias_ordenados[0]
    dias_hasta_lunes = 7 - dia_actual  # Días hasta el lunes próximo
    dias_desde_lunes = primer_dia_proxima  # Días desde lunes hasta objetivo

    total_dias = dias_hasta_lunes + dias_desde_lunes
    return fecha_base + timedelta(days=total_dias)


if __name__ == "__main__":
    analizar_problema()
