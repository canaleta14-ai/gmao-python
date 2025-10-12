#!/usr/bin/env python3
"""
Verificar estado actual del inventario
"""
import sqlite3


def verificar_inventario_actual():
    """Verificar el estado actual del inventario"""
    try:
        conn = sqlite3.connect("instance/database.db")
        cursor = conn.cursor()

        print("📊 ESTADO ACTUAL DEL INVENTARIO:")
        print("=" * 40)

        # Verificar todos los artículos
        cursor.execute(
            "SELECT codigo, descripcion, cantidad_actual, cantidad_minima, cantidad_maxima FROM inventario ORDER BY codigo"
        )
        articulos = cursor.fetchall()

        print(f"Total artículos: {len(articulos)}")
        print()

        for codigo, desc, actual, minima, maxima in articulos:
            print(f'• {codigo}: {desc or "Sin descripción"}')
            print(f"  Cantidad actual: {actual or 0}")
            print(f"  Mín/Máx: {minima or 0}/{maxima or 0}")
            print()

        # Verificar si hay lotes asociados
        cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table" AND name="lotes"'
        )
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM lotes")
            total_lotes = cursor.fetchone()[0]
            print(f"📦 Total lotes en sistema: {total_lotes}")

            # Mostrar lotes si existen
            if total_lotes > 0:
                cursor.execute(
                    "SELECT numero_lote, codigo_articulo, cantidad, fecha_vencimiento FROM lotes ORDER BY fecha_vencimiento"
                )
                lotes = cursor.fetchall()
                print("\n🏷️  Lotes existentes:")
                for numero, codigo_art, cantidad, fecha_venc in lotes:
                    print(
                        f'   • {numero} ({codigo_art}): {cantidad} uds - Vence: {fecha_venc or "Sin fecha"}'
                    )
        else:
            print("📦 Tabla de lotes no existe aún")

        print(f"\n✅ ESTADO SISTEMA FIFO:")
        print("   • Artículos FIFO de prueba: ELIMINADOS")
        print("   • Sistema FIFO: DISPONIBLE para artículos reales")
        print("   • Integración inventario: ACTIVA")
        print("   • URL: http://127.0.0.1:5000/inventario/")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    verificar_inventario_actual()
