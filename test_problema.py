#!/usr/bin/env python3
"""
Script para probar con la fecha/hora exacta del problema
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.factory import create_app
from app.controllers.planes_controller import calcular_proxima_ejecucion
from datetime import datetime


def test_problema_exacto():
    app = create_app()

    with app.app_context():
        # Simular la situación exacta del problema
        # Domingo 22 de septiembre alrededor de las 7:56 PM
        fecha_exacta = datetime(2025, 9, 22, 19, 56, 0)

        test_data = {
            "tipo_frecuencia": "semanal",
            "intervalo_semanas": 1,
            "dias_semana": ["miercoles"],
        }

        print(f"=== PROBLEMA EXACTO ===")
        print(f"Fecha/hora base: {fecha_exacta}")
        print(
            f"Día de la semana: {fecha_exacta.weekday()} ({fecha_exacta.strftime('%A')})"
        )

        proxima = calcular_proxima_ejecucion(test_data, fecha_exacta)
        print(f"Resultado: {proxima}")
        print(f"Día calculado: {proxima.weekday()} ({proxima.strftime('%A')})")
        print(f"Fecha: {proxima.strftime('%d/%m/%Y')}")

        # Verificar manualmente
        print(f"\n=== VERIFICACIÓN MANUAL ===")
        print(f"Hoy es domingo (22/09), día de la semana: {fecha_exacta.weekday()}")
        print(f"Miércoles es día de la semana: 2")
        print(f"Días hasta el próximo miércoles: {2 - fecha_exacta.weekday()}")

        if 2 > fecha_exacta.weekday():
            print("El miércoles de esta semana aún no ha pasado")
            dias_hasta = 2 - fecha_exacta.weekday()
            fecha_esperada = fecha_exacta + timedelta(days=dias_hasta)
            print(f"Fecha esperada: {fecha_esperada.strftime('%d/%m/%Y (%A)')}")
        else:
            print("El miércoles de esta semana ya pasó, ir al próximo")
            dias_hasta = (7 - fecha_exacta.weekday()) + 2
            fecha_esperada = fecha_exacta + timedelta(days=dias_hasta)
            print(f"Fecha esperada: {fecha_esperada.strftime('%d/%m/%Y (%A)')}")


if __name__ == "__main__":
    from datetime import timedelta

    test_problema_exacto()
