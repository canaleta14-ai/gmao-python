import subprocess
import sys

try:
    result = subprocess.run(
        ["node", "-c", "static/js/inventario.js"],
        capture_output=True,
        text=True,
        cwd=r"c:\gmao - copia",
    )
    if result.returncode == 0:
        print("✅ Sintaxis JavaScript correcta")
    else:
        print("❌ Error de sintaxis:")
        print(result.stderr)
except FileNotFoundError:
    print("❌ Node.js no está instalado o no está en el PATH")
    print("Verificando sintaxis manualmente...")

    # Verificación manual básica
    with open(r"c:\gmao - copia\static\js\inventario.js", "r", encoding="utf-8") as f:
        content = f.read()

    # Contar llaves
    open_braces = content.count("{")
    close_braces = content.count("}")
    open_parens = content.count("(")
    close_parens = content.count(")")

    print(f"Llaves abiertas: {open_braces}")
    print(f"Llaves cerradas: {close_braces}")
    print(f"Paréntesis abiertos: {open_parens}")
    print(f"Paréntesis cerrados: {close_parens}")

    if open_braces != close_braces:
        print(f"❌ Faltan {open_braces - close_braces} llaves de cierre")
    else:
        print("✅ Llaves balanceadas")
