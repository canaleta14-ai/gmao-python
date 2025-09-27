"""
Script simple para añadir la columna categoria_id y crear categorías
"""

from app import create_app
from app.extensions import db
from app.models.categoria import Categoria
from sqlalchemy import text


def setup_categorias():
    """Configura las categorías dinámicas"""
    app = create_app()

    with app.app_context():
        # Crear las tablas si no existen
        db.create_all()

        # Añadir la columna categoria_id si no existe
        try:
            db.session.execute(
                text("ALTER TABLE inventario ADD COLUMN categoria_id INTEGER")
            )
            db.session.commit()
            print("✓ Columna categoria_id añadida")
        except Exception as e:
            if (
                "duplicate column name" in str(e).lower()
                or "already exists" in str(e).lower()
            ):
                print("✓ Columna categoria_id ya existe")
            else:
                print(f"Error añadiendo columna: {e}")

        # Crear categorías por defecto si no existen
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

        try:
            db.session.commit()
            print("✓ Categorías creadas exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error al crear categorías: {e}")

        # Mostrar estadísticas finales
        print("\n=== CATEGORÍAS DISPONIBLES ===")
        for categoria in Categoria.query.all():
            print(
                f"{categoria.nombre} ({categoria.prefijo}) - Color: {categoria.color}"
            )


if __name__ == "__main__":
    setup_categorias()
