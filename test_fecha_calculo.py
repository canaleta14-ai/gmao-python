#!/usr/bin/env python3
"""
Script para probar la función de cálculo de próxima ejecución
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.factory import create_app
from app.controllers.planes_controller import calcular_proxima_ejecucion
from datetime import datetime


def test_calcular_fechas():
    app = create_app()

    with app.app_context():
        # Probar el caso que reporta el usuario:
        # Tipo mensual, día específico de la semana, cada 1 mes, semana 1, sábado

        test_data = {
            "tipo_frecuencia": "mensual",
            "tipo_mensual": "dia_semana_mes",
            "intervalo_meses": 1,
            "semana_mes": 1,
            "dia_semana_mes": "sabado",
        }

        fecha_base = datetime(2025, 9, 22)  # Fecha actual del usuario

        print(f"Fecha base: {fecha_base.strftime('%A, %d de %B de %Y')}")
        print(f"Configuración: {test_data}")

        try:
            proxima_fecha = calcular_proxima_ejecucion(test_data, fecha_base)
            print(
                f"Próxima ejecución calculada: {proxima_fecha.strftime('%A, %d de %B de %Y')}"
            )

            # Verificar que es el primer sábado del próximo mes
            esperado_mes = 10 if fecha_base.month < 12 else 1
            esperado_año = (
                fecha_base.year if fecha_base.month < 12 else fecha_base.year + 1
            )

            print(f"Mes esperado: {esperado_mes}, Año esperado: {esperado_año}")
            print(
                f"Mes calculado: {proxima_fecha.month}, Año calculado: {proxima_fecha.year}"
            )
            print(f"Día de la semana: {proxima_fecha.strftime('%A')}")

            # Verificar que es sábado
            if proxima_fecha.weekday() == 5:  # 5 = sábado
                print("✅ Correcto: Es un sábado")
            else:
                print("❌ Error: No es un sábado")

            # Verificar que es la primera semana
            dia_del_mes = proxima_fecha.day
            if 1 <= dia_del_mes <= 7:
                print("✅ Correcto: Es la primera semana del mes")
            else:
                print(f"❌ Error: Día {dia_del_mes} no está en la primera semana")

        except Exception as e:
            print(f"❌ Error al calcular fecha: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_calcular_fechas()
