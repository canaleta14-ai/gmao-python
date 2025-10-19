#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo para corregir todos los problemas de codificación UTF-8
"""
import os
import glob


def fix_encoding_in_file(file_path):
    """Corrige problemas de codificación en un archivo"""

    # Mapeo de caracteres mal codificados a correctos
    replacements = {
        # Emojis y símbolos
        "🔧": "🔧",
        "🔧": "🔧",
        # Casos específicos mal codificados
        "Ó": "Ó",
        "Órdenes": "Órdenes",
        # Casos específicos de git log
        "ñ": "ñ",
        "ú": "ú",
        "á": "á",
        "ó": "ó",
        "í": "í",
        "é": "é",
    }

    try:
        # Leer archivo
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        original_content = content
        changes_count = 0

        # Aplicar reemplazos
        for wrong, correct in replacements.items():
            if wrong in content:
                count = content.count(wrong)
                content = content.replace(wrong, correct)
                changes_count += count
                print(
                    f"  ✅ {file_path}: Corregido '{wrong}' → '{correct}' ({count} veces)"
                )

        # Guardar solo si hubo cambios
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ {file_path}: {changes_count} correcciones aplicadas")
            return True

        return False

    except Exception as e:
        print(f"❌ Error en {file_path}: {e}")
        return False


def main():
    """Procesar todos los archivos relevantes"""

    # Extensiones a procesar
    extensions = ["*.js", "*.py", "*.html", "*.css", "*.md", "*.txt"]

    # Directorios a procesar
    directories = [
        "static/js",
        "app/templates",
        "static/css",
        ".",  # raíz para archivos .md y .txt
    ]

    print("🔧 Iniciando corrección de codificación UTF-8...\n")

    files_processed = 0
    files_changed = 0

    for directory in directories:
        for ext in extensions:
            pattern = os.path.join(directory, "**", ext) if directory != "." else ext
            files = glob.glob(pattern, recursive=True)

            for file_path in files:
                # Saltar archivos de node_modules, venv, etc.
                if any(
                    x in file_path
                    for x in ["node_modules", ".venv", "__pycache__", ".git"]
                ):
                    continue

                files_processed += 1
                if fix_encoding_in_file(file_path):
                    files_changed += 1

    print(f"\n📊 Resumen:")
    print(f"   Archivos procesados: {files_processed}")
    print(f"   Archivos corregidos: {files_changed}")
    print(f"\n✅ Corrección completada!")


if __name__ == "__main__":
    main()
