"""
Script para importar artículos desde Excel a la base de datos
Similar a la importación de activos y proveedores
"""

import sys
import os
from decimal import Decimal

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.inventario import Inventario
from app.models.categoria import Categoria
import pandas as pd
from datetime import datetime


def limpiar_valor_numerico(valor):
    """Limpia y convierte valores numéricos"""
    if pd.isna(valor) or valor == "" or valor is None:
        return None

    # Si es string, limpiar
    if isinstance(valor, str):
        # Remover espacios y comas
        valor = valor.strip().replace(",", "")
        if valor == "" or valor.lower() in ["nan", "none", "null"]:
            return None
        try:
            return Decimal(str(valor))
        except:
            return None

    # Si ya es número
    try:
        return Decimal(str(valor))
    except:
        return None


def limpiar_texto(texto):
    """Limpia texto eliminando valores inválidos"""
    if pd.isna(texto) or texto == "" or texto is None:
        return None

    texto_str = str(texto).strip()

    # Eliminar cadenas de punto y coma
    if texto_str.replace(";", "").strip() == "":
        return None

    if texto_str.lower() in ["nan", "none", "null", ""]:
        return None

    return texto_str


def obtener_o_crear_categoria(nombre_categoria, nombre_subcategoria=None):
    """Obtiene o crea una categoría"""
    if not nombre_categoria:
        return None

    # Buscar categoría existente
    categoria = Categoria.query.filter_by(nombre=nombre_categoria).first()

    if not categoria:
        # Generar prefijo desde el nombre
        prefijo = Categoria.generar_prefijo_desde_nombre(nombre_categoria)

        # Verificar que el prefijo sea único
        contador = 1
        prefijo_original = prefijo
        while Categoria.query.filter_by(prefijo=prefijo).first():
            prefijo = f"{prefijo_original}{contador}"
            contador += 1

        # Crear nueva categoría
        categoria = Categoria(
            nombre=nombre_categoria,
            descripcion=f"Categoría importada: {nombre_categoria}",
            prefijo=prefijo,
            activa=True,
        )
        db.session.add(categoria)
        db.session.flush()  # Para obtener el ID sin hacer commit
        print(f"  ✅ Categoría creada: {nombre_categoria} (Prefijo: {prefijo})")

    return categoria.id


def importar_articulos():
    """Importa artículos desde el archivo Excel"""
    app = create_app()

    with app.app_context():
        # Leer el archivo Excel
        archivo_excel = "Articulos.xlsx"
        print(f"\n📂 Leyendo archivo: {archivo_excel}")

        try:
            df = pd.read_excel(archivo_excel)
            print(f"✅ Archivo leído correctamente: {len(df)} filas")
        except Exception as e:
            print(f"❌ Error al leer el archivo: {e}")
            return

        # Mostrar columnas disponibles
        print(f"\n📋 Columnas encontradas:")
        for col in df.columns:
            print(f"   - {col}")

        # Estadísticas
        total_filas = len(df)
        procesadas = 0
        creadas = 0
        actualizadas = 0
        errores = 0
        omitidas = 0

        print(f"\n🔄 Procesando {total_filas} artículos...")
        print("=" * 80)

        for index, row in df.iterrows():
            try:
                # Saltar filas vacías o sin ID
                if pd.isna(row.get("ID")):
                    omitidas += 1
                    continue

                codigo_id = str(int(row["ID"]))
                producto = limpiar_texto(row.get("Producto"))

                # Si no hay producto, omitir
                if not producto:
                    print(f"⚠️  Fila {index + 1}: Sin descripción de producto, omitida")
                    omitidas += 1
                    continue

                # Preparar datos
                stock = limpiar_valor_numerico(row.get("Stock"))
                costo = limpiar_valor_numerico(row.get("Costo"))
                minimo = limpiar_valor_numerico(row.get("Minimo"))
                maximo = limpiar_valor_numerico(row.get("Maximo"))

                unidad = limpiar_texto(row.get("Unidad")) or "pz"
                unidad_compra = limpiar_texto(row.get("Unidad de compra")) or unidad

                ubicacion = limpiar_texto(row.get("Localización"))
                almacen = limpiar_texto(row.get("Almacén"))
                categoria_nombre = limpiar_texto(row.get("Categoría"))
                subcategoria_nombre = limpiar_texto(row.get("Subcategoría"))
                nif_proveedor = limpiar_texto(row.get("NIF Proveedor"))
                cuenta_contable = limpiar_texto(row.get("Cuenta Contable"))
                estado = limpiar_texto(row.get("Estado"))
                descripcion_producto = limpiar_texto(row.get("Descripción producto"))

                # Generar código único
                codigo = f"ART-{codigo_id.zfill(5)}"

                # Buscar si ya existe
                articulo = Inventario.query.filter_by(codigo=codigo).first()

                # Obtener o crear categoría
                categoria_id = None
                if categoria_nombre:
                    categoria_id = obtener_o_crear_categoria(
                        categoria_nombre, subcategoria_nombre
                    )

                if articulo:
                    # Actualizar existente
                    articulo.descripcion = producto
                    articulo.nombre = producto[:100] if producto else None
                    articulo.stock_actual = stock or 0
                    articulo.stock_minimo = minimo or 0
                    articulo.stock_maximo = maximo
                    articulo.precio_unitario = costo or 0
                    articulo.precio_promedio = costo or 0
                    articulo.precio = costo
                    articulo.unidad_medida = unidad
                    articulo.unidad = unidad_compra
                    articulo.ubicacion = ubicacion
                    articulo.categoria_id = categoria_id
                    articulo.categoria = categoria_nombre
                    articulo.subcategoria = subcategoria_nombre
                    articulo.proveedor_principal = nif_proveedor
                    articulo.cuenta_contable_compra = cuenta_contable or "622000000"
                    articulo.activo = (estado and estado.lower() == "nuevo") or True
                    articulo.observaciones = descripcion_producto
                    articulo.fecha_actualizacion = datetime.now()

                    # Marcar como crítico si está por debajo del mínimo
                    if stock and minimo and stock <= minimo:
                        articulo.critico = True

                    actualizadas += 1
                    accion = "ACTUALIZADO"
                else:
                    # Crear nuevo
                    articulo = Inventario(
                        codigo=codigo,
                        descripcion=producto,
                        nombre=producto[:100] if producto else None,
                        stock_actual=stock or 0,
                        stock_minimo=minimo or 0,
                        stock_maximo=maximo,
                        cantidad=int(stock) if stock else 0,
                        cantidad_minima=int(minimo) if minimo else 0,
                        precio_unitario=costo or 0,
                        precio_promedio=costo or 0,
                        precio=costo,
                        unidad_medida=unidad,
                        unidad=unidad_compra,
                        ubicacion=ubicacion,
                        categoria_id=categoria_id,
                        categoria=categoria_nombre,
                        subcategoria=subcategoria_nombre,
                        proveedor_principal=nif_proveedor,
                        cuenta_contable_compra=cuenta_contable or "622000000",
                        activo=(estado and estado.lower() == "nuevo") or True,
                        observaciones=descripcion_producto,
                        critico=False,
                    )

                    # Marcar como crítico si está por debajo del mínimo
                    if stock and minimo and stock <= minimo:
                        articulo.critico = True

                    db.session.add(articulo)
                    creadas += 1
                    accion = "CREADO"

                procesadas += 1

                # Mostrar progreso cada 50 registros
                if procesadas % 50 == 0:
                    print(f"📦 Procesados {procesadas}/{total_filas} artículos...")

                # Commit cada 100 registros para evitar problemas de memoria
                if procesadas % 100 == 0:
                    db.session.commit()
                    print(f"💾 Guardados {procesadas} registros...")

            except Exception as e:
                errores += 1
                print(f"❌ Error en fila {index + 1}: {e}")
                db.session.rollback()
                continue

        # Commit final
        try:
            db.session.commit()
            print(f"\n💾 Guardando cambios finales...")
        except Exception as e:
            print(f"❌ Error al guardar cambios finales: {e}")
            db.session.rollback()

        # Resumen
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE IMPORTACIÓN")
        print("=" * 80)
        print(f"Total filas en Excel:    {total_filas}")
        print(f"Artículos procesados:    {procesadas}")
        print(f"Artículos creados:       {creadas}")
        print(f"Artículos actualizados:  {actualizadas}")
        print(f"Artículos omitidos:      {omitidas}")
        print(f"Errores:                 {errores}")
        print("=" * 80)

        # Estadísticas adicionales
        total_articulos = Inventario.query.count()
        articulos_criticos = Inventario.query.filter_by(critico=True).count()
        categorias_count = Categoria.query.count()

        print(f"\n📈 ESTADÍSTICAS GENERALES")
        print(f"Total artículos en BD:   {total_articulos}")
        print(f"Artículos críticos:      {articulos_criticos}")
        print(f"Categorías en BD:        {categorias_count}")
        print("=" * 80)


if __name__ == "__main__":
    print("🚀 Iniciando importación de artículos desde Excel...")
    importar_articulos()
    print("\n✅ Proceso completado")
