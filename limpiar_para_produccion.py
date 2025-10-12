#!/usr/bin/env python3
"""
Script para limpiar completamente el inventario para producción
"""
import sqlite3


def limpiar_inventario_completo():
    """Eliminar todos los artículos del inventario para empezar limpio"""
    print("🧹 === LIMPIEZA COMPLETA PARA PRODUCCIÓN ===")

    try:
        conn = sqlite3.connect("instance/database.db")
        cursor = conn.cursor()

        # Verificar qué artículos hay actualmente
        cursor.execute(
            "SELECT codigo, descripcion, stock_actual FROM inventario WHERE activo = 1"
        )
        articulos = cursor.fetchall()

        if not articulos:
            print("✅ El inventario ya está vacío")
            conn.close()
            return True

        print(f"\n📊 Artículos actuales a eliminar:")
        for codigo, desc, stock in articulos:
            print(f"   • {codigo}: {desc} (Stock: {stock})")

        print(f"\n⚠️  ¿Eliminar TODOS los {len(articulos)} artículos del inventario?")
        print("   Esta acción preparará el sistema para producción limpia.")
        respuesta = input("   Escribe 'PRODUCCION' para confirmar: ").strip().upper()

        if respuesta != "PRODUCCION":
            print("❌ Operación cancelada")
            conn.close()
            return False

        print(f"\n🗑️  Eliminando artículos...")

        # Eliminar lotes asociados (si existen)
        cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table" AND name="lotes"'
        )
        if cursor.fetchone():
            cursor.execute("DELETE FROM lotes")
            lotes_eliminados = cursor.rowcount
            print(f"   ✅ {lotes_eliminados} lotes eliminados")

        # Eliminar movimientos de inventario (si existen)
        cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table" AND name="movimientos_inventario"'
        )
        if cursor.fetchone():
            cursor.execute("DELETE FROM movimientos_inventario")
            movimientos_eliminados = cursor.rowcount
            print(f"   ✅ {movimientos_eliminados} movimientos eliminados")

        # Eliminar artículos del inventario
        cursor.execute("DELETE FROM inventario")
        articulos_eliminados = cursor.rowcount
        print(f"   ✅ {articulos_eliminados} artículos eliminados")

        conn.commit()

        # Verificar que está limpio
        cursor.execute("SELECT COUNT(*) FROM inventario")
        restantes = cursor.fetchone()[0]

        if restantes == 0:
            print(f"\n🎉 ¡SISTEMA LIMPIO PARA PRODUCCIÓN!")
            print("   • Inventario: 0 artículos")
            print("   • Lotes: 0 registros")
            print("   • Movimientos: 0 registros")
            print("   • Sistema FIFO: Disponible")
            print("   • Integración: Activa en /inventario")
        else:
            print(f"⚠️  Aún quedan {restantes} artículos")

        conn.close()
        return restantes == 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🏭 PREPARACIÓN PARA PRODUCCIÓN")
    print("=" * 40)
    print("Este script eliminará TODOS los artículos del inventario")
    print("para dejar el sistema completamente limpio para producción.")
    print("=" * 40)

    exito = limpiar_inventario_completo()

    if exito:
        print("\n✅ RESULTADO: Sistema listo para producción")
        print("💡 Próximos pasos:")
        print("   1. Agregar artículos reales de producción")
        print("   2. Usar botón eliminar cuando sea necesario")
        print("   3. Sistema FIFO disponible para lotes reales")
    else:
        print("\n❌ RESULTADO: No se pudo completar la limpieza")
