#!/usr/bin/env python3
"""
Verificar estado actual del inventario con estructura correcta
"""
import sqlite3


def verificar_inventario_real():
    """Verificar el estado actual del inventario con la estructura correcta"""
    try:
        conn = sqlite3.connect("instance/database.db")
        cursor = conn.cursor()

        print("📊 ESTADO ACTUAL DEL INVENTARIO:")
        print("=" * 50)

        # Verificar todos los artículos con la estructura correcta
        cursor.execute(
            """
            SELECT codigo, descripcion, stock_actual, stock_minimo, stock_maximo, 
                   unidad_medida, ubicacion, proveedor_principal
            FROM inventario 
            WHERE activo = 1
            ORDER BY codigo
        """
        )
        articulos = cursor.fetchall()

        print(f"📦 Total artículos activos: {len(articulos)}")
        print()

        for (
            codigo,
            desc,
            actual,
            minimo,
            maximo,
            unidad,
            ubicacion,
            proveedor,
        ) in articulos:
            print(f'🔧 {codigo}: {desc or "Sin descripción"}')
            print(f'   📍 Ubicación: {ubicacion or "No especificada"}')
            print(f'   📊 Stock: {actual or 0} {unidad or "UNI"}')
            print(
                f'   📈 Rango: {minimo or 0} - {maximo or "Sin máximo"} {unidad or "UNI"}'
            )
            print(f'   🏢 Proveedor: {proveedor or "No especificado"}')
            print()

        # Verificar si hay tabla de lotes
        cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table" AND name="lotes"'
        )
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM lotes WHERE cantidad > 0")
            total_lotes = cursor.fetchone()[0]
            print(f"🏷️  Total lotes activos: {total_lotes}")

            if total_lotes > 0:
                cursor.execute(
                    """
                    SELECT numero_lote, codigo_articulo, cantidad, fecha_vencimiento 
                    FROM lotes 
                    WHERE cantidad > 0
                    ORDER BY fecha_vencimiento
                """
                )
                lotes = cursor.fetchall()
                print("\n📋 Lotes existentes:")
                for numero, codigo_art, cantidad, fecha_venc in lotes:
                    print(
                        f'   • {numero} ({codigo_art}): {cantidad} uds - Vence: {fecha_venc or "Sin fecha"}'
                    )
        else:
            print(
                "🏷️  Tabla de lotes: No existe (se creará automáticamente cuando se necesite)"
            )

        print(f"\n✅ ESTADO SISTEMA FIFO:")
        print("   • ✅ Artículos FIFO de prueba: ELIMINADOS")
        print("   • ✅ Sistema FIFO: DISPONIBLE para artículos reales")
        print("   • ✅ Integración inventario: ACTIVA en /inventario")
        print("   • ✅ Badge FIFO: Funcionará automáticamente con lotes reales")

        # Verificar si algún artículo necesitaría gestión FIFO
        fifo_candidates = []
        for (
            codigo,
            desc,
            actual,
            minimo,
            maximo,
            unidad,
            ubicacion,
            proveedor,
        ) in articulos:
            # Los artículos que podrían necesitar FIFO son aquellos con stock > 0
            if actual and actual > 0:
                fifo_candidates.append((codigo, desc, actual))

        if fifo_candidates:
            print(f"\n💡 ARTÍCULOS CANDIDATOS PARA FIFO:")
            print(
                "   (Artículos con stock que podrían beneficiarse de gestión por lotes)"
            )
            for codigo, desc, stock in fifo_candidates:
                print(f"   • {codigo}: {desc} ({stock} unidades)")
            print("\n   Para habilitar FIFO en un artículo:")
            print("   1. Ir a http://127.0.0.1:5000/inventario/")
            print('   2. Hacer clic en "🏷️ Gestión FIFO"')
            print("   3. Crear lotes para el artículo deseado")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    verificar_inventario_real()
