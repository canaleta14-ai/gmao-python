#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para cargar activos desde Excel a PostgreSQL
Similar al proceso de importación de proveedores
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

import pandas as pd
from app.extensions import db
from app.models import Activo, Proveedor
from app.factory import create_app
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def limpiar_activos_existentes():
    """Elimina todos los activos existentes antes de importar"""
    try:
        count = db.session.query(Activo).count()
        if count > 0:
            db.session.query(Activo).delete()
            db.session.commit()
            logger.info(f"✅ Eliminados {count} activos existentes")
        else:
            logger.info("ℹ️  No hay activos existentes para eliminar")
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al eliminar activos existentes: {e}")
        raise


def mapear_estado(estado_excel):
    """
    Convierte el campo Estado del Excel al formato del modelo

    Args:
        estado_excel (str): Estado desde Excel

    Returns:
        str: Estado mapeado ('Operativo', 'En Mantenimiento', 'Fuera de Servicio', etc.)
    """
    if pd.isna(estado_excel) or estado_excel == "":
        return "Operativo"  # Por defecto

    estado_str = str(estado_excel).strip().lower()

    # Mapeo de estados
    mapeo = {
        "operativo": "Operativo",
        "activo": "Operativo",
        "funcionando": "Operativo",
        "mantenimiento": "En Mantenimiento",
        "en mantenimiento": "En Mantenimiento",
        "reparación": "En Reparación",
        "en reparación": "En Reparación",
        "fuera de servicio": "Fuera de Servicio",
        "inactivo": "Fuera de Servicio",
        "baja": "Fuera de Servicio",
    }

    return mapeo.get(estado_str, "Operativo")


def extraer_departamento_de_codigo(codigo_sage):
    """
    Extrae el código de departamento del Codigo SAGE.
    Formato esperado: 123A45678 -> extrae "123"

    Args:
        codigo_sage (str): Código SAGE del activo (ej: 100A00019)

    Returns:
        str: Código de departamento (000, 100, 140, etc.)
    """
    if pd.isna(codigo_sage):
        return "000"  # General por defecto

    codigo_str = str(codigo_sage).strip()

    # El departamento son los primeros 3 caracteres del código SAGE
    if len(codigo_str) >= 3:
        dept = codigo_str[:3]
        if dept.isdigit():
            return dept

    # Si no se puede extraer, usar departamento general
    return "000"


def generar_codigo_activo(codigo_excel, departamento):
    """
    Genera un código de activo en el formato correcto

    Args:
        codigo_excel: Código del Excel (puede ser número o texto)
        departamento (str): Código del departamento

    Returns:
        str: Código formateado (ej: 000A00001)
    """
    if pd.isna(codigo_excel):
        # Generar automáticamente
        numero = Activo.generar_siguiente_numero()
        return f"{departamento}A{numero}"

    codigo_str = str(codigo_excel).strip()

    # Si ya está en formato correcto, usarlo
    if len(codigo_str) == 9 and codigo_str[3] == "A":
        return codigo_str

    # Si es solo un número, formatearlo
    try:
        numero = int(float(codigo_str))
        numero_str = str(numero).zfill(5)
        return f"{departamento}A{numero_str}"
    except (ValueError, TypeError):
        # Si no se puede convertir, generar uno nuevo
        numero = Activo.generar_siguiente_numero()
        return f"{departamento}A{numero}"


def limpiar_texto(valor, max_length=None):
    """
    Limpia y trunca un texto para ajustarlo a la base de datos

    Args:
        valor: Valor a limpiar
        max_length (int): Longitud máxima permitida

    Returns:
        str: Texto limpio o None
    """
    if pd.isna(valor) or valor == "":
        return None

    texto = str(valor).strip()

    if max_length and len(texto) > max_length:
        texto = texto[:max_length]
        logger.warning(f"⚠️  Texto truncado a {max_length} caracteres: {texto[:50]}...")

    return texto if texto else None


def cargar_activos_desde_excel(ruta_excel, limpiar_antes=False):
    """
    Carga activos desde Excel a PostgreSQL

    Args:
        ruta_excel (str): Ruta al archivo Excel
        limpiar_antes (bool): Si True, elimina todos los activos existentes antes de importar
    """
    try:
        # Leer el archivo Excel
        logger.info(f"📖 Leyendo archivo Excel: {ruta_excel}")
        df = pd.read_excel(ruta_excel)
        logger.info(f"📊 Encontradas {len(df)} filas en el Excel")

        if len(df) == 0:
            logger.warning("⚠️  El archivo Excel está vacío")
            return

        # Mostrar las columnas encontradas
        logger.info(f"📋 Columnas en Excel: {list(df.columns)}")

        # Limpiar datos existentes si se solicita
        if limpiar_antes:
            limpiar_activos_existentes()

        # Procesar cada fila
        activos_creados = 0
        activos_errores = 0
        activos_duplicados = 0

        for index, row in df.iterrows():
            try:
                # Extraer departamento del Codigo SAGE (no del "Código del activo")
                codigo_sage = row.get("Codigo SAGE")
                departamento = extraer_departamento_de_codigo(codigo_sage)

                # Usar el Codigo SAGE directamente como código del activo
                codigo = limpiar_texto(codigo_sage, max_length=50)

                # Si no hay código SAGE, generar uno
                if not codigo:
                    numero = Activo.generar_siguiente_numero()
                    codigo = f"{departamento}A{numero}"

                # Verificar si el código ya existe
                activo_existente = Activo.query.filter_by(codigo=codigo).first()
                if activo_existente:
                    logger.warning(
                        f"⚠️  Activo duplicado (código: {codigo}), saltando..."
                    )
                    activos_duplicados += 1
                    continue

                # Mapear campos del Excel al modelo
                nombre = limpiar_texto(row.get("Nombre del activo"), max_length=100)
                descripcion = limpiar_texto(row.get("Descripción"))
                estado = mapear_estado(row.get("Estado"))
                modelo = limpiar_texto(row.get("Modelo"), max_length=100)
                numero_serie = limpiar_texto(row.get("Número de serie"), max_length=100)

                # Buscar proveedor por NIF
                proveedor_nombre = None
                nif_proveedor = limpiar_texto(
                    row.get("Identificación fiscal proveedor activo"), max_length=50
                )
                if nif_proveedor:
                    proveedor = Proveedor.query.filter_by(nif=nif_proveedor).first()
                    if proveedor:
                        proveedor_nombre = proveedor.nombre
                        logger.info(
                            f"   🏢 Proveedor encontrado: {proveedor.nombre} (NIF: {nif_proveedor})"
                        )
                    else:
                        logger.warning(
                            f"   ⚠️  Proveedor no encontrado para NIF: {nif_proveedor}"
                        )

                # Validar campos requeridos
                if not nombre:
                    logger.error(f"❌ Fila {index + 2}: Falta el nombre del activo")
                    activos_errores += 1
                    continue

                # Crear el activo
                activo = Activo(
                    codigo=codigo,
                    departamento=departamento,
                    nombre=nombre,
                    descripcion=descripcion,
                    estado=estado,
                    modelo=modelo,
                    numero_serie=numero_serie,
                    proveedor=proveedor_nombre,  # Nombre del proveedor
                    activo=True,  # Por defecto activo
                )

                db.session.add(activo)
                activos_creados += 1

                logger.info(
                    f"✅ Activo {activos_creados}: {codigo} - {nombre} (Dpto: {departamento})"
                )

                # Commit cada 50 registros para evitar problemas de memoria
                if activos_creados % 50 == 0:
                    db.session.commit()
                    logger.info(
                        f"💾 Commit intermedio: {activos_creados} activos guardados"
                    )

            except Exception as e:
                logger.error(f"❌ Error procesando fila {index + 2}: {e}")
                activos_errores += 1
                db.session.rollback()

        # Commit final
        try:
            db.session.commit()
            logger.info(f"💾 Commit final exitoso")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error en commit final: {e}")
            raise

        # Resumen
        logger.info("=" * 70)
        logger.info("📊 RESUMEN DE IMPORTACIÓN")
        logger.info("=" * 70)
        logger.info(f"✅ Activos creados: {activos_creados}")
        logger.info(f"⚠️  Activos duplicados: {activos_duplicados}")
        logger.info(f"❌ Activos con errores: {activos_errores}")
        logger.info(
            f"📈 Total procesado: {activos_creados + activos_duplicados + activos_errores}"
        )
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Error general al cargar activos: {e}")
        db.session.rollback()
        raise


def main():
    """Función principal"""
    # Crear aplicación Flask
    app = create_app()

    with app.app_context():
        ruta_excel = "Activos.xlsx"

        logger.info("🚀 Iniciando importación de activos desde Excel")
        logger.info(f"📁 Archivo: {ruta_excel}")

        # Confirmar antes de limpiar
        limpiar = input(
            "\n¿Deseas eliminar todos los activos existentes antes de importar? (s/N): "
        )
        limpiar_antes = limpiar.lower() in ["s", "si", "sí", "y", "yes"]

        if limpiar_antes:
            confirmar = input(
                "⚠️  ADVERTENCIA: Esto eliminará TODOS los activos existentes. ¿Continuar? (s/N): "
            )
            if confirmar.lower() not in ["s", "si", "sí", "y", "yes"]:
                logger.info("❌ Operación cancelada por el usuario")
                return

        # Ejecutar importación
        cargar_activos_desde_excel(ruta_excel, limpiar_antes=limpiar_antes)

        logger.info("🎉 Proceso completado exitosamente")


if __name__ == "__main__":
    main()
