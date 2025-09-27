#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script para verificar los datos de activos en la base de datos

import sqlite3
import json
from datetime import datetime


def verificar_activos():
    print("🔍 Verificando datos de activos en la base de datos...\n")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect("instance/database.db")
        cursor = conn.cursor()

        # Consultar todos los activos
        cursor.execute(
            """
            SELECT id, codigo, nombre, estado, activo, departamento, tipo 
            FROM activo 
            ORDER BY id
        """
        )

        activos = cursor.fetchall()

        if not activos:
            print("❌ No se encontraron activos en la base de datos")
            return

        print(f"📊 Encontrados {len(activos)} activos:\n")

        activos_activos = 0
        activos_desactivados = 0

        print("| ID | Código | Nombre | Estado | Activo | Departamento | Tipo |")
        print("|----|---------|--------|--------|---------|--------------|------|")

        for activo in activos:
            id_act, codigo, nombre, estado, activo_bool, departamento, tipo = activo
            estado_str = "✅ SÍ" if activo_bool else "❌ NO"

            if activo_bool:
                activos_activos += 1
            else:
                activos_desactivados += 1

            print(
                f'| {id_act} | {codigo or "N/A"} | {nombre[:20]}... | {estado or "N/A"} | {estado_str} | {departamento or "N/A"} | {tipo or "N/A"} |'
            )

        print(f"\n📈 Resumen:")
        print(f"   • Activos ACTIVOS: {activos_activos}")
        print(f"   • Activos DESACTIVADOS: {activos_desactivados}")
        print(f"   • Total: {len(activos)}")

        # Verificar estructura de tabla
        cursor.execute("PRAGMA table_info(activo)")
        columnas = cursor.fetchall()

        print(f'\n🗂️ Estructura de la tabla "activo":')
        for col in columnas:
            print(
                f'   • {col[1]} ({col[2]}) - {"NOT NULL" if col[3] else "NULL"} - Default: {col[4] or "None"}'
            )

        conn.close()
        print(f'\n✅ Verificación completada - {datetime.now().strftime("%H:%M:%S")}')

    except Exception as e:
        print(f"❌ Error al verificar activos: {str(e)}")


if __name__ == "__main__":
    verificar_activos()
