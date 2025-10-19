"""
Script para verificar la situación actual de artículos y lotes en el sistema
"""

from app import create_app
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario
from app.extensions import db

app = create_app()

with app.app_context():
    total_articulos = Inventario.query.count()
    total_lotes = LoteInventario.query.count()
    articulos_con_stock = Inventario.query.filter(Inventario.stock_actual > 0).count()

    print("\n" + "=" * 60)
    print("📊 ANÁLISIS DE INVENTARIO Y LOTES")
    print("=" * 60)
    print(f"\n✅ Artículos totales en inventario: {total_articulos}")
    print(f"✅ Artículos con stock > 0: {articulos_con_stock}")
    print(f"📦 Lotes FIFO creados: {total_lotes}")

    if total_lotes == 0 and articulos_con_stock > 0:
        print("\n⚠️  PROBLEMA DETECTADO:")
        print("   - Hay artículos con stock pero NO hay lotes creados")
        print("   - El sistema FIFO requiere que el stock esté organizado en lotes")
        print("\n💡 SOLUCIÓN:")
        print("   - Opción 1: Crear lotes manualmente desde /lotes/crear_lote")
        print("   - Opción 2: Ejecutar script de migración automática")

        # Mostrar algunos ejemplos
        print("\n📋 Ejemplos de artículos con stock sin lotes:")
        ejemplos = Inventario.query.filter(Inventario.stock_actual > 0).limit(5).all()
        for art in ejemplos:
            print(
                f"   - ID: {art.id} | Código: {art.codigo} | Stock: {art.stock_actual} | {art.nombre or art.descripcion}"
            )

    elif total_lotes > 0:
        print("\n✅ Sistema FIFO configurado correctamente")

        # Verificar artículos con lotes
        articulos_con_lotes = (
            db.session.query(Inventario.id)
            .join(LoteInventario, Inventario.id == LoteInventario.inventario_id)
            .distinct()
            .count()
        )

        print(f"📦 Artículos que tienen lotes: {articulos_con_lotes}")

        if articulos_con_stock > articulos_con_lotes:
            sin_lotes = articulos_con_stock - articulos_con_lotes
            print(f"\n⚠️  Artículos con stock pero sin lotes: {sin_lotes}")
            print("   Estos artículos necesitan lotes para usar el sistema FIFO")

    print("\n" + "=" * 60 + "\n")
