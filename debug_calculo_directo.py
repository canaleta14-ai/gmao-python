"""
Debug directo del cálculo semanal
"""

import os
import sys
from datetime import datetime

# Configurar la aplicación Flask
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")


def test_calculo_manual():
    """Probar directamente el cálculo"""
    fecha_base = datetime.now()
    print(f"📅 Fecha base: {fecha_base.strftime('%Y-%m-%d %A')}")

    # Simular configuración semanal para lunes
    configuracion = {
        "tipo": "semanal",
        "dias_semana": ["lunes"],
        "intervalo_semanas": 1,
    }

    from app.controllers.planes_controller import calcular_proxima_ejecucion

    try:
        proxima = calcular_proxima_ejecucion(configuracion, fecha_base)
        print(f"✅ Próxima ejecución: {proxima.strftime('%Y-%m-%d %A')}")
        return proxima
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_calculo_manual()
