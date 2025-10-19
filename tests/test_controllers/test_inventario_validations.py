"""
Tests unitarios para validaciones del módulo inventario
Prueba las validaciones implementadas en inventario_controller_simple.py
"""

import pytest
from app.controllers.inventario_controller_simple import crear_articulo_simple
from app.models.inventario import Inventario
from app.extensions import db


class TestInventarioValidaciones:
    """Suite de tests para validaciones de creación de artículos"""

    def test_crear_articulo_sin_descripcion_falla(self, client):
        """Debe fallar si la descripción está vacía"""
        data = {
            "codigo": "TEST001",
            "descripcion": "",  # Descripción vacía
            "stock_minimo": 10,
            "stock_maximo": 100,
        }

        with pytest.raises(ValueError) as excinfo:
            crear_articulo_simple(data)

        assert "descripción es obligatoria" in str(excinfo.value).lower()

    def test_crear_articulo_sin_codigo_sin_categoria_falla(self, client):
        """Debe fallar si no hay código ni categoría_id para generarlo"""
        data = {"codigo": "", "categoria_id": None, "descripcion": "Artículo de prueba"}

        with pytest.raises(ValueError) as excinfo:
            crear_articulo_simple(data)

        assert "código es obligatorio" in str(excinfo.value).lower()

    def test_crear_articulo_stock_minimo_negativo_falla(self, client):
        """Debe fallar si el stock mínimo es negativo"""
        data = {
            "codigo": "TEST002",
            "descripcion": "Artículo de prueba",
            "stock_minimo": -5,  # Stock negativo
            "stock_maximo": 100,
        }

        with pytest.raises(ValueError) as excinfo:
            crear_articulo_simple(data)

        assert (
            "stock actual no puede ser negativo" in str(excinfo.value).lower()
            or "stock mínimo no puede ser negativo" in str(excinfo.value).lower()
        )

    def test_crear_articulo_stock_maximo_negativo_falla(self, client):
        """Debe fallar si el stock máximo es negativo"""
        data = {
            "codigo": "TEST003",
            "descripcion": "Artículo de prueba",
            "stock_minimo": 10,
            "stock_maximo": -100,  # Stock negativo
        }

        with pytest.raises(ValueError) as excinfo:
            crear_articulo_simple(data)

        assert "stock máximo no puede ser negativo" in str(excinfo.value).lower()

    def test_crear_articulo_precio_negativo_falla(self, client):
        """Debe fallar si el precio unitario es negativo"""
        data = {
            "codigo": "TEST004",
            "descripcion": "Artículo de prueba",
            "precio_unitario": -50.00,  # Precio negativo
        }

        with pytest.raises(ValueError) as excinfo:
            crear_articulo_simple(data)

        assert (
            "precio" in str(excinfo.value).lower()
            and "negativo" in str(excinfo.value).lower()
        )

    def test_crear_articulo_stock_minimo_mayor_que_maximo_falla(self, client):
        """Debe fallar si stock_minimo > stock_maximo cuando stock_maximo > 0"""
        data = {
            "codigo": "TEST005",
            "descripcion": "Artículo de prueba",
            "stock_minimo": 100,  # Mayor que el máximo
            "stock_maximo": 50,
        }

        with pytest.raises(ValueError) as excinfo:
            crear_articulo_simple(data)

        assert "stock mínimo no puede ser mayor" in str(excinfo.value).lower()

    def test_crear_articulo_valores_no_numericos_falla(self, client):
        """Debe fallar si los valores numéricos no son válidos"""
        data = {
            "codigo": "TEST006",
            "descripcion": "Artículo de prueba",
            "stock_minimo": "abc",  # Valor no numérico
            "stock_maximo": 100,
        }

        with pytest.raises(ValueError) as excinfo:
            crear_articulo_simple(data)

        assert (
            "numéricos" in str(excinfo.value).lower()
            or "válidos" in str(excinfo.value).lower()
        )

    def test_crear_articulo_codigo_duplicado_falla(self, client, db_session):
        """Debe fallar si el código ya existe en la base de datos"""
        # Crear primer artículo
        data1 = {"codigo": "TEST_DUP001", "descripcion": "Artículo original"}
        articulo1 = crear_articulo_simple(data1)
        db.session.commit()

        # Intentar crear artículo con código duplicado
        data2 = {
            "codigo": "TEST_DUP001",  # Código duplicado
            "descripcion": "Artículo duplicado",
        }

        with pytest.raises(Exception):  # IntegrityError o ValueError
            crear_articulo_simple(data2)
            db.session.commit()

    def test_crear_articulo_valido_exitoso(self, client, db_session):
        """Debe crear artículo exitosamente con datos válidos"""
        data = {
            "codigo": "TEST_VALID001",
            "descripcion": "Artículo válido de prueba",
            "stock_minimo": 10,
            "stock_maximo": 100,
            "precio_unitario": 25.50,
            "unidad_medida": "UNI",
            "activo": True,
        }

        articulo = crear_articulo_simple(data)
        db.session.commit()

        assert articulo is not None
        assert articulo.codigo == "TEST_VALID001"
        assert articulo.descripcion == "Artículo válido de prueba"
        assert float(articulo.stock_minimo) == 10
        assert float(articulo.stock_maximo) == 100
        assert float(articulo.precio_unitario) == 25.50

    def test_crear_articulo_con_codigo_vacio_y_categoria_genera_codigo(
        self, client, db_session
    ):
        """Debe generar código automáticamente si está vacío pero hay categoría_id"""
        # Nota: Este test asume que existe una categoría con id=1 en la BD de prueba
        data = {
            "codigo": "",  # Código vacío
            "categoria_id": 1,  # Categoría válida
            "descripcion": "Artículo con código auto-generado",
        }

        articulo = crear_articulo_simple(data)
        db.session.commit()

        assert articulo is not None
        assert articulo.codigo != ""  # Debe tener código generado
        assert articulo.descripcion == "Artículo con código auto-generado"

    def test_crear_articulo_stock_maximo_cero_permite_minimo_mayor(
        self, client, db_session
    ):
        """Cuando stock_maximo es 0, no debe validar que minimo <= maximo"""
        data = {
            "codigo": "TEST_STOCK_ZERO",
            "descripcion": "Artículo con stock máximo en cero",
            "stock_minimo": 10,
            "stock_maximo": 0,  # Máximo en cero permite cualquier mínimo
        }

        articulo = crear_articulo_simple(data)
        db.session.commit()

        assert articulo is not None
        assert float(articulo.stock_minimo) == 10
        assert float(articulo.stock_maximo) == 0

    def test_crear_articulo_campos_opcionales_con_none(self, client, db_session):
        """Debe aceptar None en campos opcionales"""
        data = {
            "codigo": "TEST_OPTIONAL",
            "descripcion": "Artículo con campos opcionales",
            "stock_minimo": 0,
            "stock_maximo": 0,
            "precio_unitario": None,  # Opcional
            "unidad_medida": None,  # Opcional
            "proveedor": None,  # Opcional
            "ubicacion": None,  # Opcional
        }

        articulo = crear_articulo_simple(data)
        db.session.commit()

        assert articulo is not None
        assert articulo.codigo == "TEST_OPTIONAL"
        assert articulo.precio_unitario is None or float(articulo.precio_unitario) == 0

    def test_crear_articulo_convierte_tipos_correctamente(self, client, db_session):
        """Debe convertir strings a números correctamente"""
        data = {
            "codigo": "TEST_CONVERSION",
            "descripcion": "Artículo con conversión de tipos",
            "stock_minimo": "15",  # String que debe convertirse a número
            "stock_maximo": "150",  # String que debe convertirse a número
            "precio_unitario": "45.99",  # String que debe convertirse a float
        }

        articulo = crear_articulo_simple(data)
        db.session.commit()

        assert articulo is not None
        assert float(articulo.stock_minimo) == 15
        assert float(articulo.stock_maximo) == 150
        assert float(articulo.precio_unitario) == 45.99
