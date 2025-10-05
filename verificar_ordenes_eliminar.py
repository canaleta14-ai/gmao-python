#!/usr/bin/env python3
"""
Script para verificar las órdenes de trabajo y sus estados
para confirmar que el botón de eliminar debería aparecer.
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.factory import create_app
from app.models.orden_trabajo import OrdenTrabajo

def verificar_ordenes():
    """Verificar las órdenes de trabajo y sus estados"""
    app = create_app()
    
    with app.app_context():
        print("=== VERIFICACIÓN DE ÓRDENES DE TRABAJO ===\n")
        
        # Obtener todas las órdenes
        ordenes = OrdenTrabajo.query.all()
        
        if not ordenes:
            print("❌ No hay órdenes de trabajo en la base de datos")
            return
        
        print(f"📊 Total de órdenes: {len(ordenes)}\n")
        
        # Contar por estado
        estados = {}
        ordenes_eliminables = []
        
        for orden in ordenes:
            estado = orden.estado
            if estado not in estados:
                estados[estado] = 0
            estados[estado] += 1
            
            # Verificar si es eliminable
            if estado in ['Pendiente', 'Cancelada']:
                ordenes_eliminables.append(orden)
        
        # Mostrar estadísticas por estado
        print("📈 Órdenes por estado:")
        for estado, cantidad in estados.items():
            print(f"   {estado}: {cantidad}")
        
        print(f"\n🗑️  Órdenes eliminables (Pendiente/Cancelada): {len(ordenes_eliminables)}")
        
        if ordenes_eliminables:
            print("\n📋 Órdenes que deberían mostrar botón de eliminar:")
            for orden in ordenes_eliminables[:10]:  # Mostrar máximo 10
                print(f"   - Orden #{orden.id} ({orden.numero_orden}) - Estado: {orden.estado}")
                print(f"     Fecha: {orden.fecha_creacion}")
                print(f"     Tipo: {orden.tipo}")
                print()
        else:
            print("\n⚠️  No hay órdenes eliminables en el sistema")
            print("   Para probar la funcionalidad, necesitas órdenes con estado 'Pendiente' o 'Cancelada'")
        
        print("\n=== VERIFICACIÓN COMPLETADA ===")

if __name__ == "__main__":
    verificar_ordenes()