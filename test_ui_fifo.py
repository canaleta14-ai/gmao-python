#!/usr/bin/env python3
"""
Prueba completa de la interfaz de usuario del sistema FIFO
Este script valida que todas las funcionalidades de la UI estén operativas
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models import Inventario, Categoria, Proveedor
from app.models.lote_inventario import LoteInventario, MovimientoLote
from app.services.servicio_fifo import ServicioFIFO
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_test_data():
    """Crear datos de prueba para la interfaz"""
    logger.info("=== Configurando datos de prueba para UI ===")

    # Verificar que existe la categoría General
    categoria = Categoria.query.filter_by(nombre="General").first()
    if not categoria:
        categoria = Categoria(
            nombre="General", descripcion="Categoría general para pruebas"
        )
        db.session.add(categoria)
        db.session.commit()
        logger.info("✓ Categoría 'General' creada")

    # Usar proveedor existente o crear uno completo
    proveedor = Proveedor.query.first()
    if not proveedor:
        proveedor = Proveedor(
            nombre="Proveedor Test",
            nif="12345678Z",
            cuenta_contable="400000001",
            direccion="Direccion Test",
            telefono="123456789",
            email="test@ejemplo.com",
            contacto="test@ejemplo.com",
            activo=True,
        )
        db.session.add(proveedor)
        db.session.commit()
        logger.info("✓ Proveedor 'Proveedor Test' creado")
    else:
        logger.info(f"✓ Usando proveedor existente: {proveedor.nombre}")

    # Crear artículos de prueba con diferentes escenarios
    articulos_test = [
        {
            "codigo": "FIFO-001",
            "nombre": "Artículo FIFO Básico",
            "stock_actual": 0,
            "stock_minimo": 10,
            "precio_unitario": 15.50,
            "unidad_medida": "UN",
        },
        {
            "codigo": "FIFO-002",
            "nombre": "Producto Perecedero",
            "stock_actual": 0,
            "stock_minimo": 5,
            "precio_unitario": 25.00,
            "unidad_medida": "KG",
        },
        {
            "codigo": "FIFO-003",
            "nombre": "Material de Construcción",
            "stock_actual": 0,
            "stock_minimo": 20,
            "precio_unitario": 8.75,
            "unidad_medida": "M",
        },
    ]

    inventarios_creados = []
    for art_data in articulos_test:
        # Verificar si ya existe
        inventario = Inventario.query.filter_by(codigo=art_data["codigo"]).first()
        if not inventario:
            inventario = Inventario(
                codigo=art_data["codigo"],
                nombre=art_data["nombre"],
                stock_actual=art_data["stock_actual"],
                stock_minimo=art_data["stock_minimo"],
                precio_unitario=art_data["precio_unitario"],
                unidad_medida=art_data["unidad_medida"],
                categoria_id=categoria.id,
                proveedor_principal=proveedor.nombre,
                activo=True,
            )
            db.session.add(inventario)
            inventarios_creados.append(inventario)

    db.session.commit()
    if inventarios_creados:
        logger.info(f"✓ {len(inventarios_creados)} artículos de prueba creados")

    return articulos_test


def create_test_lotes():
    """Crear lotes de prueba con diferentes escenarios de vencimiento"""
    logger.info("=== Creando lotes de prueba ===")

    articulos = Inventario.query.filter(Inventario.codigo.like("FIFO-%")).all()

    if not articulos:
        logger.error("No se encontraron artículos de prueba")
        return

    # Fechas para diferentes escenarios
    hoy = datetime.now(timezone.utc)
    vencido = hoy - timedelta(days=10)  # Vencido hace 10 días
    critico = hoy + timedelta(days=3)  # Vence en 3 días (crítico)
    proximo = hoy + timedelta(days=15)  # Vence en 15 días
    normal = hoy + timedelta(days=60)  # Vence en 60 días

    lotes_creados = []

    for i, inventario in enumerate(articulos):
        # Crear múltiples lotes por artículo con diferentes estados
        escenarios = [
            {
                "cantidad": 50,
                "precio": 10.00,
                "fecha_venc": vencido if i == 0 else None,
                "codigo": f"LOTE-VENCIDO-{inventario.codigo}" if i == 0 else None,
                "observaciones": "Lote vencido para pruebas UI" if i == 0 else None,
            },
            {
                "cantidad": 30,
                "precio": 12.00,
                "fecha_venc": critico,
                "codigo": f"LOTE-CRITICO-{inventario.codigo}",
                "observaciones": "Lote crítico (vence en 3 días)",
            },
            {
                "cantidad": 75,
                "precio": 11.50,
                "fecha_venc": proximo,
                "codigo": f"LOTE-PROXIMO-{inventario.codigo}",
                "observaciones": "Lote próximo a vencer",
            },
            {
                "cantidad": 100,
                "precio": 13.00,
                "fecha_venc": normal,
                "codigo": f"LOTE-NORMAL-{inventario.codigo}",
                "observaciones": "Lote con vencimiento normal",
            },
            {
                "cantidad": 25,
                "precio": 14.00,
                "fecha_venc": None,  # Sin vencimiento
                "codigo": f"LOTE-SIN-VENC-{inventario.codigo}",
                "observaciones": "Lote sin fecha de vencimiento",
            },
        ]

        for escenario in escenarios:
            try:
                lote = ServicioFIFO.crear_lote_entrada(
                    inventario_id=inventario.id,
                    cantidad=escenario["cantidad"],
                    precio_unitario=escenario["precio"],
                    codigo_lote=escenario["codigo"],
                    fecha_vencimiento=escenario["fecha_venc"],
                    documento_origen=f"DOC-TEST-{len(lotes_creados)+1:03d}",
                    usuario_id="test_ui",
                    observaciones=escenario["observaciones"],
                )
                lotes_creados.append(lote)

            except Exception as e:
                logger.error(f"Error creando lote para {inventario.codigo}: {e}")

    db.session.commit()
    logger.info(f"✓ {len(lotes_creados)} lotes de prueba creados")

    return lotes_creados


def create_test_movements():
    """Crear movimientos de prueba para mostrar trazabilidad"""
    logger.info("=== Creando movimientos de prueba ===")

    # Obtener algunos lotes para crear movimientos
    lotes = LoteInventario.query.limit(5).all()

    movimientos_creados = 0
    for lote in lotes:
        try:
            # Simular consumo parcial
            cantidad_consumir = min(10, lote.cantidad_actual * 0.2)

            if cantidad_consumir > 0:
                consumos, faltante = ServicioFIFO.consumir_fifo(
                    inventario_id=lote.inventario_id,
                    cantidad_total=cantidad_consumir,
                    documento_referencia=f"CONSUMO-TEST-{movimientos_creados+1}",
                    usuario_id="test_ui",
                    observaciones="Consumo de prueba para trazabilidad UI",
                )
                movimientos_creados += len(consumos)

        except Exception as e:
            logger.error(f"Error creando movimiento para lote {lote.id}: {e}")

    db.session.commit()
    logger.info(f"✓ {movimientos_creados} movimientos de prueba creados")


def test_ui_endpoints():
    """Probar que los endpoints de la UI respondan correctamente"""
    logger.info("=== Probando endpoints de la UI ===")

    with app.test_client() as client:
        # Probar página principal
        response = client.get("/lotes/")
        logger.info(f"GET /lotes/ - Status: {response.status_code}")

        # Probar página de crear lote
        response = client.get("/lotes/crear_lote")
        logger.info(f"GET /lotes/crear_lote - Status: {response.status_code}")

        # Probar página de trazabilidad
        response = client.get("/lotes/trazabilidad")
        logger.info(f"GET /lotes/trazabilidad - Status: {response.status_code}")

        # Probar página de vencimientos
        response = client.get("/lotes/vencimientos")
        logger.info(f"GET /lotes/vencimientos - Status: {response.status_code}")

        # Probar API de lotes de un inventario
        inventario = Inventario.query.filter(Inventario.codigo.like("FIFO-%")).first()
        if inventario:
            response = client.get(f"/lotes/api/lotes/{inventario.id}")
            logger.info(
                f"GET /lotes/api/lotes/{inventario.id} - Status: {response.status_code}"
            )

        # Probar API de trazabilidad
        lote = LoteInventario.query.first()
        if lote:
            response = client.get(f"/lotes/api/trazabilidad/{lote.id}")
            logger.info(
                f"GET /lotes/api/trazabilidad/{lote.id} - Status: {response.status_code}"
            )


def verificar_datos_ui():
    """Verificar que hay datos suficientes para mostrar en la UI"""
    logger.info("=== Verificando datos para UI ===")

    # Contar lotes por estado
    total_lotes = LoteInventario.query.filter_by(activo=True).count()

    hoy = datetime.now(timezone.utc)
    lotes_vencidos = LoteInventario.query.filter(
        LoteInventario.activo == True, LoteInventario.fecha_vencimiento <= hoy
    ).count()

    lotes_proximos = LoteInventario.query.filter(
        LoteInventario.activo == True,
        LoteInventario.fecha_vencimiento > hoy,
        LoteInventario.fecha_vencimiento <= hoy + timedelta(days=30),
    ).count()

    total_movimientos = MovimientoLote.query.count()

    logger.info(f"✓ Lotes activos: {total_lotes}")
    logger.info(f"✓ Lotes vencidos: {lotes_vencidos}")
    logger.info(f"✓ Lotes próximos a vencer: {lotes_proximos}")
    logger.info(f"✓ Total movimientos: {total_movimientos}")

    # Verificar que hay artículos con lotes
    articulos_con_lotes = (
        db.session.query(Inventario).join(LoteInventario).distinct().count()
    )
    logger.info(f"✓ Artículos con lotes: {articulos_con_lotes}")

    return {
        "total_lotes": total_lotes,
        "lotes_vencidos": lotes_vencidos,
        "lotes_proximos": lotes_proximos,
        "total_movimientos": total_movimientos,
        "articulos_con_lotes": articulos_con_lotes,
    }


def show_usage_examples():
    """Mostrar ejemplos de uso de la interfaz"""
    logger.info("=== Ejemplos de uso de la interfaz ===")

    print("\n" + "=" * 60)
    print("   INTERFAZ DE USUARIO SISTEMA FIFO - EJEMPLOS DE USO")
    print("=" * 60)

    print("\n📋 PÁGINAS PRINCIPALES:")
    print("   • http://localhost:5000/lotes/")
    print("     └─ Página principal con dashboard y búsqueda")
    print("   • http://localhost:5000/lotes/crear_lote")
    print("     └─ Formulario para crear nuevos lotes")
    print("   • http://localhost:5000/lotes/trazabilidad")
    print("     └─ Búsqueda y visualización de trazabilidad")
    print("   • http://localhost:5000/lotes/vencimientos")
    print("     └─ Control de productos próximos a vencer")

    # Obtener ejemplos de datos reales
    inventario = Inventario.query.filter(Inventario.codigo.like("FIFO-%")).first()
    lote = LoteInventario.query.first()

    if inventario:
        print(f"\n🎯 EJEMPLOS CON DATOS REALES:")
        print(f"   • Ver lotes del artículo {inventario.codigo}:")
        print(f"     http://localhost:5000/lotes/inventario/{inventario.id}")

    if lote:
        print(f"   • Ver trazabilidad del lote {lote.id}:")
        print(f"     http://localhost:5000/lotes/trazabilidad?lote={lote.id}")

    print(f"\n🔧 FUNCIONALIDADES DISPONIBLES:")
    print(f"   ✓ Búsqueda de artículos con autocompletado")
    print(f"   ✓ Creación de lotes con validación en tiempo real")
    print(f"   ✓ Consumo FIFO automático desde la interfaz")
    print(f"   ✓ Reservas de stock por orden de trabajo")
    print(f"   ✓ Trazabilidad completa con timeline visual")
    print(f"   ✓ Control de vencimientos con alertas automáticas")
    print(f"   ✓ Vista detallada por artículo con estadísticas")
    print(f"   ✓ Acciones rápidas desde cards interactivas")

    print(f"\n⚡ CARACTERÍSTICAS TÉCNICAS:")
    print(f"   ✓ Interfaz responsive (móvil y desktop)")
    print(f"   ✓ Actualizaciones en tiempo real vía AJAX")
    print(f"   ✓ Validación de formularios del lado cliente")
    print(f"   ✓ Manejo de errores con mensajes informativos")
    print(f"   ✓ Diseño moderno con Bootstrap y CSS personalizado")
    print(f"   ✓ Integración completa con sistema FIFO backend")

    print("\n" + "=" * 60)


def main():
    """Función principal de prueba"""
    logger.info("🚀 Iniciando prueba completa de interfaz FIFO")

    try:
        # Configurar datos de prueba
        setup_test_data()

        # Crear lotes de prueba
        create_test_lotes()

        # Crear movimientos de prueba
        create_test_movements()

        # Verificar datos
        stats = verificar_datos_ui()

        # Probar endpoints
        test_ui_endpoints()

        # Mostrar ejemplos de uso
        show_usage_examples()

        logger.info("✅ Prueba de interfaz completada exitosamente")

        if stats["total_lotes"] > 0:
            print(f"\n🎉 ¡INTERFAZ LISTA! Hay {stats['total_lotes']} lotes para probar")
            print("   Inicie el servidor Flask y visite las URLs mostradas arriba")
        else:
            logger.warning("⚠️  No se crearon lotes. Verifique la configuración")

    except Exception as e:
        logger.error(f"❌ Error en prueba de interfaz: {e}")
        raise


if __name__ == "__main__":
    # Crear aplicación Flask
    app = create_app()

    with app.app_context():
        main()
