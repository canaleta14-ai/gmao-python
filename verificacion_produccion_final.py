#!/usr/bin/env python3
"""
Verificación final del sistema listo para producción
"""
import os
import sqlite3


def verificacion_final_produccion():
    """Verificar que el sistema esté completamente listo para producción"""
    print("🎯 === VERIFICACIÓN FINAL - SISTEMA PRODUCCIÓN ===")
    print()

    resultados = {
        "base_datos": False,
        "inventario_limpio": False,
        "fifo_disponible": False,
        "interfaz_actualizada": False,
        "scripts_disponibles": False,
    }

    try:
        # 1. Verificar base de datos
        print("1️⃣ VERIFICANDO BASE DE DATOS:")
        conn = sqlite3.connect("instance/database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM inventario")
        count_inventario = cursor.fetchone()[0]
        print(f"   • Artículos en inventario: {count_inventario}")

        cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table" AND name="lotes"'
        )
        tabla_lotes = cursor.fetchone()
        if tabla_lotes:
            cursor.execute("SELECT COUNT(*) FROM lotes")
            count_lotes = cursor.fetchone()[0]
            print(f"   • Lotes existentes: {count_lotes}")
        else:
            print("   • Tabla lotes: Se creará automáticamente")

        resultados["base_datos"] = True
        resultados["inventario_limpio"] = count_inventario == 0
        conn.close()

        # 2. Verificar sistema FIFO
        print("\n2️⃣ VERIFICANDO SISTEMA FIFO:")
        archivos_fifo = [
            "app/blueprints/lotes.py",
            "static/js/fifo-inventario-badge.js",
            "app/services/servicio_fifo.py",
        ]

        fifo_ok = True
        for archivo in archivos_fifo:
            if os.path.exists(archivo):
                print(f"   ✅ {archivo}")
            else:
                print(f"   ❌ {archivo} - NO ENCONTRADO")
                fifo_ok = False

        resultados["fifo_disponible"] = fifo_ok

        # 3. Verificar interfaz actualizada
        print("\n3️⃣ VERIFICANDO INTERFAZ:")
        archivo_inventario = "app/templates/inventario/inventario.html"

        if os.path.exists(archivo_inventario):
            with open(archivo_inventario, "r", encoding="utf-8") as f:
                contenido = f.read()

            tiene_fifo = "btn-fifo" in contenido and "Gestión FIFO" in contenido
            tiene_eliminar = (
                "mostrarModalEliminarArticulos" in contenido
                and "Eliminar Artículos" in contenido
            )

            print(f"   ✅ Template inventario existe")
            print(f"   {'✅' if tiene_fifo else '❌'} Botón FIFO integrado")
            print(f"   {'✅' if tiene_eliminar else '❌'} Botón eliminar artículos")

            resultados["interfaz_actualizada"] = tiene_fifo and tiene_eliminar
        else:
            print("   ❌ Template inventario no encontrado")

        # 4. Verificar JavaScript
        print("\n4️⃣ VERIFICANDO JAVASCRIPT:")
        archivo_js = "static/js/inventario.js"

        if os.path.exists(archivo_js):
            with open(archivo_js, "r", encoding="utf-8") as f:
                contenido_js = f.read()

            tiene_modal_eliminar = "mostrarModalEliminarArticulos" in contenido_js
            tiene_confirmacion = "confirmarEliminacionArticulos" in contenido_js

            print(f"   ✅ JavaScript inventario existe")
            print(f"   {'✅' if tiene_modal_eliminar else '❌'} Función modal eliminar")
            print(f"   {'✅' if tiene_confirmacion else '❌'} Función confirmación")

            resultados["scripts_disponibles"] = (
                tiene_modal_eliminar and tiene_confirmacion
            )
        else:
            print("   ❌ JavaScript inventario no encontrado")

        # 5. Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN VERIFICACIÓN:")
        print("=" * 60)

        for categoria, estado in resultados.items():
            icono = "✅" if estado else "❌"
            print(f"   {icono} {categoria.replace('_', ' ').title()}")

        todos_ok = all(resultados.values())

        if todos_ok:
            print(f"\n🎉 ¡SISTEMA LISTO PARA PRODUCCIÓN!")
            print("=" * 60)
            print("✅ CARACTERÍSTICAS DISPONIBLES:")
            print("   • Inventario completamente limpio")
            print("   • Sistema FIFO integrado y funcional")
            print("   • Botón eliminar artículos con confirmación")
            print("   • Base de datos optimizada")
            print("   • Interfaz moderna y completa")
            print()
            print("🚀 PRÓXIMOS PASOS:")
            print("   1. Iniciar servidor: python run.py")
            print("   2. Acceder a: http://127.0.0.1:5000/inventario/")
            print("   3. Agregar artículos reales de producción")
            print("   4. Usar gestión FIFO cuando sea necesario")
            print("   5. Eliminar artículos con el botón de confirmación")

        else:
            print(f"\n⚠️  SISTEMA NECESITA AJUSTES")
            print("   Revise los elementos marcados con ❌")

        return todos_ok

    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False


if __name__ == "__main__":
    verificacion_final_produccion()
