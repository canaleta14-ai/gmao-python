#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el plan PM-2025-0001
"""

import sqlite3
from datetime import datetime


def corregir_plan():
    print("🔧 CORRIGIENDO PLAN PM-2025-0001")
    print("=" * 40)

    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    # Mostrar estado actual
    cursor.execute(
        """
        SELECT codigo_plan, nombre, proxima_ejecucion, generacion_automatica 
        FROM plan_mantenimiento 
        WHERE codigo_plan = 'PM-2025-0001'
    """
    )

    plan_actual = cursor.fetchone()
    print(f"📋 Estado ANTES:")
    print(f"   Plan: {plan_actual[0]} - {plan_actual[1]}")
    print(f"   Próxima ejecución: {plan_actual[2]}")
    print(f"   Generación automática: {plan_actual[3]}")

    # Corregir el plan
    nueva_fecha = "2025-09-29 06:00:00"
    cursor.execute(
        """
        UPDATE plan_mantenimiento 
        SET generacion_automatica = 1,
            proxima_ejecucion = ?
        WHERE codigo_plan = 'PM-2025-0001'
    """,
        (nueva_fecha,),
    )

    conn.commit()

    # Mostrar estado corregido
    cursor.execute(
        """
        SELECT codigo_plan, nombre, proxima_ejecucion, generacion_automatica 
        FROM plan_mantenimiento 
        WHERE codigo_plan = 'PM-2025-0001'
    """
    )

    plan_corregido = cursor.fetchone()
    print(f"\n✅ Estado DESPUÉS:")
    print(f"   Plan: {plan_corregido[0]} - {plan_corregido[1]}")
    print(f"   Próxima ejecución: {plan_corregido[2]}")
    print(f"   Generación automática: {plan_corregido[3]}")

    conn.close()

    print(f"\n🎯 CAMBIOS REALIZADOS:")
    print(f"   ✅ Generación automática: HABILITADA")
    print(f"   ✅ Próxima ejecución: Lunes 29/09/2025 06:00")
    print(f"   ✅ Ahora el plan se ejecutará automáticamente")


if __name__ == "__main__":
    corregir_plan()
