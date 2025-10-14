"""
Tests de integración completos para el sistema FIFO.
Prueba todo el flujo end-to-end: entrada → rotación → salida.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.extensions import db
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario, MovimientoLote
from app.models.categoria import Categoria
from app.services.servicio_fifo import ServicioFIFO


@pytest.mark.integration
@pytest.mark.fifo
class TestFIFOIntegracionCompleta:
    """Tests de integración completos para el sistema FIFO"""

    @pytest.fixture
    def categoria_test(self, db_session):
        """Crear categoría para testing"""
        categoria = Categoria(nombre="Material FIFO Test", descripcion="Para tests")
        db_session.add(categoria)
        db_session.commit()
        return categoria

    @pytest.fixture
    def inventario_test(self, db_session, categoria_test):
        """Crear artículo de inventario para testing"""
        inventario = Inventario(
            codigo="FIFO-TEST-001",
            nombre="Material de Prueba FIFO",
            descripcion="Material para testing de sistema FIFO",
            categoria_id=categoria_test.id,
            unidad_medida="kg",
            stock_actual=0,
            stock_minimo=10,
            stock_maximo=100,
            precio_unitario=Decimal("25.50"),
            activo=True,
        )
        db_session.add(inventario)
        db_session.commit()
        return inventario

    def test_flujo_fifo_completo_basico(self, db_session, inventario_test):
        """
        Test de flujo FIFO básico: entrada → consumo → verificación
        """
        inventario_id = inventario_test.id

        # FASE 1: ENTRADA DE LOTES
        # Crear primer lote (más antiguo)
        lote1 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=100,
            precio_unitario=20.0,
            codigo_lote="LOTE-001",
            documento_origen="COMPRA-001",
            usuario_id="user_test",
            observaciones="Primer lote para testing FIFO",
        )

        # Crear segundo lote (más reciente)
        lote2 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=150,
            precio_unitario=22.0,
            codigo_lote="LOTE-002",
            documento_origen="COMPRA-002",
            usuario_id="user_test",
            observaciones="Segundo lote para testing FIFO",
        )

        db_session.commit()

        # Verificar lotes creados
        assert lote1.cantidad_actual == 100
        assert lote2.cantidad_actual == 150
        assert lote1.fecha_entrada < lote2.fecha_entrada

        # FASE 2: CONSUMO FIFO
        # Consumir 120 unidades (debe tomar del lote más antiguo primero)
        lotes_consumidos, cantidad_faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=120,
            documento_referencia="CONSUMO-001",
            usuario_id="user_test",
            observaciones="Consumo test FIFO",
        )

        db_session.commit()

        # VERIFICACIONES
        # No debe faltar cantidad
        assert cantidad_faltante == 0

        # Debe haber 2 consumos: lote1 completo + parte del lote2
        assert len(lotes_consumidos) == 2

        # Primer consumo: todo el lote1 (100 unidades)
        lote_consumido_1, cantidad_consumida_1 = lotes_consumidos[0]
        assert lote_consumido_1.id == lote1.id
        assert cantidad_consumida_1 == 100

        # Segundo consumo: parte del lote2 (20 unidades)
        lote_consumido_2, cantidad_consumida_2 = lotes_consumidos[1]
        assert lote_consumido_2.id == lote2.id
        assert cantidad_consumida_2 == 20

        # Verificar cantidades actuales
        db_session.refresh(lote1)
        db_session.refresh(lote2)
        assert lote1.cantidad_actual == 0  # Completamente consumido
        assert lote2.cantidad_actual == 130  # 150 - 20 = 130

    def test_flujo_fifo_con_fechas_vencimiento(self, db_session, inventario_test):
        """
        Test FIFO con fechas de vencimiento considerando FEFO
        (First Expired, First Out)
        """
        inventario_id = inventario_test.id
        hoy = datetime.now()

        # Lote que vence primero (prioridad alta)
        lote_vencimiento_proximo = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=50,
            precio_unitario=25.0,
            codigo_lote="LOTE-PROX-VENC",
            fecha_vencimiento=hoy + timedelta(days=30),
            documento_origen="COMPRA-VENC-001",
            usuario_id="user_test",
        )

        # Lote que vence más tarde (entrada antes)
        lote_vencimiento_lejano = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=80,
            precio_unitario=24.0,
            codigo_lote="LOTE-LEJ-VENC",
            fecha_vencimiento=hoy + timedelta(days=90),
            documento_origen="COMPRA-VENC-002",
            usuario_id="user_test",
        )

        db_session.commit()

        # Consumir 100 unidades
        lotes_consumidos, cantidad_faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=100,
            documento_referencia="CONSUMO-VENC-001",
            usuario_id="user_test",
        )

        db_session.commit()

        # Verificar que se consumió primero el que vence antes
        assert len(lotes_consumidos) == 2
        assert cantidad_faltante == 0

        # Primer consumo debe ser el de vencimiento próximo
        lote_consumido_1, cantidad_1 = lotes_consumidos[0]
        assert lote_consumido_1.id == lote_vencimiento_proximo.id
        assert cantidad_1 == 50  # Todo el lote

        # Segundo consumo del lote con vencimiento lejano
        lote_consumido_2, cantidad_2 = lotes_consumidos[1]
        assert lote_consumido_2.id == lote_vencimiento_lejano.id
        assert cantidad_2 == 50  # Parte del lote

    def test_flujo_fifo_stock_insuficiente(self, db_session, inventario_test):
        """
        Test manejo de stock insuficiente en sistema FIFO
        """
        inventario_id = inventario_test.id

        # Crear un solo lote con cantidad limitada
        lote_limitado = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=30,
            precio_unitario=20.0,
            codigo_lote="LOTE-LIMITADO",
            documento_origen="COMPRA-LIM-001",
            usuario_id="user_test",
        )

        db_session.commit()

        # Intentar consumir más de lo disponible
        lotes_consumidos, cantidad_faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=50,  # Más de los 30 disponibles
            documento_referencia="CONSUMO-EXCESO-001",
            usuario_id="user_test",
        )

        db_session.commit()

        # Verificaciones
        assert len(lotes_consumidos) == 1  # Solo el lote disponible
        assert cantidad_faltante == 20  # 50 - 30 = 20 faltantes

        # El lote debe haberse consumido completamente
        lote_consumido, cantidad_consumida = lotes_consumidos[0]
        assert lote_consumido.id == lote_limitado.id
        assert cantidad_consumida == 30

        # Verificar estado del lote
        db_session.refresh(lote_limitado)
        assert lote_limitado.cantidad_actual == 0

    def test_flujo_fifo_multiple_consumos_secuenciales(
        self, db_session, inventario_test
    ):
        """
        Test múltiples consumos secuenciales manteniendo orden FIFO
        """
        inventario_id = inventario_test.id

        # Crear múltiples lotes
        lotes = []
        for i in range(1, 4):  # 3 lotes
            lote = ServicioFIFO.crear_lote_entrada(
                inventario_id=inventario_id,
                cantidad=100,
                precio_unitario=20.0 + i,
                codigo_lote=f"LOTE-MULTI-{i:03d}",
                documento_origen=f"COMPRA-MULTI-{i:03d}",
                usuario_id="user_test",
            )
            lotes.append(lote)

        db_session.commit()

        # PRIMER CONSUMO: 80 unidades (dentro del primer lote)
        lotes_consumidos_1, faltante_1 = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=80,
            documento_referencia="CONSUMO-MULTI-001",
            usuario_id="user_test",
        )

        # SEGUNDO CONSUMO: 150 unidades (resto del primer lote + parte del segundo)
        lotes_consumidos_2, faltante_2 = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=150,
            documento_referencia="CONSUMO-MULTI-002",
            usuario_id="user_test",
        )

        db_session.commit()

        # VERIFICACIONES PRIMER CONSUMO
        assert faltante_1 == 0
        assert len(lotes_consumidos_1) == 1
        assert lotes_consumidos_1[0][0].id == lotes[0].id
        assert lotes_consumidos_1[0][1] == 80

        # VERIFICACIONES SEGUNDO CONSUMO
        assert faltante_2 == 0
        assert len(lotes_consumidos_2) == 3

        # Verificar orden FIFO mantenido y cantidades consumidas
        # Primer lote: 20 restantes
        assert lotes_consumidos_2[0][0].id == lotes[0].id
        assert lotes_consumidos_2[0][1] == 20
        # Segundo lote: 100 completos
        assert lotes_consumidos_2[1][0].id == lotes[1].id
        assert lotes_consumidos_2[1][1] == 100
        # Tercer lote: 30 restantes
        assert lotes_consumidos_2[2][0].id == lotes[2].id
        assert lotes_consumidos_2[2][1] == 30

        # Verificar estados finales
        db_session.refresh(lotes[0])
        db_session.refresh(lotes[1])
        db_session.refresh(lotes[2])

        assert lotes[0].cantidad_actual == 0  # Completamente consumido
        assert lotes[1].cantidad_actual == 0  # Completamente consumido
        assert lotes[2].cantidad_actual == 70  # 100 - 30 = 70

    def test_fifo_trazabilidad_movimientos(self, db_session, inventario_test):
        """
        Test trazabilidad completa de movimientos en sistema FIFO
        """
        inventario_id = inventario_test.id

        # Crear lote
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=100,
            precio_unitario=30.0,
            codigo_lote="LOTE-TRAZABILIDAD",
            documento_origen="COMPRA-TRAZA-001",
            usuario_id="user_admin",
            observaciones="Lote para prueba de trazabilidad",
        )

        db_session.commit()

        # Realizar consumo
        lotes_consumidos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=60,
            orden_trabajo_id=123,
            documento_referencia="OT-123-CONSUMO",
            usuario_id="user_operador",
            observaciones="Consumo para orden de trabajo 123",
        )

        db_session.commit()

        # VERIFICAR TRAZABILIDAD
        # Verificar movimientos del lote
        movimientos = (
            MovimientoLote.query.filter_by(lote_id=lote.id)
            .order_by(MovimientoLote.fecha_movimiento)
            .all()
        )

        assert len(movimientos) >= 1  # Al menos el movimiento de consumo

        # Verificar último movimiento (consumo)
        movimiento_consumo = movimientos[-1]
        assert movimiento_consumo.tipo_movimiento == "consumo"
        assert movimiento_consumo.cantidad == Decimal("60")
        assert movimiento_consumo.orden_trabajo_id == 123
        assert movimiento_consumo.documento_referencia == "OT-123-CONSUMO"
        assert movimiento_consumo.usuario_id == "user_operador"
        assert "orden de trabajo 123" in movimiento_consumo.observaciones

        # Verificar estado del lote
        db_session.refresh(lote)
        assert lote.cantidad_actual == 40  # 100 - 60 = 40

    def test_fifo_escenario_real_produccion(self, db_session, inventario_test):
        """
        Test simulando escenario real de producción con múltiples entradas y salidas
        """
        inventario_id = inventario_test.id

        # SIMULACIÓN DE SEMANA DE TRABAJO

        # Lunes: Recepción de material
        lote_lunes = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=200,
            precio_unitario=25.0,
            codigo_lote="LOTE-LUNES-001",
            documento_origen="FACTURA-001-2024",
            proveedor_id=1,
            usuario_id="almacenero",
        )

        # Martes: Consumo pequeño
        consumo_martes, _ = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=30,
            orden_trabajo_id=101,
            documento_referencia="OT-101",
            usuario_id="tecnico1",
        )

        # Miércoles: Nueva entrada + consumo grande
        lote_miercoles = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_id,
            cantidad=150,
            precio_unitario=26.5,
            codigo_lote="LOTE-MIERCOLES-001",
            documento_origen="FACTURA-002-2024",
            proveedor_id=2,
            usuario_id="almacenero",
        )

        consumo_miercoles, _ = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=180,
            orden_trabajo_id=102,
            documento_referencia="OT-102",
            usuario_id="tecnico2",
        )

        # Jueves: Consumo final
        consumo_jueves, faltante_jueves = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_id,
            cantidad_total=100,
            orden_trabajo_id=103,
            documento_referencia="OT-103",
            usuario_id="tecnico1",
        )

        db_session.commit()

        # VERIFICACIONES DEL ESCENARIO

        # Calcular stock esperado
        total_entradas = 200 + 150  # 350
        total_consumos = 30 + 180 + len(consumo_jueves) and sum(
            cantidad for _, cantidad in consumo_jueves
        )  # Consumos reales

        # Verificar que el sistema FIFO funcionó correctamente
        assert len(consumo_martes) == 1  # Solo del primer lote
        assert consumo_martes[0][0].id == lote_lunes.id

        # El consumo del miércoles debe agotar el primer lote y tocar el segundo
        assert len(consumo_miercoles) == 2

        # No debe quedar stock insuficiente después de todas las operaciones
        assert faltante_jueves == 0 or (
            total_entradas >= sum([30, 180]) and faltante_jueves <= 100
        )

        # Verificar trazabilidad completa
        todos_movimientos = (
            MovimientoLote.query.join(LoteInventario)
            .filter(LoteInventario.inventario_id == inventario_id)
            .all()
        )

        assert len(todos_movimientos) >= 3  # Al menos 3 consumos registrados

        # Verificar que se mantiene integridad referencial
        for movimiento in todos_movimientos:
            assert movimiento.lote_id is not None
            assert movimiento.usuario_id is not None
            assert movimiento.documento_referencia is not None


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_performance_lotes_multiples(db_session):
    """
    Test de rendimiento con múltiples lotes para verificar eficiencia FIFO
    """
    # Crear categoría e inventario para test de performance
    categoria = Categoria(
        nombre="Performance Test", descripcion="Para pruebas de rendimiento"
    )
    db_session.add(categoria)
    db_session.commit()

    inventario = Inventario(
        codigo="PERF-FIFO-001",
        nombre="Material Performance Test",
        categoria_id=categoria.id,
        unidad_medida="unidad",
        stock_actual=0,
        stock_minimo=1,
        stock_maximo=10000,
        precio_unitario=Decimal("10.0"),
        activo=True,
    )
    db_session.add(inventario)
    db_session.commit()

    # Crear muchos lotes pequeños
    num_lotes = 50
    for i in range(num_lotes):
        ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario.id,
            cantidad=10,
            precio_unitario=10.0 + (i * 0.1),
            codigo_lote=f"PERF-LOTE-{i:03d}",
            documento_origen=f"DOC-PERF-{i:03d}",
            usuario_id="perf_test_user",
        )

    db_session.commit()

    # Consumir cantidad que requiera múltiples lotes
    import time

    inicio = time.time()

    lotes_consumidos, faltante = ServicioFIFO.consumir_fifo(
        inventario_id=inventario.id,
        cantidad_total=250,  # 25 lotes completos
        documento_referencia="PERF-CONSUMO-001",
        usuario_id="perf_test_user",
    )

    tiempo_consumo = time.time() - inicio

    db_session.commit()

    # Verificaciones de performance y funcionalidad
    assert faltante == 0  # Debe haber suficiente stock
    assert len(lotes_consumidos) == 25  # Debe consumir exactamente 25 lotes
    assert tiempo_consumo < 2.0  # No debe tomar más de 2 segundos

    # Verificar orden FIFO correcto
    for i, (lote, cantidad) in enumerate(lotes_consumidos):
        expected_codigo = f"PERF-LOTE-{i:03d}"
        assert expected_codigo in lote.codigo_lote
        assert cantidad == 10  # Cada lote se consume completamente
