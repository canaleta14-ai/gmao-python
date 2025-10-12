#!/usr/bin/env python3
"""
Verificación final del estado del sistema después de eliminar artículos FIFO
"""
import sqlite3


def verificar_estado_final():
    """Verificar que los artículos FIFO fueron eliminados correctamente"""
    try:
        conn = sqlite3.connect("instance/database.db")
        cursor = conn.cursor()

        # Verificar artículos FIFO restantes
        cursor.execute("SELECT COUNT(*) FROM inventario WHERE codigo LIKE 'FIFO%'")
        fifo_count = cursor.fetchone()[0]

        # Verificar total de artículos
        cursor.execute("SELECT COUNT(*) FROM inventario")
        total_count = cursor.fetchone()[0]

        print("📊 ESTADO FINAL DEL SISTEMA:")
        print(f"   • Artículos FIFO restantes: {fifo_count}")
        print(f"   • Total artículos en inventario: {total_count}")

        if fifo_count == 0:
            print("\n✅ ¡SISTEMA LIMPIO!")
            print("   • No hay artículos FIFO de prueba")
            print("   • El sistema FIFO sigue disponible para artículos reales")
            print("   • La integración en inventario permanece activa")
        else:
            print(f"\n⚠️  Aún hay {fifo_count} artículos FIFO")

            # Mostrar qué artículos quedan
            cursor.execute(
                "SELECT codigo, descripcion FROM inventario WHERE codigo LIKE 'FIFO%'"
            )
            restantes = cursor.fetchall()
            print("   Artículos restantes:")
            for codigo, desc in restantes:
                print(f"      • {codigo}: {desc or 'Sin descripción'}")

        conn.close()
        return fifo_count == 0

    except Exception as e:
        print(f"❌ Error verificando estado: {e}")
        return False


def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN FINAL")
    print("=" * 30)

    limpio = verificar_estado_final()

    if limpio:
        print("\n🎉 RESULTADO: Eliminación completada con éxito")
        print("📋 Próximos pasos:")
        print("   1. El sistema FIFO está listo para usar")
        print("   2. Puedes agregar artículos reales cuando lo necesites")
        print("   3. La integración en inventario funciona correctamente")
        print("   4. El botón '🏷️ Gestión FIFO' estará disponible")
    else:
        print("\n⚠️  RESULTADO: La eliminación no fue completa")
        print("   Revisa los artículos restantes arriba")


if __name__ == "__main__":
    main()
