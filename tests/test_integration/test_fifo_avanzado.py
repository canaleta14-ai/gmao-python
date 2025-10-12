"""
Test de integración avanzado para el sistema FIFO.
Simula escenarios reales de producción con múltiples artículos y operaciones complejas.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.extensions import db
from app.models.inventario import Inventario
from app.models.lote_inventario import LoteInventario, MovimientoLote
from app.models.categoria import Categoria
from app.models.orden_trabajo import OrdenTrabajo
from app.services.servicio_fifo import ServicioFIFO


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_escenario_produccion_completo(app, client):
    """
    Test de escenario de producción completo:
    - Múltiples materiales
    - Múltiples órdenes de trabajo
    - Entradas y consumos intercalados
    - Verificación de trazabilidad
    """
    with app.app_context():
        # SETUP: Crear estructura de datos
        categoria_mp = Categoria(nombre="Materia Prima", descripcion="Materias primas")
        categoria_cons = Categoria(
            nombre="Consumibles", descripcion="Materiales consumibles"
        )
        db.session.add_all([categoria_mp, categoria_cons])
        db.session.commit()

        # Crear materiales de diferentes tipos
        material_acero = Inventario(
            codigo="MP-ACERO-001",
            nombre="Acero inoxidable 316L",
            categoria_id=categoria_mp.id,
            unidad_medida="kg",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("100"),
            stock_maximo=Decimal("1000"),
            precio_unitario=Decimal("15.75"),
            activo=True,
        )

        material_soldadura = Inventario(
            codigo="CONS-SOLD-001",
            nombre="Electrodo soldadura E308L",
            categoria_id=categoria_cons.id,
            unidad_medida="kg",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("20"),
            stock_maximo=Decimal("200"),
            precio_unitario=Decimal("12.50"),
            activo=True,
        )

        db.session.add_all([material_acero, material_soldadura])
        db.session.commit()

        # ESCENARIO SEMANA 1: Recepción inicial de materiales

        # Lunes: Llega acero del proveedor A
        lote_acero_prov_a = ServicioFIFO.crear_lote_entrada(
            inventario_id=material_acero.id,
            cantidad=500.0,
            precio_unitario=15.50,
            codigo_lote="ACERO-PROV-A-001",
            documento_origen="FACTURA-A-2024-001",
            proveedor_id=1,
            usuario_id="almacenero",
            observaciones="Primera entrega proveedor A",
        )

        # Miércoles: Llega soldadura
        lote_soldadura = ServicioFIFO.crear_lote_entrada(
            inventario_id=material_soldadura.id,
            cantidad=50.0,
            precio_unitario=12.00,
            codigo_lote="SOLD-001-2024",
            documento_origen="FACTURA-SOLD-001",
            proveedor_id=2,
            usuario_id="almacenero",
        )

        # Viernes: Llega más acero del proveedor B (precio diferente)
        lote_acero_prov_b = ServicioFIFO.crear_lote_entrada(
            inventario_id=material_acero.id,
            cantidad=300.0,
            precio_unitario=16.20,
            codigo_lote="ACERO-PROV-B-001",
            documento_origen="FACTURA-B-2024-001",
            proveedor_id=3,
            usuario_id="almacenero",
            observaciones="Primera entrega proveedor B",
        )

        db.session.commit()

        # ESCENARIO SEMANA 2: Inicio de producción

        # Orden de trabajo 1: Fabricación de tanque pequeño
        ot_1_acero, faltante_1a = ServicioFIFO.consumir_fifo(
            inventario_id=material_acero.id,
            cantidad_total=150.0,
            orden_trabajo_id=2024001,
            documento_referencia="OT-2024-001",
            usuario_id="operador_juan",
            observaciones="Fabricación tanque 500L - Acero",
        )

        ot_1_soldadura, faltante_1s = ServicioFIFO.consumir_fifo(
            inventario_id=material_soldadura.id,
            cantidad_total=8.0,
            orden_trabajo_id=2024001,
            documento_referencia="OT-2024-001",
            usuario_id="soldador_maria",
            observaciones="Fabricación tanque 500L - Soldadura",
        )

        # Orden de trabajo 2: Fabricación de tanque grande
        ot_2_acero, faltante_2a = ServicioFIFO.consumir_fifo(
            inventario_id=material_acero.id,
            cantidad_total=400.0,
            orden_trabajo_id=2024002,
            documento_referencia="OT-2024-002",
            usuario_id="operador_carlos",
            observaciones="Fabricación tanque 1000L - Acero",
        )

        ot_2_soldadura, faltante_2s = ServicioFIFO.consumir_fifo(
            inventario_id=material_soldadura.id,
            cantidad_total=15.0,
            orden_trabajo_id=2024002,
            documento_referencia="OT-2024-002",
            usuario_id="soldador_ana",
            observaciones="Fabricación tanque 1000L - Soldadura",
        )

        db.session.commit()

        # VERIFICACIONES DEL ESCENARIO

        # 1. Verificar que no hubo faltantes
        assert faltante_1a == 0, "No debería faltar acero para OT-001"
        assert faltante_1s == 0, "No debería faltar soldadura para OT-001"
        assert faltante_2a == 0, "No debería faltar acero para OT-002"
        assert faltante_2s == 0, "No debería faltar soldadura para OT-002"

        # 2. Verificar orden FIFO correcto para acero
        # OT-001 debe haber consumido solo del proveedor A (más antiguo)
        assert len(ot_1_acero) == 1
        assert ot_1_acero[0][0].id == lote_acero_prov_a.id
        assert ot_1_acero[0][1] == 150.0

        # OT-002 debe haber consumido resto del proveedor A + parte del proveedor B
        assert len(ot_2_acero) == 2
        assert ot_2_acero[0][0].id == lote_acero_prov_a.id  # Resto del lote A
        assert ot_2_acero[0][1] == 350.0  # 500 - 150 = 350
        assert ot_2_acero[1][0].id == lote_acero_prov_b.id  # Parte del lote B
        assert ot_2_acero[1][1] == 50.0  # 400 - 350 = 50

        # 3. Verificar estados finales de lotes
        db.session.refresh(lote_acero_prov_a)
        db.session.refresh(lote_acero_prov_b)
        db.session.refresh(lote_soldadura)

        assert lote_acero_prov_a.cantidad_actual == Decimal("0")  # Agotado
        assert lote_acero_prov_b.cantidad_actual == Decimal("250")  # 300 - 50 = 250
        assert lote_soldadura.cantidad_actual == Decimal("27")  # 50 - 8 - 15 = 27

        # 4. Verificar trazabilidad de movimientos
        movimientos_acero = (
            MovimientoLote.query.join(LoteInventario)
            .filter(LoteInventario.inventario_id == material_acero.id)
            .all()
        )

        movimientos_soldadura = (
            MovimientoLote.query.join(LoteInventario)
            .filter(LoteInventario.inventario_id == material_soldadura.id)
            .all()
        )

        # Debe haber 3 movimientos de acero (1 para OT-001, 2 para OT-002)
        assert len(movimientos_acero) == 3

        # Debe haber 2 movimientos de soldadura (1 para cada OT)
        assert len(movimientos_soldadura) == 2

        # 5. Verificar que los movimientos tienen la información correcta
        for mov in movimientos_acero:
            assert mov.orden_trabajo_id in [2024001, 2024002]
            assert mov.tipo_movimiento == "consumo"
            assert mov.usuario_id in ["operador_juan", "operador_carlos"]

        for mov in movimientos_soldadura:
            assert mov.orden_trabajo_id in [2024001, 2024002]
            assert mov.tipo_movimiento == "consumo"
            assert mov.usuario_id in ["soldador_maria", "soldador_ana"]


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_con_fechas_vencimiento_avanzado(app, client):
    """
    Test avanzado de FIFO con fechas de vencimiento (FEFO - First Expired, First Out)
    """
    with app.app_context():
        # Crear categoría y material perecedero
        categoria = Categoria(nombre="Químicos", descripcion="Productos químicos")
        db.session.add(categoria)
        db.session.commit()

        quimico = Inventario(
            codigo="QUIM-001",
            nombre="Reactivo químico especial",
            categoria_id=categoria.id,
            unidad_medida="litro",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("10"),
            stock_maximo=Decimal("100"),
            precio_unitario=Decimal("45.80"),
            activo=True,
        )
        db.session.add(quimico)
        db.session.commit()

        hoy = datetime.now()

        # Crear lotes con diferentes fechas de vencimiento
        # Lote que vence en 15 días (prioridad más alta)
        lote_vence_pronto = ServicioFIFO.crear_lote_entrada(
            inventario_id=quimico.id,
            cantidad=25.0,
            precio_unitario=45.00,
            codigo_lote="QUIM-PRONTO",
            fecha_vencimiento=hoy + timedelta(days=15),
            documento_origen="COMPRA-QUIM-001",
            usuario_id="almacenero",
        )

        # Lote que vence en 60 días (entrada antes)
        lote_vence_medio = ServicioFIFO.crear_lote_entrada(
            inventario_id=quimico.id,
            cantidad=40.0,
            precio_unitario=46.50,
            codigo_lote="QUIM-MEDIO",
            fecha_vencimiento=hoy + timedelta(days=60),
            documento_origen="COMPRA-QUIM-002",
            usuario_id="almacenero",
        )

        # Lote que vence en 90 días (más nuevo)
        lote_vence_tarde = ServicioFIFO.crear_lote_entrada(
            inventario_id=quimico.id,
            cantidad=30.0,
            precio_unitario=47.20,
            codigo_lote="QUIM-TARDE",
            fecha_vencimiento=hoy + timedelta(days=90),
            documento_origen="COMPRA-QUIM-003",
            usuario_id="almacenero",
        )

        db.session.commit()

        # Consumo que requiere múltiples lotes
        lotes_consumidos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=quimico.id,
            cantidad_total=70.0,
            documento_referencia="CONSUMO-QUIM-001",
            usuario_id="operador_lab",
            observaciones="Proceso de laboratorio urgente",
        )

        db.session.commit()

        # VERIFICACIONES FEFO
        assert faltante == 0
        assert len(lotes_consumidos) == 3  # Debe usar los 3 lotes

        # Verificar orden de consumo por fecha de vencimiento
        # Primero: lote que vence en 15 días (completo)
        assert lotes_consumidos[0][0].id == lote_vence_pronto.id
        assert lotes_consumidos[0][1] == 25.0

        # Segundo: lote que vence en 60 días (completo)
        assert lotes_consumidos[1][0].id == lote_vence_medio.id
        assert lotes_consumidos[1][1] == 40.0

        # Tercero: lote que vence en 90 días (parcial)
        assert lotes_consumidos[2][0].id == lote_vence_tarde.id
        assert lotes_consumidos[2][1] == 5.0  # 70 - 25 - 40 = 5

        # Verificar estados finales
        db.session.refresh(lote_vence_pronto)
        db.session.refresh(lote_vence_medio)
        db.session.refresh(lote_vence_tarde)

        assert lote_vence_pronto.cantidad_actual == Decimal("0")  # Agotado
        assert lote_vence_medio.cantidad_actual == Decimal("0")  # Agotado
        assert lote_vence_tarde.cantidad_actual == Decimal("25")  # 30 - 5 = 25


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_performance_multiple_lotes(app, client):
    """
    Test de rendimiento del sistema FIFO con muchos lotes
    """
    with app.app_context():
        # Crear categoría y material
        categoria = Categoria(nombre="Performance", descripcion="Test de rendimiento")
        db.session.add(categoria)
        db.session.commit()

        material = Inventario(
            codigo="PERF-001",
            nombre="Material para test de rendimiento",
            categoria_id=categoria.id,
            unidad_medida="unidad",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("1"),
            stock_maximo=Decimal("10000"),
            precio_unitario=Decimal("1.00"),
            activo=True,
        )
        db.session.add(material)
        db.session.commit()

        # Crear muchos lotes pequeños (simular entradas frecuentes)
        num_lotes = 100
        cantidad_por_lote = 50

        import time

        inicio_creacion = time.time()

        for i in range(num_lotes):
            ServicioFIFO.crear_lote_entrada(
                inventario_id=material.id,
                cantidad=cantidad_por_lote,
                precio_unitario=1.00 + (i * 0.01),  # Precio ligeramente creciente
                codigo_lote=f"PERF-LOTE-{i:03d}",
                documento_origen=f"DOC-PERF-{i:03d}",
                usuario_id="test_performance",
            )

            # Commit cada 10 lotes para simular comportamiento real
            if (i + 1) % 10 == 0:
                db.session.commit()

        db.session.commit()
        tiempo_creacion = time.time() - inicio_creacion

        # Consumo que requiere muchos lotes
        inicio_consumo = time.time()

        lotes_consumidos, faltante = ServicioFIFO.consumir_fifo(
            inventario_id=material.id,
            cantidad_total=2500,  # 50 lotes completos
            documento_referencia="CONSUMO-PERF-001",
            usuario_id="test_performance",
        )

        tiempo_consumo = time.time() - inicio_consumo
        db.session.commit()

        # VERIFICACIONES DE PERFORMANCE Y FUNCIONALIDAD

        # Funcionalidad: consumo correcto
        assert faltante == 0
        assert len(lotes_consumidos) == 50  # Exactamente 50 lotes

        # Verificar orden FIFO correcto
        for i, (lote, cantidad) in enumerate(lotes_consumidos):
            expected_codigo = f"PERF-LOTE-{i:03d}"
            assert expected_codigo in lote.codigo_lote
            assert cantidad == cantidad_por_lote

        # Performance: no debe tomar demasiado tiempo
        assert tiempo_creacion < 5.0, f"Creación de lotes tardó {tiempo_creacion:.2f}s"
        assert tiempo_consumo < 2.0, f"Consumo FIFO tardó {tiempo_consumo:.2f}s"

        # Verificar stock restante
        stock_restante = sum(
            lote.cantidad_actual
            for lote in LoteInventario.query.filter_by(inventario_id=material.id).all()
        )

        expected_stock = (num_lotes * cantidad_por_lote) - 2500  # 5000 - 2500 = 2500
        assert stock_restante == Decimal(str(expected_stock))

        print(f"Performance Test Results:")
        print(f"  - Tiempo creación {num_lotes} lotes: {tiempo_creacion:.3f}s")
        print(f"  - Tiempo consumo FIFO 50 lotes: {tiempo_consumo:.3f}s")
        print(f"  - Stock final: {stock_restante}")


@pytest.mark.integration
@pytest.mark.fifo
def test_fifo_casos_edge_avanzados(app, client):
    """
    Test de casos edge avanzados del sistema FIFO
    """
    with app.app_context():
        # Crear categoría y material
        categoria = Categoria(nombre="Edge Cases", descripcion="Casos edge")
        db.session.add(categoria)
        db.session.commit()

        material = Inventario(
            codigo="EDGE-001",
            nombre="Material para casos edge",
            categoria_id=categoria.id,
            unidad_medida="kg",
            stock_actual=Decimal("0"),
            stock_minimo=Decimal("0"),
            stock_maximo=Decimal("1000"),
            precio_unitario=Decimal("10.00"),
            activo=True,
        )
        db.session.add(material)
        db.session.commit()

        # CASO 1: Consumo con cantidad exactamente cero
        lotes_zero, faltante_zero = ServicioFIFO.consumir_fifo(
            inventario_id=material.id,
            cantidad_total=0.0,
            documento_referencia="CONSUMO-ZERO",
            usuario_id="test_edge",
        )

        assert len(lotes_zero) == 0
        assert faltante_zero == 0

        # CASO 2: Crear lote con cantidad muy pequeña (decimales)
        lote_decimal = ServicioFIFO.crear_lote_entrada(
            inventario_id=material.id,
            cantidad=0.001,  # 1 gramo
            precio_unitario=10.00,
            codigo_lote="EDGE-DECIMAL",
            documento_origen="DOC-DECIMAL",
            usuario_id="test_edge",
        )

        # CASO 3: Consumir cantidad muy pequeña
        lotes_pequeno, faltante_pequeno = ServicioFIFO.consumir_fifo(
            inventario_id=material.id,
            cantidad_total=0.0005,  # 0.5 gramos
            documento_referencia="CONSUMO-PEQUENO",
            usuario_id="test_edge",
        )

        db.session.commit()

        # Verificaciones casos edge
        assert len(lotes_pequeno) == 1
        assert faltante_pequeno == 0
        assert lotes_pequeno[0][1] == 0.0005

        # Verificar precisión decimal
        db.session.refresh(lote_decimal)
        assert lote_decimal.cantidad_actual == Decimal("0.0005")  # 0.001 - 0.0005

        # CASO 4: Lote con cantidad negativa (debería fallar)
        with pytest.raises(ValueError):
            ServicioFIFO.crear_lote_entrada(
                inventario_id=material.id,
                cantidad=-10.0,  # Cantidad negativa
                precio_unitario=10.00,
                codigo_lote="EDGE-NEGATIVO",
                documento_origen="DOC-NEG",
                usuario_id="test_edge",
            )

        # CASO 5: Consumo de material inexistente
        with pytest.raises(ValueError):
            ServicioFIFO.consumir_fifo(
                inventario_id=99999,  # ID inexistente
                cantidad_total=10.0,
                documento_referencia="CONSUMO-INEXISTENTE",
                usuario_id="test_edge",
            )
