"""
Script para migrar a categorías dinámicas
Añade las tablas de categorías y migra datos existentes
"""

from app import create_app
from app.extensions import db
from app.models.categoria import Categoria
from app.models.inventario import Inventario
from sqlalchemy import text


def migrar_categorias():
    """Migra las categorías existentes a la nueva estructura"""
    app = create_app()

    with app.app_context():
        # Crear las tablas si no existen
        db.create_all()

        # Obtener categorías únicas existentes
        categorias_existentes = db.session.execute(
            text(
                "SELECT DISTINCT categoria FROM inventario WHERE categoria IS NOT NULL AND categoria != ''"
            )
        ).fetchall()

        print(f"Encontradas {len(categorias_existentes)} categorías existentes")

        # Crear categorías predeterminadas
        categorias_default = [
            {
                "nombre": "Herramientas",
                "prefijo": "HER",
                "descripcion": "Herramientas de trabajo y mantenimiento",
                "color": "#28a745",
            },
            {
                "nombre": "Materiales",
                "prefijo": "MAT",
                "descripcion": "Materiales de construcción y mantenimiento",
                "color": "#ffc107",
            },
            {
                "nombre": "Equipos",
                "prefijo": "EQU",
                "descripcion": "Equipos y maquinaria",
                "color": "#007bff",
            },
            {
                "nombre": "Repuestos",
                "prefijo": "REP",
                "descripcion": "Repuestos y partes de recambio",
                "color": "#dc3545",
            },
            {
                "nombre": "Insumos",
                "prefijo": "INS",
                "descripcion": "Insumos y consumibles",
                "color": "#6f42c1",
            },
            {
                "nombre": "Otros",
                "prefijo": "OTR",
                "descripcion": "Otros artículos",
                "color": "#6c757d",
            },
        ]

        # Crear categorías por defecto si no existen
        for cat_data in categorias_default:
            categoria_existente = Categoria.query.filter_by(
                prefijo=cat_data["prefijo"]
            ).first()
            if not categoria_existente:
                nueva_categoria = Categoria(**cat_data)
                db.session.add(nueva_categoria)
                print(
                    f"Creando categoría: {cat_data['nombre']} ({cat_data['prefijo']})"
                )

        # Crear categorías para las existentes que no están en las por defecto
        for (categoria_nombre,) in categorias_existentes:
            # Verificar si ya existe una categoría con este nombre
            categoria_db = Categoria.query.filter_by(nombre=categoria_nombre).first()

            if not categoria_db:
                # Generar un prefijo único
                prefijo_base = categoria_nombre[:3].upper()
                prefijo = prefijo_base
                contador = 1

                while Categoria.query.filter_by(prefijo=prefijo).first():
                    prefijo = f"{prefijo_base}{contador}"
                    contador += 1

                nueva_categoria = Categoria(
                    nombre=categoria_nombre,
                    prefijo=prefijo,
                    descripcion=f"Categoría migrada: {categoria_nombre}",
                    color="#17a2b8",
                )

                db.session.add(nueva_categoria)
                print(f"Creando categoría migrada: {categoria_nombre} ({prefijo})")

        try:
            db.session.commit()
            print("✓ Categorías creadas exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error al crear categorías: {e}")
            return

        # Migrar relaciones de artículos existentes
        print("\nMigrando relaciones de artículos...")
        articulos_sin_categoria = Inventario.query.filter(
            (Inventario.categoria_id.is_(None))
            & (Inventario.categoria.isnot(None))
            & (Inventario.categoria != "")
        ).all()

        print(f"Encontrados {len(articulos_sin_categoria)} artículos para migrar")

        for articulo in articulos_sin_categoria:
            categoria = Categoria.query.filter_by(nombre=articulo.categoria).first()
            if categoria:
                articulo.categoria_id = categoria.id
                print(
                    f"Migrado artículo {articulo.codigo} a categoría {categoria.nombre}"
                )

        # Asignar categoría "Otros" a artículos sin categoría
        articulos_sin_ninguna_categoria = Inventario.query.filter(
            (Inventario.categoria_id.is_(None))
            & ((Inventario.categoria.is_(None)) | (Inventario.categoria == ""))
        ).all()

        categoria_otros = Categoria.query.filter_by(prefijo="OTR").first()
        if categoria_otros:
            for articulo in articulos_sin_ninguna_categoria:
                articulo.categoria_id = categoria_otros.id
                articulo.categoria = "Otros"
                print(f"Asignado artículo {articulo.codigo} a categoría Otros")

        try:
            db.session.commit()
            print("✓ Migración de artículos completada exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error en la migración de artículos: {e}")
            return

        # Mostrar estadísticas finales
        print("\n=== ESTADÍSTICAS FINALES ===")
        for categoria in Categoria.query.all():
            total_articulos = Inventario.query.filter_by(
                categoria_id=categoria.id
            ).count()
            print(
                f"{categoria.nombre} ({categoria.prefijo}): {total_articulos} artículos"
            )


if __name__ == "__main__":
    migrar_categorias()
