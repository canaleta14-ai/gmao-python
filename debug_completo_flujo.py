"""
Debug completo del flujo de calcular_proxima_ejecucion
"""

import os
import sys
from datetime import datetime

# Configurar la aplicación Flask
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")

from app import create_app


def debug_completo():
    """Debug completo paso a paso"""
    app = create_app()

    with app.app_context():
        from app.controllers.planes_controller import calcular_proxima_ejecucion

        fecha_base = datetime.now()
        configuracion = {
            "tipo": "semanal",
            "dias_semana": ["lunes"],
            "intervalo_semanas": 1,
        }

        print("🔍 DEBUG COMPLETO")
        print("=" * 50)
        print(f"📅 Fecha base: {fecha_base.strftime('%Y-%m-%d %A')}")
        print(f"⚙️ Configuración: {configuracion}")
        print()

        # Interceptar la función para agregar más debug
        resultado = calcular_proxima_ejecucion(configuracion, fecha_base)

        print()
        print("=" * 50)
        print(f"🎯 RESULTADO FINAL: {resultado.strftime('%Y-%m-%d %A')}")

        return resultado


if __name__ == "__main__":
    debug_completo()
