#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script completo para limpiar todos los caracteres corruptos en ordenes.js
"""


def fix_all_encoding():
    file_path = r"c:\gmao - copia\static\js\ordenes.js"

    try:
        # Leer el archivo
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Mapeo completo de correcciones
        replacements = {
            # Caracteres comunes con √
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
            # Palabras específicas comunes
            "vàlid": "válid",
            "pàgin": "págin",
            "búsq": "búsq",
            "estadíst": "estadíst",
            "Crític": "Críti",
            "extraíd": "extraíd",
            "específ": "específ",
            "títul": "títul",
            "vací": "vací",
            # Símbolos especiales
            "✅": "✅",
            "⚙️": "⚙️",
            "¢": "€",
            # Caracteres aislados problemáticos
            "√": "",
            "‚": "",
            "∫": "",
            "≠": "",
            "≤": "",
            "≥": "",
            # Reemplazos de caracteres corruptos por su equivalente
            "àlid": "álid",
            "àgin": "ágin",
            "úsq": "úsq",
            "ístic": "ístic",
            "ítica": "ítica",
            "íd": "íd",
            "ífica": "ífica",
            "ítulo": "ítulo",
            "ía": "ía",
        }

        # Aplicar todas las correcciones
        for corrupt, correct in replacements.items():
            content = content.replace(corrupt, correct)

        # Limpiar secuencias de caracteres no válidos
        import re

        # Eliminar caracteres de control no válidos
        content = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", content)

        # Escribir el archivo corregido
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Archivo ordenes.js completamente corregido")

        # Verificar que no queden caracteres problemáticos
        problematic_chars = ["√", "‚", "∫", "≠", "≤", "≥"]
        remaining_issues = []
        for char in problematic_chars:
            if char in content:
                remaining_issues.append(char)

        if remaining_issues:
            print(f"⚠️  Aún quedan algunos caracteres: {remaining_issues}")
        else:
            print("✅ Todos los caracteres problemáticos han sido limpiados")

    except Exception as e:
        print(f"❌ Error al corregir el archivo: {e}")


if __name__ == "__main__":
    fix_all_encoding()
