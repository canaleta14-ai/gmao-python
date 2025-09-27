#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# Leer el archivo JavaScript
with open("static/js/ordenes.js", "r", encoding="utf-8") as f:
    content = f.read()

print("🔍 Verificaciones de sintaxis básicas:")

# Verificar paréntesis balanceados
open_parens = content.count("(")
close_parens = content.count(")")
print(
    f'Paréntesis: {open_parens} abiertos, {close_parens} cerrados - {"✅" if open_parens == close_parens else "❌"}'
)

# Verificar llaves balanceadas
open_braces = content.count("{")
close_braces = content.count("}")
print(
    f'Llaves: {open_braces} abiertas, {close_braces} cerradas - {"✅" if open_braces == close_braces else "❌"}'
)

# Verificar corchetes balanceados
open_brackets = content.count("[")
close_brackets = content.count("]")
print(
    f'Corchetes: {open_brackets} abiertos, {close_brackets} cerrados - {"✅" if open_brackets == close_brackets else "❌"}'
)

# Verificar funciones principales
functions = ["mostrarModalNuevaOrden", "exportarCSV"]
for func in functions:
    if f"function {func}(" in content:
        print(f"Función {func}: ✅ encontrada")
    else:
        print(f"Función {func}: ❌ no encontrada")

# Verificar que no haya caracteres problemáticos
problematic_chars = ["√", "‚", "∫", "ó", "ñ", "✅", "'"]
found_problems = []
for char in problematic_chars:
    if char in content:
        found_problems.append(char)

if found_problems:
    print(f"❌ Caracteres problemáticos encontrados: {found_problems}")
else:
    print("✅ No se encontraron caracteres problemáticos")

print("✅ Verificación básica completada")
