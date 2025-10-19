"""
Tests unitarios para ServicioFIFO
Prueba la funcionalidad completa del sistema FIFO de gestión de lotes
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from app.services.servicio_fifo import ServicioFIFO
from app.models.inventario import Inventario
from app.models.categoria import Categoria
from app.models.lote_inventario import LoteInventario, MovimientoLote
from app.extensions import db


class TestServicioFIFO:
    """Suite de tests para ServicioFIFO"""

    @pytest.fixture
    def categoria_test(self, db_session):
        """Crear categoría de prueba"""
        categoria = Categoria(nombre="Categoria Test", prefijo="TST")
        db.session.add(categoria)
        db.session.commit()
        return categoria

    @pytest.fixture
    def inventario_test(self, db_session, categoria_test):
        """Crear artículo de inventario de prueba"""
        inventario = Inventario(
            codigo="TST-FIFO-001",
            descripcion="Artículo para pruebas FIFO",
            categoria_id=categoria_test.id,
            stock_actual=0,
            stock_minimo=10,
            stock_maximo=100,
            activo=True,
        )
        db.session.add(inventario)
        db.session.commit()
        return inventario

    def test_crear_lote_entrada_exitoso(self, client, db_session, inventario_test):
        """Debe crear un lote de entrada correctamente"""
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=50,
            precio_unitario=10.50,
            codigo_lote="LOTE-001",
            usuario_id="test_user",
        )

        assert lote is not None
        assert lote.inventario_id == inventario_test.id
        assert float(lote.cantidad_inicial) == 50
        assert float(lote.cantidad_actual) == 50
        assert float(lote.precio_unitario) == 10.50
        assert float(lote.costo_total) == 525.00  # 50 * 10.50
        assert lote.codigo_lote == "LOTE-001"

    def test_crear_lote_con_cantidad_negativa_falla(
        self, client, db_session, inventario_test
    ):
        """Debe fallar al crear lote con cantidad negativa"""
        with pytest.raises(ValueError) as excinfo:
            ServicioFIFO.crear_lote_entrada(
                inventario_id=inventario_test.id,
                cantidad=-10,
                precio_unitario=10.50,
                usuario_id="test_user",
            )
        assert "cantidad del lote debe ser positiva" in str(excinfo.value).lower()

    def test_crear_lote_con_cantidad_cero_falla(
        self, client, db_session, inventario_test
    ):
        """Debe fallar al crear lote con cantidad cero"""
        with pytest.raises(ValueError) as excinfo:
            ServicioFIFO.crear_lote_entrada(
                inventario_id=inventario_test.id,
                cantidad=0,
                precio_unitario=10.50,
                usuario_id="test_user",
            )
        assert "cantidad del lote debe ser positiva" in str(excinfo.value).lower()

    def test_crear_lote_inventario_inexistente_falla(self, client, db_session):
        """Debe fallar al crear lote para inventario que no existe"""
        with pytest.raises(ValueError) as excinfo:
            ServicioFIFO.crear_lote_entrada(
                inventario_id=99999,  # ID inexistente
                cantidad=10,
                precio_unitario=5.00,
                usuario_id="test_user",
            )
        assert "no encontrado" in str(excinfo.value).lower()

    def test_consumir_fifo_orden_correcto(self, client, db_session, inventario_test):
        """Debe consumir lotes en orden FIFO (primero el más antiguo)"""
        # Crear 3 lotes con diferentes fechas
        lote1 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=10,
            precio_unitario=5.00,
            codigo_lote="LOTE-OLD",
            usuario_id="test_user",
        )

        # Forzar fecha más antigua
        lote1.fecha_entrada = datetime.now(timezone.utc) - timedelta(days=10)
        db.session.commit()

        lote2 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=20,
            precio_unitario=6.00,
            codigo_lote="LOTE-MED",
            usuario_id="test_user",
        )

        lote2.fecha_entrada = datetime.now(timezone.utc) - timedelta(days=5)
        db.session.commit()

        lote3 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=30,
            precio_unitario=7.00,
            codigo_lote="LOTE-NEW",
            usuario_id="test_user",
        )

        # Consumir 25 unidades - debe consumir todo lote1 (10) y parte de lote2 (15)
        consumos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_test.id, cantidad_total=25, usuario_id="test_user"
        )
        db.session.commit()

        assert faltante == 0
        assert len(consumos) == 2

        # Verificar orden FIFO
        assert consumos[0][0].codigo_lote == "LOTE-OLD"
        assert consumos[0][1] == 10  # Todo el lote1
        assert consumos[1][0].codigo_lote == "LOTE-MED"
        assert consumos[1][1] == 15  # Parte del lote2

        # Verificar cantidades actuales
        db.session.refresh(lote1)
        db.session.refresh(lote2)
        db.session.refresh(lote3)

        assert float(lote1.cantidad_actual) == 0
        assert float(lote2.cantidad_actual) == 5
        assert float(lote3.cantidad_actual) == 30  # No tocado

    def test_consumir_fifo_stock_insuficiente(
        self, client, db_session, inventario_test
    ):
        """Debe manejar correctamente cuando no hay suficiente stock"""
        # Crear lote con 10 unidades
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=10,
            precio_unitario=5.00,
            usuario_id="test_user",
        )

        # Intentar consumir 20 unidades (más de lo disponible)
        consumos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_test.id, cantidad_total=20, usuario_id="test_user"
        )
        db.session.commit()

        assert len(consumos) == 1
        assert consumos[0][1] == 10  # Solo pudo consumir 10
        assert faltante == 10  # Faltan 10 unidades

        db.session.refresh(lote)
        assert float(lote.cantidad_actual) == 0

    def test_consumir_fifo_excluye_lotes_vencidos(
        self, client, db_session, inventario_test
    ):
        """Debe excluir lotes vencidos por defecto"""
        # Crear lote vencido
        lote_vencido = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=50,
            precio_unitario=5.00,
            codigo_lote="LOTE-VENCIDO",
            usuario_id="test_user",
        )
        lote_vencido.fecha_vencimiento = datetime.now(timezone.utc) - timedelta(days=1)
        db.session.commit()

        # Intentar consumir - no debe usar el lote vencido
        consumos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_test.id, cantidad_total=10, usuario_id="test_user"
        )

        assert len(consumos) == 0
        assert faltante == 10

    def test_reservar_stock_exitoso(self, client, db_session, inventario_test):
        """Debe reservar stock correctamente"""
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=100,
            precio_unitario=5.00,
            usuario_id="test_user",
        )

        # Reservar 30 unidades
        reservas, faltante = ServicioFIFO.reservar_stock(
            inventario_id=inventario_test.id,
            cantidad_total=30,
            orden_trabajo_id=1,
            usuario_id="test_user",
        )
        db.session.commit()

        assert faltante == 0
        assert len(reservas) == 1
        assert reservas[0][1] == 30

        db.session.refresh(lote)
        assert float(lote.cantidad_actual) == 100  # No cambia
        assert float(lote.cantidad_reservada) == 30  # Se reservó
        assert lote.cantidad_disponible == 70  # 100 - 30

    def test_liberar_reservas_exitoso(self, client, db_session, inventario_test):
        """Debe liberar reservas correctamente"""
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=100,
            precio_unitario=5.00,
            usuario_id="test_user",
        )

        # Reservar
        ServicioFIFO.reservar_stock(
            inventario_id=inventario_test.id,
            cantidad_total=30,
            orden_trabajo_id=1,
            usuario_id="test_user",
        )
        db.session.commit()

        db.session.refresh(lote)
        assert float(lote.cantidad_reservada) == 30

        # Liberar
        liberaciones = ServicioFIFO.liberar_reservas(
            orden_trabajo_id=1, usuario_id="test_user"
        )
        db.session.commit()

        assert len(liberaciones) == 1
        assert liberaciones[0][1] == 30

        db.session.refresh(lote)
        assert float(lote.cantidad_reservada) == 0
        assert lote.cantidad_disponible == 100

    def test_obtener_stock_disponible(self, client, db_session, inventario_test):
        """Debe obtener información detallada de stock"""
        # Crear varios lotes
        lote1 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=50,
            precio_unitario=5.00,
            codigo_lote="LOTE-1",
            usuario_id="test_user",
        )

        lote2 = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=30,
            precio_unitario=6.00,
            codigo_lote="LOTE-2",
            usuario_id="test_user",
        )

        # Reservar algo del lote1
        ServicioFIFO.reservar_stock(
            inventario_id=inventario_test.id,
            cantidad_total=10,
            orden_trabajo_id=1,
            usuario_id="test_user",
        )
        db.session.commit()

        stock_info = ServicioFIFO.obtener_stock_disponible(inventario_test.id)

        assert stock_info["inventario_id"] == inventario_test.id
        assert stock_info["total_actual"] == 80  # 50 + 30
        assert stock_info["total_reservado"] == 10
        assert stock_info["total_disponible"] == 70  # 80 - 10
        assert stock_info["numero_lotes"] == 2
        assert len(stock_info["lotes"]) == 2

    def test_movimientos_registrados_correctamente(
        self, client, db_session, inventario_test
    ):
        """Debe registrar movimientos de lote correctamente"""
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=100,
            precio_unitario=5.00,
            usuario_id="test_user",
        )

        # Consumir
        ServicioFIFO.consumir_fifo(
            inventario_id=inventario_test.id,
            cantidad_total=20,
            documento_referencia="DOC-001",
            usuario_id="test_user",
        )
        db.session.commit()

        # Verificar movimiento registrado
        movimientos = MovimientoLote.query.filter_by(lote_id=lote.id).all()
        assert len(movimientos) == 1
        assert movimientos[0].tipo_movimiento == "consumo"
        assert float(movimientos[0].cantidad) == 20
        assert movimientos[0].documento_referencia == "DOC-001"
        assert movimientos[0].usuario_id == "test_user"

    def test_consumir_multiples_lotes_fifo(self, client, db_session, inventario_test):
        """Debe consumir de múltiples lotes respetando FIFO"""
        # Crear 5 lotes pequeños
        for i in range(5):
            lote = ServicioFIFO.crear_lote_entrada(
                inventario_id=inventario_test.id,
                cantidad=10,
                precio_unitario=5.00 + i,
                codigo_lote=f"LOTE-{i+1}",
                usuario_id="test_user",
            )
            lote.fecha_entrada = datetime.now(timezone.utc) - timedelta(days=10 - i)
            db.session.commit()

        # Consumir 35 unidades - debe usar 4 lotes completos (10 cada uno) y 5 del quinto
        consumos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=inventario_test.id, cantidad_total=35, usuario_id="test_user"
        )
        db.session.commit()

        assert faltante == 0
        assert len(consumos) == 4  # Usó 4 lotes

        # Verificar orden
        for i, (lote, cantidad) in enumerate(consumos):
            if i < 3:
                assert cantidad == 10  # Lotes 1-3 consumidos completamente
            else:
                assert cantidad == 5  # Lote 4 parcialmente consumido

    def test_validacion_cantidad_negativa_consumo(
        self, client, db_session, inventario_test
    ):
        """El modelo debe validar cantidades negativas en consumo"""
        lote = ServicioFIFO.crear_lote_entrada(
            inventario_id=inventario_test.id,
            cantidad=100,
            precio_unitario=5.00,
            usuario_id="test_user",
        )

        # Intentar consumir cantidad negativa directamente en el modelo
        with pytest.raises(ValueError) as excinfo:
            lote.consumir(-10)

        assert "no puede ser negativa" in str(excinfo.value).lower()
