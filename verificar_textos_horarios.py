#!/usr/bin/env python3
"""
Verificar que todos los textos informativos muestren la hora correcta (6:00 AM)
"""
import os
import re


def buscar_referencias_hora():
    """Buscar referencias a horarios en archivos relevantes"""
    print("🔍 VERIFICANDO REFERENCIAS DE HORARIOS")
    print("=" * 50)

    archivos_revisar = [
        "app/templates/preventivo/preventivo.html",
        "static/js/preventivo.js",
        "static/js/main.js",
    ]

    patrones = [
        r"11:00",
        r"once",
        r"11 AM",
        r"11:00 AM",
        r"6:00",
        r"seis",
        r"6 AM",
        r"6:00 AM",
    ]

    referencias_encontradas = []

    for archivo in archivos_revisar:
        if os.path.exists(archivo):
            print(f"\n📄 Revisando: {archivo}")
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    lineas = contenido.split("\n")

                    for num_linea, linea in enumerate(lineas, 1):
                        for patron in patrones:
                            if re.search(patron, linea, re.IGNORECASE):
                                print(f"   Línea {num_linea}: {linea.strip()}")
                                referencias_encontradas.append(
                                    {
                                        "archivo": archivo,
                                        "linea": num_linea,
                                        "contenido": linea.strip(),
                                        "patron": patron,
                                    }
                                )
            except Exception as e:
                print(f"   ❌ Error al leer archivo: {e}")
        else:
            print(f"   ⚠️ Archivo no encontrado: {archivo}")

    print(f"\n📊 RESUMEN:")
    print(f"   • Total referencias encontradas: {len(referencias_encontradas)}")

    # Verificar que tenemos 6:00 AM y no 11:00 AM
    referencias_6am = [
        r
        for r in referencias_encontradas
        if re.search(r"6:00|6 AM", r["contenido"], re.IGNORECASE)
    ]
    referencias_11am = [
        r
        for r in referencias_encontradas
        if re.search(r"11:00|11 AM", r["contenido"], re.IGNORECASE)
    ]

    print(f"   • Referencias a 6:00 AM: {len(referencias_6am)}")
    print(f"   • Referencias a 11:00 AM: {len(referencias_11am)}")

    if len(referencias_11am) > 0:
        print(
            "\n❌ ATENCIÓN: Aún hay referencias a 11:00 AM que deberían actualizarse:"
        )
        for ref in referencias_11am:
            print(f"   • {ref['archivo']}:{ref['linea']} - {ref['contenido']}")
        return False
    else:
        print("\n✅ PERFECTO: No hay referencias obsoletas a 11:00 AM")
        if len(referencias_6am) > 0:
            print("✅ Se encontraron referencias correctas a 6:00 AM")
        return True


if __name__ == "__main__":
    print(f"📅 Fecha de verificación: 28 de septiembre de 2025")
    print(f"🕕 Hora nueva del scheduler: 6:00 AM")
    print()

    if buscar_referencias_hora():
        print("\n🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ Todos los textos informativos están actualizados correctamente")
    else:
        print("\n⚠️ VERIFICACIÓN INCOMPLETA")
        print("❌ Hay textos que aún necesitan actualización")
