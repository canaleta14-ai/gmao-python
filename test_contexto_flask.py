#!/usr/bin/env python3
"""
Prueba real con el contexto de la aplicación Flask
"""

from app.factory import create_app
from app.controllers.planes_controller import calcular_proxima_ejecucion, crear_plan
from datetime import datetime

app = create_app()

with app.app_context():
    # Datos de prueba exactos como los enviaría el navegador
    data = {
        "nombre": "Test Miercoles Real",
        "descripcion": "Plan de prueba para miércoles",
        "activo_id": 1,
        "frecuencia": "Semanal",
        "tipo_frecuencia": "semanal",
        "intervalo_semanas": 1,
        "dias_semana": ["miercoles"],
    }

    print("=== PRUEBA CON CONTEXTO FLASK ===")
    print(f"Fecha actual: {datetime.now()}")
    print(f"Datos: {data}")

    try:
        # Probar solo el cálculo
        proxima = calcular_proxima_ejecucion(data)
        print(f"Próxima ejecución calculada: {proxima}")
        print(f"Día de la semana: {proxima.weekday()} (2 = miércoles)")

        # Probar creación completa
        print("\n=== CREANDO PLAN COMPLETO ===")
        plan = crear_plan(data)
        print(f"Plan creado: ID={plan.id}, Código={plan.codigo_plan}")
        print(f"Próxima ejecución guardada: {plan.proxima_ejecucion}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
