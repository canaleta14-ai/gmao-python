#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corregir caracteres corruptos en ordenes.js
"""


def fix_encoding():
    # Mapeo de caracteres corruptos a caracteres correctos
    replacements = {
        "ó": "ó",
        "ñ": "ñ",
        "é": "é",
        "√∂": "ò",
        "√¡": "á",
        "ú": "ú",
        "√Ä": "Á",
        "√É": "É",
        "√Ñ": "Ñ",
        "√ì": "Ó",
        "á": "à",
        "√®": "í",
        "√ü": "ì",
        "ú": "ú",
        "í": "í",
        "vàlid": "válid",
        "pàgin": "págin",
        "✅": "✅",
        "búsq": "búsq",
        "estadíst": "estadíst",
        "Crític": "Críti",
        "extraíd": "extraíd",
        "específ": "específ",
        "títul": "títul",
        "vací": "vací",
    }

    file_path = r"c:\gmao - copia\static\js\ordenes.js"

    try:
        # Leer el archivo
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Aplicar todas las correcciones
        for corrupt, correct in replacements.items():
            content = content.replace(corrupt, correct)

        # Escribir el archivo corregido
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Archivo ordenes.js corregido exitosamente")

    except Exception as e:
        print(f"❌ Error al corregir el archivo: {e}")


if __name__ == "__main__":
    fix_encoding()
