#!/usr/bin/env python3
"""
Script para eliminar únicamente artículos FIFO del inventario
"""
import os
import sqlite3


def eliminar_solo_articulos_fifo():
    """Eliminar solo los artículos FIFO del inventario"""
    print("🗑️  === ELIMINANDO ARTÍCULOS FIFO ===")

    db_path = "instance/database.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar artículos FIFO antes de eliminar
        print("\n📊 Artículos FIFO a eliminar:")
        cursor.execute(
            "SELECT codigo, descripcion FROM inventario WHERE codigo LIKE 'FIFO%'"
        )
        articulos = cursor.fetchall()

        if not articulos:
            print("✅ No hay artículos FIFO para eliminar")
            conn.close()
            return True

        for codigo, descripcion in articulos:
            print(f"   • {codigo}: {descripcion or 'Sin descripción'}")

        # Confirmar eliminación
        print(f"\n⚠️  ¿Eliminar {len(articulos)} artículos FIFO?")
        respuesta = input("   Escribe 'SI' para confirmar: ").strip().upper()

        if respuesta != "SI":
            print("❌ Operación cancelada")
            conn.close()
            return False

        # Eliminar artículos FIFO
        print("\n🗑️  Eliminando artículos FIFO...")
        cursor.execute("DELETE FROM inventario WHERE codigo LIKE 'FIFO%'")
        eliminados = cursor.rowcount

        conn.commit()
        print(f"✅ {eliminados} artículos FIFO eliminados")

        # Verificar que se eliminaron
        cursor.execute("SELECT COUNT(*) FROM inventario WHERE codigo LIKE 'FIFO%'")
        restantes = cursor.fetchone()[0]

        if restantes == 0:
            print("🎉 ¡Eliminación completada con éxito!")
            print("💡 El sistema FIFO sigue disponible para artículos reales")
        else:
            print(f"⚠️  Aún quedan {restantes} artículos FIFO")

        conn.close()
        return restantes == 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🧹 ELIMINADOR SIMPLE DE ARTÍCULOS FIFO")
    print("=" * 40)

    exito = eliminar_solo_articulos_fifo()

    if exito:
        print("\n✅ RESULTADO: Artículos FIFO eliminados correctamente")
        print("   • Sistema FIFO limpio")
        print("   • Listo para artículos reales")
    else:
        print("\n❌ RESULTADO: No se pudieron eliminar todos los artículos")
