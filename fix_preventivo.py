#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir codificación UTF-8 en preventivo.js
"""


def fix_preventivo_js():
    file_path = "static/js/preventivo.js"

    try:
        # Leer archivo
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # Reemplazos básicos comunes
        basic_replacements = {
            "Ã³": "ó",
            "Ã¡": "á",
            "Ã©": "é",
            "Ã­": "í",
            "Ãº": "ú",
            "Ã±": "ñ",
        }

        # Aplicar reemplazos básicos
        for wrong, correct in basic_replacements.items():
            if wrong in content:
                count = content.count(wrong)
                content = content.replace(wrong, correct)
                print(f"✅ Corregido {count} instancias de: {wrong} -> {correct}")

        # Reemplazos específicos para preventivo.js
        specific_replacements = [
            ("aÃ±o", "año"),
            ("especÃ­ficas", "específicas"),
            ("selecciÃ³n", "selección"),
            ("FunciÃ³n", "Función"),
            ("bÃºsquedas", "búsquedas"),
            ("pÃ¡gina", "página"),
            ("MÃ³dulo", "Módulo"),
            ("paginaciÃ³n", "paginación"),
            ("estadÃ­sticas", "estadísticas"),
            ("dÃ­as", "días"),
            ("Ãšltima", "Última"),
            ('Ã"rdenes', "Órdenes"),
            ("Â¬Ã¸", "¿"),
            ("Â¿", "¿"),
        ]

        for wrong, correct in specific_replacements:
            if wrong in content:
                count = content.count(wrong)
                content = content.replace(wrong, correct)
                print(f"✅ Corregido {count} instancias de: {wrong} -> {correct}")

        # Guardar si hubo cambios
        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Archivo {file_path} corregido exitosamente")
            return True
        else:
            print(f"ℹ️ No hay cambios en: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False


if __name__ == "__main__":
    fix_preventivo_js()
