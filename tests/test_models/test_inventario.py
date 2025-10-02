"""
Tests unitarios para el modelo Inventario
"""

import pytest
from app.models.inventario import Inventario


@pytest.mark.unit
class TestInventarioModel:

    def test_crear_item_inventario(self, db_session):
        """Test creación básica de item de inventario"""
        item = Inventario(
            codigo="INV-TEST-001",
            nombre="Rodamiento SKF 6205",
            categoria="Rodamientos",
            cantidad=50,
            cantidad_minima=10,
            ubicacion="Almacén A - Estante 3",
            unidad="Unidad",
        )
        db_session.add(item)
        db_session.commit()

        assert item.id is not None
        assert item.codigo == "INV-TEST-001"
        assert item.cantidad == 50
        assert item.cantidad_minima == 10

    def test_alerta_stock_minimo(self, db_session):
        """Test detección de stock por debajo del mínimo"""
        item_bajo = Inventario(
            codigo="INV-BAJO-001",
            nombre="Filtro de aceite",
            categoria="Filtros",
            cantidad=5,  # Menor que mínimo
            cantidad_minima=10,
            ubicacion="Almacén B",
            unidad="Unidad",
        )

        item_ok = Inventario(
            codigo="INV-OK-001",
            nombre="Aceite hidráulico",
            categoria="Lubricantes",
            cantidad=50,  # Mayor que mínimo
            cantidad_minima=20,
            ubicacion="Almacén C",
            unidad="Litro",
        )

        db_session.add_all([item_bajo, item_ok])
        db_session.commit()

        # Verificar ítems bajo stock mínimo
        bajo_stock = Inventario.query.filter(
            Inventario.cantidad < Inventario.cantidad_minima
        ).all()

        assert len(bajo_stock) >= 1
        assert item_bajo in bajo_stock
        assert item_ok not in bajo_stock

    def test_actualizar_cantidad(self, db_session):
        """Test actualización de cantidad de inventario"""
        item = Inventario(
            codigo="INV-UPDATE-001",
            nombre="Tornillo M8",
            categoria="Tornillería",
            cantidad=100,
            cantidad_minima=20,
            ubicacion="Almacén D",
            unidad="Unidad",
        )
        db_session.add(item)
        db_session.commit()

        cantidad_inicial = item.cantidad

        # Simular consumo
        item.cantidad -= 30
        db_session.commit()

        assert item.cantidad == cantidad_inicial - 30
        assert item.cantidad == 70

    def test_categorias_inventario(self, db_session):
        """Test diferentes categorías de inventario"""
        categorias = [
            "Rodamientos",
            "Filtros",
            "Lubricantes",
            "Tornillería",
            "Herramientas",
            "Eléctricos",
        ]

        for i, categoria in enumerate(categorias):
            item = Inventario(
                codigo=f"INV-CAT-{i:03d}",
                nombre=f"Item de {categoria}",
                categoria=categoria,
                cantidad=10,
                cantidad_minima=5,
                ubicacion="Almacén General",
                unidad="Unidad",
            )
            db_session.add(item)

        db_session.commit()

        # Verificar items por categoría
        rodamientos = Inventario.query.filter_by(categoria="Rodamientos").all()
        assert len(rodamientos) == 1

    def test_unidades_medida(self, db_session):
        """Test diferentes unidades de medida"""
        items = [
            ("INV-UN-001", "Tornillo", "Unidad"),
            ("INV-UN-002", "Aceite", "Litro"),
            ("INV-UN-003", "Cable", "Metro"),
            ("INV-UN-004", "Pintura", "Kilogramo"),
        ]

        for codigo, nombre, unidad in items:
            item = Inventario(
                codigo=codigo,
                nombre=nombre,
                categoria="General",
                cantidad=10,
                cantidad_minima=5,
                ubicacion="Almacén",
                unidad=unidad,
            )
            db_session.add(item)

        db_session.commit()

        # Verificar items en litros
        en_litros = Inventario.query.filter_by(unidad="Litro").all()
        assert len(en_litros) == 1
        assert en_litros[0].nombre == "Aceite"

    def test_codigo_unico(self, db_session):
        """Test que el código del item debe ser único"""
        item1 = Inventario(
            codigo="INV-UNIQUE-001",
            nombre="Item 1",
            categoria="General",
            cantidad=10,
            cantidad_minima=5,
            ubicacion="Almacén",
            unidad="Unidad",
        )
        db_session.add(item1)
        db_session.commit()

        # Intentar crear otro con el mismo código
        item2 = Inventario(
            codigo="INV-UNIQUE-001",  # Mismo código
            nombre="Item 2",
            categoria="General",
            cantidad=20,
            cantidad_minima=5,
            ubicacion="Almacén",
            unidad="Unidad",
        )
        db_session.add(item2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_precio_opcional(self, db_session):
        """Test campo precio opcional"""
        item_con_precio = Inventario(
            codigo="INV-PRECIO-001",
            nombre="Rodamiento Premium",
            categoria="Rodamientos",
            cantidad=20,
            cantidad_minima=5,
            ubicacion="Almacén A",
            unidad="Unidad",
            precio=25.50,
        )

        item_sin_precio = Inventario(
            codigo="INV-PRECIO-002",
            nombre="Tornillo genérico",
            categoria="Tornillería",
            cantidad=100,
            cantidad_minima=50,
            ubicacion="Almacén B",
            unidad="Unidad",
        )

        db_session.add_all([item_con_precio, item_sin_precio])
        db_session.commit()

        assert item_con_precio.precio == 25.50
        assert item_sin_precio.precio is None
