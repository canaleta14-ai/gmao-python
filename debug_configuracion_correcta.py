"""
Debug con la configuración correcta
"""

import os
import sys
from datetime import datetime

# Configurar la aplicación Flask
sys.path.append("c:/gmao - copia")
os.chdir("c:/gmao - copia")

from app import create_app


def debug_configuracion_correcta():
    """Debug con los nombres de campos correctos"""
    app = create_app()

    with app.app_context():
        from app.controllers.planes_controller import calcular_proxima_ejecucion

        fecha_base = datetime.now()

        # Configuración CORRECTA con los nombres que esperan la función
        configuracion_correcta = {
            "tipo_frecuencia": "semanal",  # Era "tipo"
            "dias_semana": ["lunes"],
            "intervalo_semanas": 1,
        }

        print("🔍 DEBUG CON CONFIGURACIÓN CORRECTA")
        print("=" * 50)
        print(f"📅 Fecha base: {fecha_base.strftime('%Y-%m-%d %A')}")
        print(f"⚙️ Configuración CORRECTA: {configuracion_correcta}")
        print()

        resultado = calcular_proxima_ejecucion(configuracion_correcta, fecha_base)

        print()
        print("=" * 50)
        print(f"🎯 RESULTADO FINAL: {resultado.strftime('%Y-%m-%d %A')}")

        return resultado


if __name__ == "__main__":
    debug_configuracion_correcta()
