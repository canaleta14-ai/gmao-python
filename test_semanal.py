#!/usr/bin/env python3
"""
Script para probar el cálculo de fechas semanales
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.factory import create_app
from app.controllers.planes_controller import calcular_proxima_ejecucion
from datetime import datetime


def test_frecuencia_semanal():
    app = create_app()

    with app.app_context():
        # Caso reportado: miércoles desde 22 de septiembre de 2025 (domingo)
        # Debería dar 01/10/2025 (primer miércoles después del domingo 22/09)

        test_data = {
            "tipo_frecuencia": "semanal",
            "intervalo_semanas": 1,
            "dias_semana": ["miercoles"],
        }

        fecha_base = datetime(2025, 9, 22)  # Domingo 22 de septiembre

        print(f"=== PRUEBA FRECUENCIA SEMANAL ===")
        print(f"Fecha base: {fecha_base.strftime('%A, %d de %B de %Y')}")
        print(f"Día de la semana actual: {fecha_base.weekday()} (0=lunes, 6=domingo)")
        print(f"Configuración: {test_data}")

        try:
            proxima_fecha = calcular_proxima_ejecucion(test_data, fecha_base)
            print(f"Próxima ejecución: {proxima_fecha.strftime('%A, %d de %B de %Y')}")
            print(f"Fecha formateada: {proxima_fecha.strftime('%d/%m/%Y')}")

            # Verificaciones
            if proxima_fecha.weekday() == 2:  # 2 = miércoles
                print("✅ Correcto: Es un miércoles")
            else:
                print(f"❌ Error: No es miércoles (día {proxima_fecha.weekday()})")

            # Verificar que es el 1 de octubre
            if proxima_fecha.day == 1 and proxima_fecha.month == 10:
                print("✅ Correcto: Es el 1 de octubre")
            else:
                print(
                    f"❌ Error: Fecha incorrecta {proxima_fecha.day}/{proxima_fecha.month}"
                )

            # Prueba adicional: desde un miércoles
            print(f"\n=== PRUEBA DESDE MIÉRCOLES ===")
            fecha_miercoles = datetime(2025, 9, 24)  # Miércoles 24 septiembre
            print(f"Fecha base: {fecha_miercoles.strftime('%A, %d de %B de %Y')}")

            proxima_desde_miercoles = calcular_proxima_ejecucion(
                test_data, fecha_miercoles
            )
            print(
                f"Próxima ejecución: {proxima_desde_miercoles.strftime('%A, %d de %B de %Y')}"
            )
            print(f"Fecha formateada: {proxima_desde_miercoles.strftime('%d/%m/%Y')}")

            # Debería ser el próximo miércoles (1 octubre)
            if proxima_desde_miercoles.day == 1 and proxima_desde_miercoles.month == 10:
                print("✅ Correcto: Próximo miércoles es 1 octubre")
            else:
                print(
                    f"❌ Error: Debería ser 1 octubre, pero es {proxima_desde_miercoles.strftime('%d/%m/%Y')}"
                )

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_frecuencia_semanal()
