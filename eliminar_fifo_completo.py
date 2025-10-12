#!/usr/bin/env python3
"""
Script para verificar y eliminar artículos FIFO de las bases de datos correctas
"""
import os
import sys
import sqlite3


def verificar_base_datos(db_path, db_name):
    """Verificar el contenido de una base de datos"""
    print(f"\n🔍 Verificando {db_name}: {db_path}")

    if not os.path.exists(db_path):
        print(f"   ❌ No existe")
        return False, 0, 0

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si existe la tabla inventario
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inventario'"
        )
        if not cursor.fetchone():
            print(f"   ⚠️  No tiene tabla 'inventario'")
            conn.close()
            return False, 0, 0

        # Contar artículos FIFO
        cursor.execute("SELECT COUNT(*) FROM inventario WHERE codigo LIKE 'FIFO%'")
        count_articulos = cursor.fetchone()[0]

        # Verificar si existe la tabla lotes
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='lotes'"
        )
        if cursor.fetchone():
            cursor.execute(
                "SELECT COUNT(*) FROM lotes WHERE codigo_articulo LIKE 'FIFO%'"
            )
            count_lotes = cursor.fetchone()[0]
        else:
            count_lotes = 0

        print(f"   📊 Artículos FIFO: {count_articulos}")
        print(f"   🏷️  Lotes FIFO: {count_lotes}")

        if count_articulos > 0:
            print(f"   📋 Artículos encontrados:")
            cursor.execute(
                "SELECT codigo, descripcion FROM inventario WHERE codigo LIKE 'FIFO%'"
            )
            for codigo, desc in cursor.fetchall():
                print(f"      • {codigo}: {desc}")

        conn.close()
        return True, count_articulos, count_lotes

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, 0, 0


def eliminar_fifo_de_db(db_path, db_name):
    """Eliminar artículos FIFO de una base de datos específica"""
    print(f"\n🗑️  Eliminando FIFO de {db_name}...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Eliminar lotes FIFO
        cursor.execute("DELETE FROM lotes WHERE codigo_articulo LIKE 'FIFO%'")
        lotes_eliminados = cursor.rowcount
        print(f"   ✅ {lotes_eliminados} lotes eliminados")

        # Eliminar movimientos de inventario FIFO (si existe la tabla)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='movimientos_inventario'"
        )
        if cursor.fetchone():
            cursor.execute(
                "DELETE FROM movimientos_inventario WHERE codigo_articulo LIKE 'FIFO%'"
            )
            movimientos_eliminados = cursor.rowcount
            print(f"   ✅ {movimientos_eliminados} movimientos eliminados")

        # Eliminar artículos FIFO
        cursor.execute("DELETE FROM inventario WHERE codigo LIKE 'FIFO%'")
        articulos_eliminados = cursor.rowcount
        print(f"   ✅ {articulos_eliminados} artículos eliminados")

        conn.commit()
        conn.close()

        return articulos_eliminados + lotes_eliminados

    except Exception as e:
        print(f"   ❌ Error eliminando: {e}")
        return 0


def main():
    """Función principal"""
    print("🧹 ELIMINADOR DE ARTÍCULOS FIFO - TODAS LAS BASES DE DATOS")
    print("=" * 60)

    # Lista de bases de datos a verificar
    bases_datos = [
        ("inventario.db", "Base principal"),
        ("instance/database.db", "Base instance/database"),
        ("instance/gmao_local.db", "Base instance/gmao_local"),
    ]

    bases_con_fifo = []

    # Verificar todas las bases de datos
    print("🔍 VERIFICANDO BASES DE DATOS...")
    for db_file, db_name in bases_datos:
        tiene_tabla, count_articulos, count_lotes = verificar_base_datos(
            db_file, db_name
        )
        if count_articulos > 0 or count_lotes > 0:
            bases_con_fifo.append((db_file, db_name, count_articulos, count_lotes))

    if not bases_con_fifo:
        print("\n✅ No se encontraron artículos FIFO en ninguna base de datos")
        print("💡 El sistema ya está limpio")
        return

    # Mostrar resumen
    print(f"\n📊 RESUMEN:")
    total_articulos = 0
    total_lotes = 0

    for db_file, db_name, articulos, lotes in bases_con_fifo:
        print(f"   • {db_name}: {articulos} artículos, {lotes} lotes")
        total_articulos += articulos
        total_lotes += lotes

    print(f"\n📋 TOTAL A ELIMINAR: {total_articulos} artículos, {total_lotes} lotes")

    # Confirmar eliminación
    print(f"\n⚠️  ¿Eliminar TODOS los artículos FIFO de TODAS las bases de datos?")
    respuesta = input("   Escribe 'SI' para confirmar: ").strip().upper()

    if respuesta != "SI":
        print("❌ Operación cancelada")
        return

    # Proceder con la eliminación
    print(f"\n🗑️  INICIANDO ELIMINACIÓN...")
    total_eliminados = 0

    for db_file, db_name, _, _ in bases_con_fifo:
        eliminados = eliminar_fifo_de_db(db_file, db_name)
        total_eliminados += eliminados

    # Verificación final
    print(f"\n✅ VERIFICACIÓN FINAL...")
    todo_limpio = True

    for db_file, db_name in bases_datos:
        _, count_articulos, count_lotes = verificar_base_datos(db_file, db_name)
        if count_articulos > 0 or count_lotes > 0:
            todo_limpio = False
            print(f"   ⚠️  {db_name}: Aún tiene artículos FIFO")

    if todo_limpio:
        print(f"\n🎉 ¡ELIMINACIÓN COMPLETADA CON ÉXITO!")
        print(f"   • Total elementos eliminados: {total_eliminados}")
        print(f"   • Todas las bases de datos limpias")
        print(f"   • Sistema FIFO sigue disponible para artículos reales")
    else:
        print(
            f"\n⚠️  Advertencia: Algunos artículos FIFO no se eliminaron completamente"
        )


if __name__ == "__main__":
    main()
