import sys

sys.path.append(".")

# Importar la función directamente
import pandas as pd
import re


def extraer_telefono_y_contacto(contacto_texto):
    """
    Extrae el teléfono y el nombre de contacto de un texto mixto
    """
    import re

    if not contacto_texto or pd.isna(contacto_texto):
        return "", ""

    texto = str(contacto_texto).strip()

    if not texto:
        return "", ""

    # Patrones de teléfonos españoles/internacionales
    patron_telefono = re.compile(
        r"""
        (?:
            # Teléfonos españoles móviles (6xx xxx xxx o 7xx xxx xxx)
            (?:6|7)\d{8}|
            # Teléfonos españoles fijos (9xx xxx xxx)
            9\d{8}|
            # Teléfonos con espacios o guiones (xxx xxx xxx, xxx-xxx-xxx)
            \d{3}[\s\-]?\d{3}[\s\-]?\d{3}|
            # Teléfonos con formato (xxx xx xx xx)
            \d{3}[\s\-]?\d{2}[\s\-]?\d{2}[\s\-]?\d{2}|
            # Teléfonos internacionales (+34, 0034, etc)
            (?:\+|00)?\d{2,4}[\s\-]?\d{6,12}|
            # Números largos sin espacios (9+ dígitos)
            \d{9,15}
        )
    """,
        re.VERBOSE,
    )

    # Buscar todos los teléfonos en el texto
    telefonos = patron_telefono.findall(texto)

    # Limpiar teléfonos encontrados (quitar espacios y guiones)
    telefonos_limpios = []
    for tel in telefonos:
        tel_limpio = re.sub(r"[\s\-\+]", "", tel)
        if len(tel_limpio) >= 9:  # Solo teléfonos válidos
            telefonos_limpios.append(tel_limpio)

    # Extraer nombres (remover números de teléfono del texto)
    texto_sin_telefonos = texto
    for tel in telefonos:
        texto_sin_telefonos = re.sub(re.escape(tel), "", texto_sin_telefonos)

    # Limpiar el texto resultante
    nombre_contacto = re.sub(r"[,\s]+", " ", texto_sin_telefonos).strip()
    nombre_contacto = re.sub(r"^[,\s]+|[,\s]+$", "", nombre_contacto)

    # Si solo hay números, no hay nombre
    if nombre_contacto and nombre_contacto.replace(" ", "").replace(",", "").isdigit():
        nombre_contacto = ""

    # Obtener el primer teléfono válido
    telefono_principal = telefonos_limpios[0] if telefonos_limpios else ""

    # Casos especiales
    if not telefono_principal and not nombre_contacto:
        # Si no encontramos patrones, ver si todo el texto es un número
        solo_digitos = re.sub(r"[^\d]", "", texto)
        if len(solo_digitos) >= 9:
            return "", solo_digitos
        else:
            # Asumir que es un nombre
            return texto, ""

    return nombre_contacto, telefono_principal


def probar_extraccion():
    """Prueba la función con los datos reales del Excel"""

    print("🧪 PROBANDO FUNCIÓN DE EXTRACCIÓN DE CONTACTOS")
    print("=" * 70)

    # Casos de prueba basados en los datos reales
    casos_prueba = [
        "610693043",
        "Toni",
        "Luis Cedeira 656940060",
        "Xema 667 56 96 08",
        "Toni, Pablo",
        "Jürgen Langelage,Technical Support, After Sales Service, 0049 541 33104-646, Marc Rütting",
        "Carlos Ortiz Vives 600969813",
        "Zacarias",
        "Ivan, Nacho, Paco",
        "Jose Luis, Móvil 647824023",
        "",
        "934567890",
        "María García 915123456",
        "+34 612 345 678",
    ]

    print(f"{'Original':<50} | {'Contacto':<25} | {'Teléfono':<15}")
    print("-" * 95)

    for caso in casos_prueba:
        nombre, telefono = extraer_telefono_y_contacto(caso)
        nombre_mostrar = nombre[:24] if nombre else "(vacío)"
        telefono_mostrar = telefono if telefono else "(vacío)"
        caso_mostrar = caso[:49] if caso else "(vacío)"

        print(f"{caso_mostrar:<50} | {nombre_mostrar:<25} | {telefono_mostrar:<15}")

    print("\n✅ Prueba completada")


if __name__ == "__main__":
    probar_extraccion()
