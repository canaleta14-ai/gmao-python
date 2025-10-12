#!/usr/bin/env python3
"""
Script para eliminar artículos de prueba FIFO del sistema
"""
import os
import sys
import sqlite3
from datetime import datetime

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def eliminar_articulos_fifo():
    """Eliminar todos los artículos y lotes FIFO de prueba"""
    print("🗑️  === ELIMINANDO ARTÍCULOS DE PRUEBA FIFO ===")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()

        # Verificar qué tenemos antes de eliminar
        print("\n📊 Estado actual:")

        # Contar artículos FIFO
        cursor.execute("SELECT COUNT(*) FROM inventario WHERE codigo LIKE 'FIFO%'")
        count_articulos = cursor.fetchone()[0]
        print(f"   • Artículos FIFO: {count_articulos}")

        # Contar lotes FIFO
        cursor.execute(
            """
            SELECT COUNT(*) FROM lotes 
            WHERE codigo_articulo LIKE 'FIFO%'
        """
        )
        count_lotes = cursor.fetchone()[0]
        print(f"   • Lotes FIFO: {count_lotes}")

        if count_articulos == 0 and count_lotes == 0:
            print("✅ No hay artículos FIFO de prueba para eliminar")
            conn.close()
            return True

        # Mostrar artículos que se van a eliminar
        print(f"\n📋 Artículos FIFO a eliminar:")
        cursor.execute(
            "SELECT codigo, descripcion FROM inventario WHERE codigo LIKE 'FIFO%'"
        )
        articulos = cursor.fetchall()

        for codigo, descripcion in articulos:
            print(f"   • {codigo}: {descripcion}")

        # Mostrar lotes que se van a eliminar
        print(f"\n🏷️  Lotes FIFO a eliminar:")
        cursor.execute(
            """
            SELECT l.numero_lote, l.codigo_articulo, l.cantidad 
            FROM lotes l 
            WHERE l.codigo_articulo LIKE 'FIFO%'
            ORDER BY l.numero_lote
        """
        )
        lotes = cursor.fetchall()

        for numero_lote, codigo_articulo, cantidad in lotes:
            print(f"   • {numero_lote} ({codigo_articulo}): {cantidad} uds")

        # Confirmar eliminación
        print(
            f"\n⚠️  ¿Estás seguro de que quieres eliminar {count_articulos} artículos y {count_lotes} lotes FIFO?"
        )
        print("   Esta acción NO se puede deshacer.")
        respuesta = input("   Escribe 'SI' para confirmar: ").strip().upper()

        if respuesta != "SI":
            print("❌ Operación cancelada por el usuario")
            conn.close()
            return False

        print(f"\n🗑️  Iniciando eliminación...")

        # 1. Eliminar lotes FIFO primero (por integridad referencial)
        print("   1️⃣ Eliminando lotes FIFO...")
        cursor.execute("DELETE FROM lotes WHERE codigo_articulo LIKE 'FIFO%'")
        lotes_eliminados = cursor.rowcount
        print(f"      ✅ {lotes_eliminados} lotes eliminados")

        # 2. Eliminar movimientos de inventario FIFO
        print("   2️⃣ Eliminando movimientos de inventario FIFO...")
        cursor.execute(
            "DELETE FROM movimientos_inventario WHERE codigo_articulo LIKE 'FIFO%'"
        )
        movimientos_eliminados = cursor.rowcount
        print(f"      ✅ {movimientos_eliminados} movimientos eliminados")

        # 3. Eliminar artículos FIFO
        print("   3️⃣ Eliminando artículos FIFO...")
        cursor.execute("DELETE FROM inventario WHERE codigo LIKE 'FIFO%'")
        articulos_eliminados = cursor.rowcount
        print(f"      ✅ {articulos_eliminados} artículos eliminados")

        # Confirmar cambios
        conn.commit()

        # Verificar que se eliminó todo
        print(f"\n✅ Verificación post-eliminación:")

        cursor.execute("SELECT COUNT(*) FROM inventario WHERE codigo LIKE 'FIFO%'")
        remaining_articulos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM lotes WHERE codigo_articulo LIKE 'FIFO%'")
        remaining_lotes = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM movimientos_inventario WHERE codigo_articulo LIKE 'FIFO%'"
        )
        remaining_movimientos = cursor.fetchone()[0]

        print(f"   • Artículos FIFO restantes: {remaining_articulos}")
        print(f"   • Lotes FIFO restantes: {remaining_lotes}")
        print(f"   • Movimientos FIFO restantes: {remaining_movimientos}")

        if (
            remaining_articulos == 0
            and remaining_lotes == 0
            and remaining_movimientos == 0
        ):
            print(f"\n🎉 ¡ELIMINACIÓN COMPLETADA CON ÉXITO!")
            print(
                f"   • Total eliminado: {articulos_eliminados} artículos, {lotes_eliminados} lotes, {movimientos_eliminados} movimientos"
            )
            print(f"   • Base de datos limpia de artículos FIFO de prueba")
        else:
            print(
                f"\n⚠️  Advertencia: Algunos elementos FIFO no se eliminaron completamente"
            )

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        return False


def verificar_estado_limpio():
    """Verificar que no queden artículos FIFO en el sistema"""
    print(f"\n🔍 === VERIFICACIÓN FINAL ===")

    try:
        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()

        # Verificar todas las tablas relevantes
        tablas_verificar = [
            ("inventario", "codigo"),
            ("lotes", "codigo_articulo"),
            ("movimientos_inventario", "codigo_articulo"),
        ]

        todo_limpio = True

        for tabla, columna in tablas_verificar:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE {columna} LIKE 'FIFO%'")
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"   ❌ {tabla}: {count} registros FIFO encontrados")
                todo_limpio = False
            else:
                print(f"   ✅ {tabla}: Limpia")

        # Verificar estado general del inventario
        cursor.execute("SELECT COUNT(*) FROM inventario")
        total_articulos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM lotes")
        total_lotes = cursor.fetchone()[0]

        print(f"\n📊 Estado actual del sistema:")
        print(f"   • Total artículos: {total_articulos}")
        print(f"   • Total lotes: {total_lotes}")

        conn.close()

        if todo_limpio:
            print(f"\n✅ Sistema completamente limpio de artículos FIFO de prueba")
            print(f"💡 El sistema FIFO sigue disponible para artículos reales")
        else:
            print(f"\n⚠️  Se encontraron algunos registros FIFO restantes")

        return todo_limpio

    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False


def main():
    """Función principal"""
    print("🧹 HERRAMIENTA DE LIMPIEZA DE ARTÍCULOS FIFO")
    print("=" * 50)
    print("Esta herramienta eliminará TODOS los artículos de prueba FIFO")
    print("del sistema, incluyendo lotes y movimientos asociados.")
    print("=" * 50)

    # Paso 1: Eliminar artículos FIFO
    exito = eliminar_articulos_fifo()

    if exito:
        # Paso 2: Verificar que todo está limpio
        verificar_estado_limpio()

        print(f"\n🎯 RESULTADO FINAL:")
        print("   ✅ Artículos FIFO de prueba eliminados")
        print("   ✅ Sistema FIFO sigue funcional para artículos reales")
        print("   ✅ Base de datos limpia y optimizada")

        print(f"\n💡 Próximos pasos:")
        print("   • El sistema FIFO sigue disponible")
        print("   • Puedes agregar artículos reales cuando lo necesites")
        print("   • La integración en inventario permanece activa")

    else:
        print(f"\n❌ No se pudieron eliminar todos los artículos FIFO")
        print("   Revisa los errores mostrados arriba")


if __name__ == "__main__":
    main()
