#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Corrección específica para main.js
with open("static/js/main.js", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Correcciones específicas
fixes = {
    "CONFIGURACI√ìN": "CONFIGURACIÓN",
    "INICIALIZACI√ìN": "INICIALIZACIÓN",
    "NAVEGACI√ìN": "NAVEGACIÓN",
    "C√ìDIGO": "CÓDIGO",
    "GESTI√ìN": "GESTIÓN",
    "SESI√ìN": "SESIÓN",
    "DEM√ÅS": "DEMÁS",
    "DIAGN√ìSTICO": "DIAGNÓSTICO",
    "ESPEC√çFICO": "ESPECÍFICO",
    "FUNCI√ìN": "FUNCIÓN",
    "ELIMINACI√ìN": "ELIMINACIÓN",
    "‚ùó": "✓",
    "‚è∞": "⏰",
    "üí•": "🗑️",
}

original = content
for bad, good in fixes.items():
    content = content.replace(bad, good)

if content != original:
    with open("static/js/main.js", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ main.js corregido")
else:
    print("ℹ️ main.js ya está correcto")
