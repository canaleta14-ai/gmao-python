import pandas as pd
from app.extensions import db
from app.models.proveedor import Proveedor
from app.factory import create_app
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def limpiar_proveedores_existentes():
    """Elimina todos los proveedores existentes antes de importar"""
    try:
        count = db.session.query(Proveedor).count()
        if count > 0:
            db.session.query(Proveedor).delete()
            db.session.commit()
            logger.info(f"Eliminados {count} proveedores existentes")
        else:
            logger.info("No hay proveedores existentes para eliminar")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar proveedores existentes: {e}")
        raise


def mapear_estado_a_activo(estado):
    """Convierte el campo Estado del Excel a booleano activo"""
    if pd.isna(estado) or estado == "":
        return True  # Por defecto activo
    estado_str = str(estado).lower().strip()
    return estado_str in ["activo", "true", "1", "si", "sí", "yes"]


def extraer_telefono_y_contacto(contacto_texto):
    """
    Extrae el teléfono y el nombre de contacto de un texto mixto

    Args:
        contacto_texto (str): Texto que puede contener nombres y teléfonos

    Returns:
        tuple: (nombre_contacto, telefono)
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


def cargar_proveedores_desde_excel(ruta_excel, limpiar_antes=False):
    """
    Carga proveedores desde Excel a PostgreSQL

    Args:
        ruta_excel (str): Ruta al archivo Excel
        limpiar_antes (bool): Si True, elimina todos los proveedores existentes antes de importar
    """
    try:
        # Leer el archivo Excel
        logger.info(f"Leyendo archivo Excel: {ruta_excel}")
        df = pd.read_excel(ruta_excel)
        logger.info(f"Encontradas {len(df)} filas en el Excel")

        if len(df) == 0:
            logger.warning("El archivo Excel está vacío")
            return

        # Mostrar las columnas encontradas
        logger.info(f"Columnas en Excel: {list(df.columns)}")

        # Limpiar datos existentes si se solicita
        if limpiar_antes:
            limpiar_proveedores_existentes()

        # Procesar cada fila
        proveedores_creados = 0
        proveedores_errores = 0

        for index, row in df.iterrows():
            try:
                # Mapear campos del Excel al modelo con separación inteligente de contacto/teléfono
                nombre = (
                    str(row.get("Proveedor", "")).strip()
                    if pd.notna(row.get("Proveedor"))
                    else ""
                )
                nif = (
                    str(row.get("NIF", "")).strip() if pd.notna(row.get("NIF")) else ""
                )
                direccion = (
                    str(row.get("Dirección", "")).strip()
                    if pd.notna(row.get("Dirección"))
                    else ""
                )

                # Procesar campo Contacto para separar nombre y teléfono
                contacto_excel = row.get("Contacto", "")
                nombre_contacto, telefono_numero = extraer_telefono_y_contacto(
                    contacto_excel
                )

                # Obtener y limpiar los campos adicionales
                email_raw = (
                    str(row.get("Email", "")).strip()
                    if pd.notna(row.get("Email"))
                    else ""
                )
                cuenta_contable_raw = (
                    str(row.get("Cuenta Contable", "")).strip()
                    if pd.notna(row.get("Cuenta Contable"))
                    else ""
                )

                proveedor = Proveedor(
                    nombre=nombre[:255] if nombre else "",  # Límite 255
                    nif=nif[:50] if nif else "",  # Límite 50
                    direccion=direccion[:255] if direccion else "",  # Límite 255
                    contacto=(
                        nombre_contacto[:100] if nombre_contacto else ""
                    ),  # Límite 100 - Nombre de la persona
                    telefono=(
                        telefono_numero[:50] if telefono_numero else ""
                    ),  # Límite 50 - Solo el número
                    email=email_raw[:120] if email_raw else "",  # Límite 120
                    cuenta_contable=(
                        cuenta_contable_raw[:50] if cuenta_contable_raw else ""
                    ),  # Límite 50
                    activo=mapear_estado_a_activo(
                        row.get("Estado")
                    ),  # Estado -> activo (booleano)
                )

                # Validar que al menos tenga nombre
                if not proveedor.nombre:
                    logger.warning(f"Fila {index + 2}: Proveedor sin nombre, saltando")
                    proveedores_errores += 1
                    continue

                db.session.add(proveedor)
                proveedores_creados += 1

                if proveedores_creados % 10 == 0:
                    logger.info(f"Procesados {proveedores_creados} proveedores...")

            except Exception as e:
                logger.error(f"Error procesando fila {index + 2}: {e}")
                proveedores_errores += 1
                continue

        # Guardar cambios
        db.session.commit()
        logger.info(f"✅ Importación completada:")
        logger.info(f"   - Proveedores creados: {proveedores_creados}")
        logger.info(f"   - Errores: {proveedores_errores}")
        logger.info(f"   - Total procesado: {len(df)} filas")

        return proveedores_creados

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error durante la importación: {e}")
        raise


def verificar_proveedores_importados():
    """Verifica los proveedores importados"""
    try:
        total = db.session.query(Proveedor).count()
        activos = db.session.query(Proveedor).filter(Proveedor.activo == True).count()
        inactivos = total - activos

        logger.info(f"📊 Estado actual de proveedores:")
        logger.info(f"   - Total: {total}")
        logger.info(f"   - Activos: {activos}")
        logger.info(f"   - Inactivos: {inactivos}")

        # Mostrar algunos ejemplos
        if total > 0:
            logger.info("📋 Primeros 5 proveedores:")
            primeros = db.session.query(Proveedor).limit(5).all()
            for p in primeros:
                logger.info(f"   - {p.nombre} (NIF: {p.nif}, Activo: {p.activo})")

    except Exception as e:
        logger.error(f"Error verificando proveedores: {e}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Verificar estado antes de importar
        logger.info("🔍 Verificando estado antes de la importación...")
        verificar_proveedores_importados()

        # Preguntar si quiere limpiar datos existentes (para modo interactivo)
        # En este caso, no limpiamos por defecto para no perder datos
        cargar_proveedores_desde_excel("Proveedores.xlsx", limpiar_antes=False)

        # Verificar estado después de importar
        logger.info("✅ Verificando estado después de la importación...")
        verificar_proveedores_importados()
