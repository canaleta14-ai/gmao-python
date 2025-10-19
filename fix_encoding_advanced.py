#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script avanzado para corregir problemas de codificación UTF-8 en JavaScript
"""
import re


def fix_advanced_encoding(file_path):
    """Corrige problemas avanzados de codificación en archivos"""

    try:
        # Leer el archivo
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Reemplazos específicos con patrones más precisos
        patterns = [
            (r'Ã"rdenes', "Órdenes"),
            (r'GESTIÃ"N', "GESTIÓN"),
            (r"mÃ\sx\.", "máx."),
            (r"ï£¿Ã¼ÃŸÏ€", "🔧"),
        ]

        changes_made = 0
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                changes_made += len(matches)
                print(
                    f"✅ Corregido {len(matches)} instancias de: {pattern} -> {replacement}"
                )

        # Guardar solo si hubo cambios
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Total de correcciones: {changes_made} en {file_path}")
            return True
        else:
            print(f"ℹ️ No hay cambios en: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False


if __name__ == "__main__":
    archivo = r"C:\Users\canal\gmao-python\gmao-sistema\static\js\ordenes.js"
    fix_advanced_encoding(archivo)
