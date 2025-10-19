"""
Script de prueba para verificar las estadísticas FIFO
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.factory import create_app
from app.controllers.estadisticas_controller import obtener_estadisticas
import json


def test_estadisticas():
    """Probar el endpoint de estadísticas"""
    print("=" * 70)
    print("🧪 PRUEBA DE ESTADÍSTICAS FIFO")
    print("=" * 70)
    print()

    # Crear aplicación
    app = create_app()

    with app.app_context():
        try:
            # Obtener estadísticas
            print("📊 Obteniendo estadísticas...")
            stats = obtener_estadisticas()

            print("\n✅ Estadísticas obtenidas exitosamente\n")

            # Mostrar estadísticas generales
            print("📋 Órdenes de Trabajo:")
            print(f"   - Por estado: {stats.get('ordenes_por_estado', {})}")
            print(f"   - Última semana: {stats.get('ordenes_ultima_semana', 0)}")
            print()

            print("🏭 Activos:")
            print(f"   - Por estado: {stats.get('activos_por_estado', {})}")
            print(f"   - Total: {stats.get('total_activos', 0)}")
            print()

            # Mostrar estadísticas FIFO
            if "fifo_stats" in stats:
                fifo = stats["fifo_stats"]
                print("📦 ESTADÍSTICAS FIFO:")
                print(f"   - Total de lotes: {fifo.get('total_lotes', 0)}")
                print(f"   - Lotes disponibles: {fifo.get('lotes_disponibles', 0)}")
                print(f"   - Artículos con lotes: {fifo.get('articulos_con_lotes', 0)}")
                print(f"   - Total artículos: {fifo.get('total_articulos', 0)}")
                print(f"   - Cobertura: {fifo.get('porcentaje_cobertura', 0)}%")
                print(
                    f"   - Próximos a vencer (30 días): {fifo.get('lotes_proximos_vencer', 0)}"
                )
                print(f"   - Lotes vencidos: {fifo.get('lotes_vencidos', 0)}")
                print(
                    f"   - Valor total inventario: ${fifo.get('valor_total_inventario', 0):,.2f}"
                )
                print()

                # Verificar coherencia
                if fifo["total_lotes"] > 0:
                    print("✅ Sistema FIFO configurado correctamente")
                else:
                    print("⚠️ No hay lotes en el sistema")

                if fifo["porcentaje_cobertura"] == 100:
                    print(
                        "✅ Cobertura completa: Todos los artículos con stock tienen lotes"
                    )
                elif fifo["porcentaje_cobertura"] > 0:
                    print(
                        f"⚠️ Cobertura parcial: {fifo['porcentaje_cobertura']}% de artículos con lotes"
                    )
                else:
                    print("❌ Sin cobertura: Ningún artículo tiene lotes")

            else:
                print("❌ No se encontraron estadísticas FIFO en la respuesta")

            print()
            print("=" * 70)
            print("📄 JSON COMPLETO:")
            print("=" * 70)
            print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))

        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_estadisticas()
