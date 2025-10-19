#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir problemas de codificación en archivos JavaScript
"""


def fix_encoding_issues(file_path):
    """Corrige problemas comunes de codificación en archivos"""

    # Diccionario de reemplazos más comunes
    replacements = {
        "Ã³": "ó",
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ãº": "ú",
        "Ã±": "ñ",
        "GestiÃ³n": "Gestión",
        'Ã"rdenes': "Órdenes",
        "paginaciÃ³n": "paginación",
        "selecciÃ³n": "selección",
        "FunciÃ³n": "Función",
        "bÃºsquedas": "búsquedas",
        "parÃ¡metro": "parámetro",
        "versiÃ³n": "versión",
        "InicializaciÃ³n": "Inicialización",
        "pÃ¡gina": "página",
        "MÃ³dulo": "Módulo",
        "Ã³rdenes": "órdenes",
        "autenticaciÃ³n": "autenticación",
        'GESTIÃ"N': "GESTIÓN",
        "mÃ x.": "máx.",
        "ï£¿Ã¼ÃŸÏ€": "🔧",
        "aÃ±o": "año",
        "especÃ­ficas": "específicas",
        "estadÃ­sticas": "estadísticas",
        "dÃ­as": "días",
        "ï£¿ðŸ"§": "🔧",
        "ðŸ"": "🔍",
        "ðŸ"Ž": "🔎", 
        "âœ…": "✅"
    }

    try:
        # Leer el archivo
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Aplicar reemplazos
        for wrong, correct in replacements.items():
            content = content.replace(wrong, correct)

        # Guardar solo si hubo cambios
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Archivo corregido: {file_path}")
            return True
        else:
            print(f"ℹ️ No hay cambios en: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False


if __name__ == "__main__":
    archivos = [
        r"C:\Users\canal\gmao-python\gmao-sistema\static\js\preventivo.js",
        r"C:\Users\canal\gmao-python\gmao-sistema\static\js\ordenes.js",
        r"C:\Users\canal\gmao-python\gmao-sistema\static\js\proveedores.js",
        r"C:\Users\canal\gmao-python\gmao-sistema\static\js\usuarios.js",
    ]

    for archivo in archivos:
        fix_encoding_issues(archivo)
