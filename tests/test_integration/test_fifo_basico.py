"""
Test de integración básico para el sistema FIFO.
Prueba el flujo básico: crear lote → consumir → verificar.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from app.extensions import db
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario
from app.models.categoria import Categoria
from app.services.servicio_fifo import ServicioFIFO


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_basico_entrada_y_consumo(app, client):
    """
    Test básico de integración FIFO: entrada de lote y consumo
    """
    with app.app_context():
        # Crear categoría
        categoria = Categoria(nombre="Test FIFO", descripcion="Para testing")
        db.session.add(categoria)
        db.session.commit()

        # Crear artículo de inventario
        inventario = Inventario(
            codigo="TEST-FIFO-001",
            nombre="Material Test FIFO",
            descripcion="Para pruebas de integración FIFO",
            categoria_id=categoria.id,
            unidad_medida="kg",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("10"),
            stock_maximo=Decimal("100"),
            precio_unitario=Decimal("25.50"),
            activo=True,
        )
        db.session.add(inventario)
        db.session.commit()

        # PASO 1: Crear entrada de lote
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario.id,
            cantidad=100.0,
            precio_unitario=25.0,
            codigo_lote="LOTE-TEST-001",
            documento_origen="COMPRA-TEST-001",
            usuario_id="test_user",
            observaciones="Lote de prueba para integración",
        )

        db.session.commit()

        # Verificar lote creado
        assert lote is not None
        assert lote.inventario_id == inventario.id
        assert lote.cantidad_inicial == Decimal("100")
        assert lote.cantidad_actual == Decimal("100")
        assert lote.precio_unitario == Decimal("25.0")
        assert lote.codigo_lote == "LOTE-TEST-001"

        # PASO 2: Consumir parte del lote
        lotes_consumidos, cantidad_faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario.id,
            cantidad_total=30.0,
            documento_referencia="CONSUMO-TEST-001",
            usuario_id="test_user",
            observaciones="Consumo de prueba",
        )

        db.session.commit()

        # Verificar consumo
        assert cantidad_faltante == 0
        assert len(lotes_consumidos) == 1

        lote_consumido, cantidad_consumida = lotes_consumidos[0]
        assert lote_consumido.id == lote.id
        assert cantidad_consumida == 30.0

        # Verificar estado del lote después del consumo
        db.session.refresh(lote)
        assert lote.cantidad_actual == Decimal("70")  # 100 - 30 = 70


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_orden_consumo_correcto(app, client):
    """
    Test que verifica el orden correcto de consumo FIFO (First In, First Out)
    """
    with app.app_context():
        # Crear categoría
        categoria = Categoria(
            nombre="Test FIFO Orden", descripcion="Para testing orden"
        )
        db.session.add(categoria)
        db.session.commit()

        # Crear artículo
        inventario = Inventario(
            codigo="TEST-ORDEN-001",
            nombre="Material Test Orden",
            categoria_id=categoria.id,
            unidad_medida="unidad",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("5"),
            stock_maximo=Decimal("200"),
            precio_unitario=Decimal("10.0"),
            activo=True,
        )
        db.session.add(inventario)
        db.session.commit()

        # Crear primer lote (más antiguo)
        lote1 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario.id,
            cantidad=50.0,
            precio_unitario=10.0,
            codigo_lote="LOTE-PRIMERO",
            documento_origen="DOC-001",
            usuario_id="test_user",
        )

        # Esperar un momento para asegurar diferencia en timestamp
        import time

        time.sleep(0.01)

        # Crear segundo lote (más reciente)
        lote2 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario.id,
            cantidad=75.0,
            precio_unitario=12.0,
            codigo_lote="LOTE-SEGUNDO",
            documento_origen="DOC-002",
            usuario_id="test_user",
        )

        db.session.commit()

        # Verificar orden de creación
        assert lote1.fecha_entrada < lote2.fecha_entrada

        # Consumir cantidad que requiera ambos lotes
        lotes_consumidos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario.id,
            cantidad_total=80.0,  # 50 del primero + 30 del segundo
            documento_referencia="CONSUMO-ORDEN-001",
            usuario_id="test_user",
        )

        db.session.commit()

        # Verificar orden de consumo FIFO
        assert faltante == 0
        assert len(lotes_consumidos) == 2

        # Primer consumo debe ser del lote más antiguo (completo)
        primer_consumo = lotes_consumidos[0]
        assert primer_consumo[0].id == lote1.id
        assert primer_consumo[1] == 50.0

        # Segundo consumo debe ser del lote más reciente (parcial)
        segundo_consumo = lotes_consumidos[1]
        assert segundo_consumo[0].id == lote2.id
        assert segundo_consumo[1] == 30.0

        # Verificar estados finales
        db.session.refresh(lote1)
        db.session.refresh(lote2)

        assert lote1.cantidad_actual == Decimal("0")  # Completamente consumido
        assert lote2.cantidad_actual == Decimal("45")  # 75 - 30 = 45


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_stock_insuficiente_integracion(app, client):
    """
    Test de integración para manejo de stock insuficiente
    """
    with app.app_context():
        # Crear categoría
        categoria = Categoria(nombre="Test Stock", descripcion="Para testing stock")
        db.session.add(categoria)
        db.session.commit()

        # Crear artículo
        inventario = Inventario(
            codigo="TEST-STOCK-001",
            nombre="Material Stock Test",
            categoria_id=categoria.id,
            unidad_medida="litro",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("1"),
            stock_maximo=Decimal("50"),
            precio_unitario=Decimal("15.0"),
            activo=True,
        )
        db.session.add(inventario)
        db.session.commit()

        # Crear lote con cantidad limitada
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario.id,
            cantidad=25.0,
            precio_unitario=15.0,
            codigo_lote="LOTE-LIMITADO",
            documento_origen="DOC-LIMIT-001",
            usuario_id="test_user",
        )

        db.session.commit()

        # Intentar consumir más de lo disponible
        lotes_consumidos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario.id,
            cantidad_total=40.0,  # Más de los 25 disponibles
            documento_referencia="CONSUMO-EXCESO",
            usuario_id="test_user",
        )

        db.session.commit()

        # Verificar manejo correcto del stock insuficiente
        assert faltante == 15.0  # 40 - 25 = 15 faltante
        assert len(lotes_consumidos) == 1

        lote_consumido, cantidad_consumida = lotes_consumidos[0]
        assert lote_consumido.id == lote.id
        assert cantidad_consumida == 25.0  # Se consumió todo lo disponible

        # Verificar estado del lote
        db.session.refresh(lote)
        assert lote.cantidad_actual == Decimal("0")


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_multiples_operaciones_secuenciales(app, client):
    """
    Test de múltiples operaciones FIFO secuenciales
    """
    with app.app_context():
        # Crear categoría
        categoria = Categoria(nombre="Test Multi", descripcion="Para testing múltiple")
        db.session.add(categoria)
        db.session.commit()

        # Crear artículo
        inventario = Inventario(
            codigo="TEST-MULTI-001",
            nombre="Material Multi Test",
            categoria_id=categoria.id,
            unidad_medida="metro",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("20"),
            stock_maximo=Decimal("500"),
            precio_unitario=Decimal("8.0"),
            activo=True,
        )
        db.session.add(inventario)
        db.session.commit()

        # Secuencia de operaciones de una semana de trabajo

        # Día 1: Entrada inicial
        lote1 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario.id,
            cantidad=200.0,
            precio_unitario=8.0,
            codigo_lote="LOTE-DIA1",
            documento_origen="RECEPCION-001",
            usuario_id="almacenero",
        )

        # Día 2: Consumo pequeño
        consumo1, faltante1 = ServicioFIFO.consumir_fifo(
            inventario_id=inventario.id,
            cantidad_total=50.0,
            documento_referencia="ORDEN-001",
            usuario_id="operador1",
        )

        # Día 3: Nueva entrada
        lote2 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario.id,
            cantidad=150.0,
            precio_unitario=8.5,
            codigo_lote="LOTE-DIA3",
            documento_origen="RECEPCION-002",
            usuario_id="almacenero",
        )

        # Día 4: Consumo grande
        consumo2, faltante2 = ServicioFIFO.consumir_fifo(
            inventario_id=inventario.id,
            cantidad_total=180.0,
            documento_referencia="ORDEN-002",
            usuario_id="operador2",
        )

        db.session.commit()

        # Verificaciones finales
        assert faltante1 == 0  # Primer consumo OK
        assert faltante2 == 0  # Segundo consumo OK

        # Verificar que el primer lote se agotó
        db.session.refresh(lote1)
        assert lote1.cantidad_actual == Decimal("0")  # 200 - 50 - 150 = 0

        # Verificar estado del segundo lote
        db.session.refresh(lote2)
        # Consumo2 toma 150 del lote1 (que quedaban) + 30 del lote2
        expected_lote2 = Decimal("150") - Decimal("30")  # 180 - 150 restantes del lote1
        assert lote2.cantidad_actual == expected_lote2

        # Verificar total de stock restante
        stock_restante = sum(
            lote.cantidad_actual
            for lote in LoteInventario.query.filter_by(
                inventario_id=inventario.id
            ).all()
        )

        total_entradas = Decimal("200") + Decimal("150")  # 350
        total_consumos = Decimal("50") + Decimal("180")  # 230
        expected_stock = total_entradas - total_consumos  # 120

        assert stock_restante == expected_stock
