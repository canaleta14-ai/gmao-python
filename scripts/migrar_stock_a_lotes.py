"""
Script de migración: Crear lotes iniciales para artículos existentes con stock

Este script crea un lote inicial para cada artículo que tiene stock pero no tiene lotes.
Es necesario para habilitar el sistema FIFO en artículos que ya existen en la base de datos.

IMPORTANTE: Este script debe ejecutarse UNA SOLA VEZ durante la migración al sistema FIFO.

Uso:
    python scripts/migrar_stock_a_lotes.py
"""

from app import create_app
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario
from app.extensions import db
from datetime import datetime, timezone
from decimal import Decimal

app = create_app()


def generar_codigo_lote(inventario_id, fecha):
    """Genera un código de lote único para la migración"""
    fecha_str = fecha.strftime("%Y%m%d")
    return f"LOTE-INICIAL-{inventario_id}-{fecha_str}"


def migrar_articulo_a_lote(articulo):
    """Crea un lote inicial para un artículo con stock"""
    try:
        # Verificar si ya tiene lotes
        lotes_existentes = LoteInventario.query.filter_by(
            inventario_id=articulo.id
        ).count()

        if lotes_existentes > 0:
            return False, f"Ya tiene {lotes_existentes} lote(s)"

        # Crear lote inicial
        fecha_actual = datetime.now(timezone.utc)
        codigo_lote = generar_codigo_lote(articulo.id, fecha_actual)

        lote = LoteInventario(
            inventario_id=articulo.id,
            codigo_lote=codigo_lote,
            cantidad_inicial=Decimal(str(articulo.stock_actual)),
            cantidad_actual=Decimal(str(articulo.stock_actual)),
            cantidad_reservada=Decimal("0"),
            fecha_entrada=fecha_actual,
            fecha_vencimiento=None,  # Sin fecha de vencimiento para stock inicial
            precio_unitario=Decimal(str(articulo.precio_unitario or 0)),
            costo_total=Decimal(str(articulo.stock_actual))
            * Decimal(str(articulo.precio_unitario or 0)),
            documento_origen="MIGRACIÓN INICIAL",
            observaciones=(
                f"Lote creado automáticamente durante la migración al sistema FIFO. "
                f"Stock original: {articulo.stock_actual} {articulo.unidad_medida or 'UNI'}"
            ),
            usuario_creacion="SISTEMA",
        )

        db.session.add(lote)
        return True, f"Lote creado: {codigo_lote}"

    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Ejecuta la migración de stock a lotes"""
    print("\n" + "=" * 70)
    print("🔄 MIGRACIÓN DE STOCK EXISTENTE A SISTEMA FIFO")
    print("=" * 70)

    with app.app_context():
        # Obtener artículos con stock pero sin lotes
        print("\n📊 Analizando inventario...")

        articulos_con_stock = Inventario.query.filter(Inventario.stock_actual > 0).all()

        print(f"\n✅ Encontrados {len(articulos_con_stock)} artículos con stock > 0")

        # Filtrar los que no tienen lotes
        articulos_sin_lotes = []
        for articulo in articulos_con_stock:
            lotes_count = LoteInventario.query.filter_by(
                inventario_id=articulo.id
            ).count()
            if lotes_count == 0:
                articulos_sin_lotes.append(articulo)

        print(f"📦 Artículos sin lotes: {len(articulos_sin_lotes)}")

        if len(articulos_sin_lotes) == 0:
            print("\n✅ No hay artículos que necesiten migración")
            print("   Todos los artículos con stock ya tienen lotes asignados")
            return

        # Confirmación
        print(f"\n⚠️  Se crearán {len(articulos_sin_lotes)} lotes iniciales")
        print("\n📋 Ejemplos de artículos a migrar:")
        for i, art in enumerate(articulos_sin_lotes[:5], 1):
            print(
                f"   {i}. [{art.codigo}] {art.nombre or art.descripcion} - Stock: {art.stock_actual}"
            )

        if len(articulos_sin_lotes) > 5:
            print(f"   ... y {len(articulos_sin_lotes) - 5} más")

        respuesta = (
            input("\n¿Desea continuar con la migración? (si/no): ").lower().strip()
        )

        if respuesta not in ["si", "s", "sí", "yes", "y"]:
            print("\n❌ Migración cancelada por el usuario")
            return

        # Ejecutar migración
        print("\n🔄 Iniciando migración...")
        print("-" * 70)

        exitosos = 0
        fallidos = 0
        errores = []

        for i, articulo in enumerate(articulos_sin_lotes, 1):
            exito, mensaje = migrar_articulo_a_lote(articulo)

            if exito:
                exitosos += 1
                print(
                    f"✅ [{i}/{len(articulos_sin_lotes)}] {articulo.codigo}: {mensaje}"
                )
            else:
                fallidos += 1
                errores.append((articulo.codigo, mensaje))
                print(
                    f"❌ [{i}/{len(articulos_sin_lotes)}] {articulo.codigo}: {mensaje}"
                )

            # Commit cada 50 registros para evitar transacciones muy largas
            if i % 50 == 0:
                try:
                    db.session.commit()
                    print(f"   💾 Guardando lote {i}...")
                except Exception as e:
                    db.session.rollback()
                    print(f"   ⚠️  Error al guardar: {str(e)}")

        # Commit final
        try:
            db.session.commit()
            print("\n💾 Guardando cambios finales...")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar cambios finales: {str(e)}")
            return

        # Resumen
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE LA MIGRACIÓN")
        print("=" * 70)
        print(f"\n✅ Lotes creados exitosamente: {exitosos}")
        print(f"❌ Fallos: {fallidos}")

        if errores:
            print("\n⚠️  Errores detectados:")
            for codigo, mensaje in errores[:10]:
                print(f"   - {codigo}: {mensaje}")
            if len(errores) > 10:
                print(f"   ... y {len(errores) - 10} más")

        # Verificación final
        total_lotes_despues = LoteInventario.query.count()
        print(f"\n📦 Total de lotes en el sistema: {total_lotes_despues}")

        print("\n✅ Migración completada")
        print("\n💡 Próximos pasos:")
        print("   1. Verificar los lotes creados en /lotes/")
        print("   2. Ajustar fechas de vencimiento si es necesario")
        print("   3. Comenzar a usar el sistema FIFO para nuevas entradas")
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migración interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error crítico durante la migración: {str(e)}")
        import traceback

        traceback.print_exc()
