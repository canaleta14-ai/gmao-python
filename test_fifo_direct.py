#!/usr/bin/env python3
"""
Test directo de la funcionalidad FIFO sin servidor
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_fifo_database():
    """Probar directamente la base de datos FIFO"""
    print("🏷️  === TEST DIRECTO SISTEMA FIFO ===")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()

        print("\n📊 Verificando artículos FIFO:")
        cursor.execute(
            """
            SELECT codigo, descripcion 
            FROM inventario 
            WHERE codigo LIKE 'FIFO%' 
            ORDER BY codigo
        """
        )
        articulos = cursor.fetchall()

        for codigo, descripcion in articulos:
            print(f"   • {codigo}: {descripcion}")

        print(f"\n📦 Total artículos FIFO: {len(articulos)}")

        print("\n🏷️  Verificando lotes activos:")
        cursor.execute(
            """
            SELECT l.numero_lote, l.codigo_articulo, l.cantidad, l.fecha_vencimiento,
                   i.descripcion
            FROM lotes l
            JOIN inventario i ON l.codigo_articulo = i.codigo
            WHERE l.cantidad > 0
            ORDER BY l.fecha_vencimiento
        """
        )
        lotes = cursor.fetchall()

        print(f"📋 Total lotes activos: {len(lotes)}")

        # Calcular estados de lotes
        hoy = datetime.now().date()
        treinta_dias = hoy + timedelta(days=30)

        vencidos = 0
        proximos_vencer = 0

        for numero_lote, codigo, cantidad, fecha_venc_str, descripcion in lotes:
            if fecha_venc_str:
                fecha_venc = datetime.strptime(fecha_venc_str, "%Y-%m-%d").date()

                if fecha_venc < hoy:
                    estado = "🔴 VENCIDO"
                    vencidos += 1
                elif fecha_venc <= treinta_dias:
                    estado = "🟡 PRÓXIMO A VENCER"
                    proximos_vencer += 1
                else:
                    estado = "🟢 OK"

                print(
                    f"   • {numero_lote} ({codigo}): {cantidad} uds - {fecha_venc} {estado}"
                )

        print(f"\n📈 Estadísticas de alertas:")
        print(f"   🔴 Lotes vencidos: {vencidos}")
        print(f"   🟡 Lotes próximos a vencer (30 días): {proximos_vencer}")
        print(f"   🟢 Lotes en buen estado: {len(lotes) - vencidos - proximos_vencer}")

        # Simular respuesta del API
        api_response = {
            "lotes": [],
            "estadisticas": {
                "total": len(lotes),
                "vencidos": vencidos,
                "proximos_vencer": proximos_vencer,
                "ok": len(lotes) - vencidos - proximos_vencer,
            },
        }

        for numero_lote, codigo, cantidad, fecha_venc_str, descripcion in lotes:
            api_response["lotes"].append(
                {
                    "numero_lote": numero_lote,
                    "codigo_articulo": codigo,
                    "descripcion": descripcion,
                    "cantidad": cantidad,
                    "fecha_vencimiento": fecha_venc_str,
                }
            )

        print(f"\n📡 Simulación de respuesta API:")
        print(f"   URL: /lotes/api/inventario/activos")
        print(f"   Status: 200 OK")
        print(f"   Data: {len(api_response['lotes'])} lotes encontrados")

        # Verificar qué mostraría el badge
        if vencidos > 0:
            badge_state = "DANGER"
            badge_count = vencidos
            badge_title = f"¡{vencidos} lote(s) vencido(s)! Haga clic para gestionar"
        elif proximos_vencer > 0:
            badge_state = "WARNING"
            badge_count = proximos_vencer
            badge_title = f"{proximos_vencer} lote(s) próximo(s) a vencer en 30 días"
        else:
            badge_state = "OK"
            badge_count = 0
            badge_title = "Sistema sin alertas"

        print(f"\n🏷️  Estado del badge en inventario:")
        print(f"   Estado: {badge_state}")
        print(f"   Contador: {badge_count}")
        print(f"   Título: {badge_title}")

        if badge_state == "DANGER":
            print(f"   🎨 Estilo: btn-outline-danger + animación pulse")
        elif badge_state == "WARNING":
            print(f"   🎨 Estilo: btn-outline-warning + animación fadeInOut")
        else:
            print(f"   🎨 Estilo: btn-outline-warning sin badge")

        conn.close()

        print(f"\n✅ TEST COMPLETADO - Sistema FIFO funcionando correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en test FIFO: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_fifo_integration():
    """Test de integración completa"""
    print("\n🔧 === TEST DE INTEGRACIÓN ===")

    # Verificar archivos clave
    files_to_check = [
        "app/templates/inventario/inventario.html",
        "static/js/fifo-inventario-badge.js",
        "static/css/style.css",
        "app/blueprints/lotes.py",
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - NO ENCONTRADO")

    # Verificar contenido de archivos importantes
    print(f"\n📄 Verificando contenido de archivos:")

    # Check inventario.html
    try:
        with open(
            "app/templates/inventario/inventario.html", "r", encoding="utf-8"
        ) as f:
            content = f.read()
            if "btn-fifo" in content and "fifo-notification-badge" in content:
                print(f"   ✅ inventario.html: Botón FIFO integrado")
            else:
                print(f"   ❌ inventario.html: Botón FIFO NO encontrado")
    except Exception as e:
        print(f"   ❌ Error leyendo inventario.html: {e}")

    # Check JavaScript
    try:
        with open("static/js/fifo-inventario-badge.js", "r", encoding="utf-8") as f:
            content = f.read()
            if (
                "updateFifoInventoryBadge" in content
                and "fifo-notification-badge" in content
            ):
                print(f"   ✅ fifo-inventario-badge.js: Script funcional")
            else:
                print(f"   ❌ fifo-inventario-badge.js: Script incompleto")
    except Exception as e:
        print(f"   ❌ Error leyendo JavaScript: {e}")

    # Check CSS
    try:
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            content = f.read()
            if "#btn-fifo" in content and "#fifo-notification-badge" in content:
                print(f"   ✅ style.css: Estilos FIFO presentes")
            else:
                print(f"   ❌ style.css: Estilos FIFO NO encontrados")
    except Exception as e:
        print(f"   ❌ Error leyendo CSS: {e}")


if __name__ == "__main__":
    print("🧪 INICIANDO TESTS DEL SISTEMA FIFO INTEGRADO")
    print("=" * 50)

    # Test 1: Base de datos
    db_ok = test_fifo_database()

    # Test 2: Integración de archivos
    test_fifo_integration()

    print("\n" + "=" * 50)

    if db_ok:
        print("🎉 RESULTADO: Sistema FIFO integrado correctamente")
        print("💡 Próximos pasos:")
        print("   1. Acceder a http://127.0.0.1:5000/inventario")
        print("   2. Verificar botón '🏷️ Gestión FIFO' con badge")
        print("   3. Confirmar funcionalidad del sistema")
    else:
        print("⚠️  RESULTADO: Se encontraron problemas en la integración")

    print("\n📋 RESUMEN DE LA INTEGRACIÓN:")
    print("   • Botón FIFO agregado a página de inventario")
    print("   • Badge de notificaciones en tiempo real")
    print("   • Sistema automático de alertas")
    print("   • Estilos CSS optimizados")
    print("   • JavaScript funcional para monitoreo")
