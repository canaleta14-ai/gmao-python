"""
Script de demostración del sistema de repuestos en órdenes de trabajo.
Muestra el flujo completo desde agregar repuestos hasta descontarlos del stock.
"""

from app import create_app
from app.extensions import db
from app.models.orden_trabajo import OrdenTrabajo
from app.models.inventario import Inventario
from app.models.orden_recambio import OrdenRecambio
from app.models.movimiento_inventario import MovimientoInventario
from app.controllers import orden_recambios_controller
from datetime import datetime


def imprimir_separador(titulo=""):
    """Imprime un separador visual."""
    if titulo:
        print(f"\n{'='*80}")
        print(f"  {titulo}")
        print("=" * 80)
    else:
        print("-" * 80)


def mostrar_orden_info(orden):
    """Muestra información de una orden."""
    print(f"\n📋 Orden: {orden.numero_orden}")
    print(f"   Estado: {orden.estado}")
    print(f"   Tipo: {orden.tipo}")
    print(f"   Activo: {orden.activo.nombre if orden.activo else 'Sin activo'}")
    print(f"   Técnico: {orden.tecnico.nombre if orden.tecnico else 'Sin asignar'}")


def mostrar_articulo_stock(articulo):
    """Muestra información de stock de un artículo."""
    print(f"\n📦 {articulo.codigo} - {articulo.descripcion}")
    print(f"   Stock actual: {articulo.stock_actual} {articulo.unidad_medida}")
    print(f"   Stock mínimo: {articulo.stock_minimo} {articulo.unidad_medida}")
    print(f"   Precio promedio: ${articulo.precio_promedio}")

    if articulo.necesita_reposicion:
        print(f"   ⚠️ ALERTA: Stock bajo (requiere reposición)")
    else:
        print(f"   ✅ Stock OK")


def mostrar_recambios_orden(orden_id):
    """Muestra los recambios de una orden."""
    recambios = OrdenRecambio.query.filter_by(orden_trabajo_id=orden_id).all()

    if not recambios:
        print("\n   No hay recambios asignados")
        return

    print(f"\n   Recambios asignados: {len(recambios)}")
    print(
        f"\n   {'Artículo':<15} {'Descripción':<30} {'Solicitado':>10} {'Utilizado':>10} {'Estado':>12}"
    )
    print(f"   {'-'*15} {'-'*30} {'-'*10} {'-'*10} {'-'*12}")

    for r in recambios:
        estado = "✅ Descontado" if r.descontado else "⏳ Pendiente"
        utilizado = r.cantidad_utilizada if r.cantidad_utilizada else "-"

        print(
            f"   {r.inventario.codigo:<15} {r.inventario.descripcion[:30]:<30} "
            f"{r.cantidad_solicitada:>10} {utilizado:>10} {estado:>12}"
        )


def mostrar_movimientos_recientes(inventario_id=None):
    """Muestra movimientos de inventario recientes."""
    query = MovimientoInventario.query.order_by(MovimientoInventario.fecha.desc())

    if inventario_id:
        query = query.filter_by(inventario_id=inventario_id)

    movimientos = query.limit(5).all()

    if not movimientos:
        print("\n   No hay movimientos recientes")
        return

    print(f"\n   Últimos movimientos:")
    print(
        f"\n   {'Fecha':<20} {'Tipo':<12} {'Cantidad':>10} {'Documento':<15} {'Observación':<30}"
    )
    print(f"   {'-'*20} {'-'*12} {'-'*10} {'-'*15} {'-'*30}")

    for m in movimientos:
        fecha = m.fecha.strftime("%Y-%m-%d %H:%M") if m.fecha else "N/A"
        obs = (
            (m.observaciones[:27] + "...")
            if m.observaciones and len(m.observaciones) > 30
            else (m.observaciones or "")
        )

        print(
            f"   {fecha:<20} {m.tipo:<12} {m.cantidad:>10} "
            f"{m.documento_referencia or 'N/A':<15} {obs:<30}"
        )


def demo_flujo_completo():
    """Demostración completa del flujo de repuestos."""
    app = create_app()

    with app.app_context():
        imprimir_separador("DEMOSTRACIÓN: SISTEMA DE REPUESTOS EN ÓRDENES")

        # 1. Seleccionar una orden
        print("\n📌 PASO 1: Seleccionar una orden de trabajo")
        imprimir_separador()

        orden = OrdenTrabajo.query.filter_by(estado="Pendiente").first()

        if not orden:
            orden = OrdenTrabajo.query.first()

        if not orden:
            print("❌ No hay órdenes disponibles en el sistema")
            return

        mostrar_orden_info(orden)

        # 2. Mostrar artículos disponibles
        imprimir_separador("PASO 2: Artículos disponibles en inventario")

        articulos = (
            Inventario.query.filter(
                Inventario.activo == True, Inventario.stock_actual > 0
            )
            .limit(5)
            .all()
        )

        if not articulos:
            print("❌ No hay artículos con stock disponible")
            return

        print(f"\n   Mostrando {len(articulos)} artículos con stock:")

        for art in articulos:
            mostrar_articulo_stock(art)

        # 3. Agregar repuestos a la orden
        imprimir_separador("PASO 3: Agregar repuestos a la orden")

        # Verificar repuestos existentes
        recambios_existentes = OrdenRecambio.query.filter_by(
            orden_trabajo_id=orden.id
        ).all()

        if recambios_existentes:
            print(
                f"\n⚠️ Esta orden ya tiene {len(recambios_existentes)} repuesto(s) asignado(s)"
            )
            mostrar_recambios_orden(orden.id)

            respuesta = input("\n¿Deseas agregar más repuestos? (s/n): ")
            if respuesta.lower() != "s":
                print("\n✋ Saltando al siguiente paso...")
                articulo_demo = recambios_existentes[0].inventario
            else:
                # Agregar nuevo repuesto
                articulo_demo = articulos[0]
                print(
                    f"\n➕ Agregando: {articulo_demo.codigo} - {articulo_demo.descripcion}"
                )
                print(f"   Cantidad: 2 unidades")

                try:
                    recambio = orden_recambios_controller.agregar_recambio_a_orden(
                        orden_id=orden.id,
                        inventario_id=articulo_demo.id,
                        cantidad_solicitada=2,
                        observaciones="Repuesto de demostración",
                    )

                    print(f"   ✅ Repuesto agregado exitosamente (ID: {recambio.id})")
                    mostrar_recambios_orden(orden.id)

                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    articulo_demo = recambios_existentes[0].inventario
        else:
            # No hay repuestos, agregar uno nuevo
            articulo_demo = articulos[0]
            print(f"\n➕ Agregando repuesto de demostración:")
            print(f"   Artículo: {articulo_demo.codigo} - {articulo_demo.descripcion}")
            print(f"   Cantidad solicitada: 2 unidades")
            print(f"   Stock disponible: {articulo_demo.stock_actual}")

            try:
                recambio = orden_recambios_controller.agregar_recambio_a_orden(
                    orden_id=orden.id,
                    inventario_id=articulo_demo.id,
                    cantidad_solicitada=2,
                    observaciones="Repuesto agregado en demostración del sistema",
                )

                print(f"\n   ✅ Repuesto agregado exitosamente")
                mostrar_recambios_orden(orden.id)

            except Exception as e:
                print(f"   ❌ Error agregando repuesto: {e}")
                return

        # 4. Ver stock ANTES del descuento
        imprimir_separador("PASO 4: Stock ANTES del descuento")

        articulo_demo = Inventario.query.get(articulo_demo.id)  # Refrescar datos
        mostrar_articulo_stock(articulo_demo)

        # 5. Descontar repuestos
        imprimir_separador("PASO 5: Descontar repuestos del stock")

        # Contar repuestos pendientes
        pendientes = OrdenRecambio.query.filter_by(
            orden_trabajo_id=orden.id, descontado=False
        ).count()

        if pendientes == 0:
            print("\n⚠️ No hay repuestos pendientes de descontar")
            print("   (Todos ya fueron descontados anteriormente)")
        else:
            print(f"\n   Repuestos pendientes de descontar: {pendientes}")

            respuesta = input("\n¿Proceder con el descuento? (s/n): ")

            if respuesta.lower() == "s":
                try:
                    resultado = orden_recambios_controller.descontar_recambios_orden(
                        orden_id=orden.id,
                        usuario_id="demo_usuario",
                        es_automatico=False,
                    )

                    print(f"\n   ✅ {resultado['mensaje']}")

                    if resultado["recambios_descontados"]:
                        print(f"\n   Recambios descontados:")
                        for r in resultado["recambios_descontados"]:
                            print(f"      • {r['articulo']}: {r['cantidad']} unidades")
                            print(
                                f"        Stock: {r['stock_anterior']} → {r['stock_actual']}"
                            )

                    if resultado.get("errores"):
                        print(f"\n   ⚠️ Errores encontrados:")
                        for e in resultado["errores"]:
                            print(f"      • {e['articulo']}: {e['error']}")

                except Exception as e:
                    print(f"   ❌ Error descontando repuestos: {e}")
            else:
                print("\n✋ Descuento cancelado")

        # 6. Ver stock DESPUÉS del descuento
        imprimir_separador("PASO 6: Stock DESPUÉS del descuento")

        articulo_demo = Inventario.query.get(articulo_demo.id)  # Refrescar datos
        mostrar_articulo_stock(articulo_demo)

        # 7. Ver repuestos actualizados
        imprimir_separador("PASO 7: Estado de repuestos de la orden")
        mostrar_recambios_orden(orden.id)

        # 8. Ver movimientos de inventario generados
        imprimir_separador("PASO 8: Movimientos de inventario generados")
        mostrar_movimientos_recientes(articulo_demo.id)

        # Resumen final
        imprimir_separador("RESUMEN FINAL")

        print(
            f"""
✅ Demostración completada exitosamente

El sistema permite:
   • ➕ Agregar repuestos a órdenes de trabajo
   • 📊 Ver stock disponible en tiempo real
   • 💾 Descontar del inventario (manual o automático)
   • 🔍 Rastrear movimientos y auditoría completa
   • ⚠️ Validar stock antes de descontar
   • 🔒 Prevenir descuentos duplicados

Orden utilizada: {orden.numero_orden}
Artículo demostrado: {articulo_demo.codigo}
Estado actual: {'✅ Sistema operacional' if articulo_demo else '❌ Error'}
"""
        )

        imprimir_separador()


def mostrar_estadisticas():
    """Muestra estadísticas generales del sistema."""
    app = create_app()

    with app.app_context():
        imprimir_separador("ESTADÍSTICAS DEL SISTEMA DE REPUESTOS")

        # Órdenes con repuestos
        ordenes_con_repuestos = (
            db.session.query(OrdenTrabajo.id).join(OrdenRecambio).distinct().count()
        )

        # Total de repuestos asignados
        total_repuestos = OrdenRecambio.query.count()

        # Repuestos descontados
        repuestos_descontados = OrdenRecambio.query.filter_by(descontado=True).count()

        # Repuestos pendientes
        repuestos_pendientes = OrdenRecambio.query.filter_by(descontado=False).count()

        # Movimientos tipo orden_trabajo
        movimientos_ot = MovimientoInventario.query.filter_by(
            subtipo="orden_trabajo"
        ).count()

        print(
            f"""
📊 Estadísticas Globales:

   Órdenes con repuestos asignados: {ordenes_con_repuestos}
   Total de repuestos registrados: {total_repuestos}
   
   Repuestos descontados: {repuestos_descontados}
   Repuestos pendientes: {repuestos_pendientes}
   
   Movimientos de inventario tipo OT: {movimientos_ot}

📈 Estado del Sistema:
   {'✅ Sistema operacional' if total_repuestos > 0 else '⚠️ Sin datos aún'}
   {'✅ Control de inventario activo' if movimientos_ot > 0 else 'ℹ️ Sin movimientos registrados'}
"""
        )

        imprimir_separador()


def main():
    """Función principal con menú."""
    print(
        """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║        DEMO: SISTEMA DE REPUESTOS EN ÓRDENES DE TRABAJO                   ║
║                                                                            ║
║  Este script demuestra el funcionamiento completo del sistema de          ║
║  gestión de repuestos integrado con las órdenes de trabajo.               ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
    )

    print("Opciones disponibles:\n")
    print("  1. Demo completa del flujo de repuestos")
    print("  2. Ver estadísticas del sistema")
    print("  3. Ambas opciones")
    print("  0. Salir")

    try:
        opcion = input("\nSelecciona una opción (0-3): ")

        if opcion == "1":
            demo_flujo_completo()
        elif opcion == "2":
            mostrar_estadisticas()
        elif opcion == "3":
            mostrar_estadisticas()
            input("\nPresiona Enter para continuar con la demo...")
            demo_flujo_completo()
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
        else:
            print("\n❌ Opción no válida")

    except KeyboardInterrupt:
        print("\n\n👋 Demo interrumpida. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
