#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir problemas de codificación en archivos JavaScript
"""

import os
import glob


def fix_encoding_in_file(filepath):
    """Corregir problemas de codificación en un archivo específico"""
    print(f"Procesando: {filepath}")

    # Mapeo de caracteres malformados a caracteres correctos
    replacements = {
        # Vocales con tildes
        "á": "á",
        "é": "é",
        "í": "í",
        "ó": "ó",
        "ú": "ú",
        "ú": "ú",
        # Eñe
        "ñ": "ñ",
        # Emojis y símbolos
        "✅": "✅",
        "❌": "❌",
        "🔧": "🔧",
        "🔍": "🔍",
        "🔄": "🔄",
        "🎯": "🎯",
        "⚡": "⚡",
        "🚀": "🚀",
        "⚙️": "⚙️",
        "🔹": "🔹",
        "👤": "👤",
        "🔔": "🔔",
        "": "",
        "1.": "1.",
        "2.": "2.",
        "3.": "3.",
        # Comillas y apostrofes
        "'": "'",
        """"""""# Guiones
        "–": "–",
        "—": "—",
        # Otros símbolos
        "¢": "¢",
    }

    try:
        # Leer archivo
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Aplicar reemplazos
        original_content = content
        for bad_char, good_char in replacements.items():
            content = content.replace(bad_char, good_char)

        # Solo escribir si hubo cambios
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Corregido: {filepath}")
            return True
        else:
            print(f"  ℹ️  Sin cambios: {filepath}")
            return False

    except Exception as e:
        print(f"  ❌ Error procesando {filepath}: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Iniciando corrección de codificación...")

    # Patrones de archivos a procesar
    patterns = ["static/js/*.js", "app/**/*.py", "templates/**/*.html", "*.py"]

    total_files = 0
    fixed_files = 0

    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        for filepath in files:
            if os.path.isfile(filepath):
                total_files += 1
                if fix_encoding_in_file(filepath):
                    fixed_files += 1

    print(f"\n📊 Resumen:")
    print(f"  📁 Archivos procesados: {total_files}")
    print(f"  ✅ Archivos corregidos: {fixed_files}")
    print(f"  ℹ️  Sin cambios: {total_files - fixed_files}")
    print("🎉 ¡Corrección de codificación completada!")


if __name__ == "__main__":
    main()
