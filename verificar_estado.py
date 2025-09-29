#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación final del estado del plan
"""

import sqlite3


def verificar_estado():
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT codigo_plan, nombre, proxima_ejecucion, generacion_automatica 
        FROM plan_mantenimiento 
        WHERE codigo_plan = 'PM-2025-0001'
    """
    )

    result = cursor.fetchone()
    print("🔍 ESTADO ACTUAL DEL PLAN PM-2025-0001:")
    print("=" * 45)
    print(f"Plan: {result[0]} - {result[1]}")
    print(f"Próxima ejecución: {result[2]}")
    print(f"Generación automática: {result[3]}")

    # Evaluar estado
    if result[3] == 1:
        print("✅ Generación automática: HABILITADA")
    else:
        print("❌ Generación automática: DESHABILITADA")

    if "2025-09-29" in result[2]:
        print("✅ Fecha corregida: OK")
    else:
        print("❌ Fecha aún incorrecta")

    conn.close()


if __name__ == "__main__":
    verificar_estado()
