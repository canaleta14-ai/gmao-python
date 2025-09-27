#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.inventario import PeriodoInventario

app = create_app()

with app.app_context():
    # Imprimir los campos del modelo PeriodoInventario
    print("📋 CAMPOS DEL MODELO PeriodoInventario:")
    print("=" * 50)

    for column in PeriodoInventario.__table__.columns:
        print(f"  - {column.name}: {column.type}")

    print("\n🏗️ INTENTANDO CREAR PERÍODO DE PRUEBA:")
    print("=" * 50)

    try:
        # Intentar crear un período simple
        periodo = PeriodoInventario(año=2025, mes=9, usuario_responsable="Test")
        print("  ✅ Modelo creado exitosamente (sin guardarlo)")
        print(f"  - Año: {periodo.año}")
        print(f"  - Mes: {periodo.mes}")
        print(f"  - Usuario responsable: {periodo.usuario_responsable}")

    except Exception as e:
        print(f"  ❌ Error al crear el modelo: {e}")

    print("\n🧪 VERIFICANDO MÉTODOS DISPONIBLES:")
    print("=" * 50)

    métodos = [attr for attr in dir(PeriodoInventario) if not attr.startswith("_")]
    for método in métodos[:10]:  # Mostrar solo los primeros 10
        print(f"  - {método}")

    if len(métodos) > 10:
        print(f"  ... y {len(métodos) - 10} más")
