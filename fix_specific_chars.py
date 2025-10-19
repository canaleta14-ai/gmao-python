#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir caracteres UTF-8 específicos problemáticos
"""


def fix_specific_chars():
    file_path = "static/js/ordenes.js"

    try:
        # Leer archivo
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # Reemplazos específicos para caracteres problemáticos
        # Usamos códigos de caracteres para evitar problemas de codificación
        content = content.replace('Ã"', "Ó")  # Ó mal codificado

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ Caracteres específicos corregidos")

            # Contar reemplazos
            changes = (
                len(original)
                - len(content)
                + (len(content.split("Ó")) - len(original.split("Ó")))
            )
            print(f"Se corrigieron caracteres problemáticos")
        else:
            print("ℹ️ No hay cambios específicos")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    fix_specific_chars()
