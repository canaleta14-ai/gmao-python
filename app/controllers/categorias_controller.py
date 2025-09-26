from flask import jsonify, request
from app.extensions import db
from app.models.categoria import Categoria
from app.models.inventario import Inventario
from sqlalchemy import func


class CategoriasController:
    """Controlador para gestionar categorías de inventario"""

    @staticmethod
    def obtener_todas():
        """Obtiene todas las categorías activas"""
        try:
            categorias = (
                Categoria.query.filter_by(activa=True).order_by(Categoria.nombre).all()
            )

            categorias_data = []
            for categoria in categorias:
                # Contar artículos en cada categoría
                total_articulos = Inventario.query.filter_by(
                    categoria_id=categoria.id
                ).count()

                categorias_data.append(
                    {
                        "id": categoria.id,
                        "nombre": categoria.nombre,
                        "prefijo": categoria.prefijo,
                        "color": categoria.color,
                        "descripcion": categoria.descripcion,
                        "ultimo_numero": categoria.ultimo_numero,
                        "total_articulos": total_articulos,
                        "activo": categoria.activa,
                        "fecha_creacion": (
                            categoria.fecha_creacion.isoformat()
                            if categoria.fecha_creacion
                            else None
                        ),
                    }
                )

            return jsonify(
                {
                    "success": True,
                    "categorias": categorias_data,
                    "total": len(categorias_data),
                }
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al obtener categorías: {str(e)}",
                    }
                ),
                500,
            )

    @staticmethod
    def crear():
        """Crea una nueva categoría"""
        try:
            data = request.get_json()

            # Validaciones
            if not data.get("nombre"):
                return (
                    jsonify({"success": False, "message": "El nombre es requerido"}),
                    400,
                )

            if not data.get("prefijo"):
                return (
                    jsonify({"success": False, "message": "El prefijo es requerido"}),
                    400,
                )

            # Verificar que el prefijo no exista
            if Categoria.query.filter_by(prefijo=data["prefijo"].upper()).first():
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Ya existe una categoría con ese prefijo",
                        }
                    ),
                    400,
                )

            # Crear nueva categoría
            categoria = Categoria(
                nombre=data["nombre"],
                prefijo=data["prefijo"].upper(),
                descripcion=data.get("descripcion", ""),
                color=data.get("color", "#007bff"),
            )

            db.session.add(categoria)
            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": "Categoría creada exitosamente",
                    "categoria": {
                        "id": categoria.id,
                        "nombre": categoria.nombre,
                        "prefijo": categoria.prefijo,
                        "color": categoria.color,
                        "descripcion": categoria.descripcion,
                    },
                }
            )

        except Exception as e:
            db.session.rollback()
            return (
                jsonify(
                    {"success": False, "message": f"Error al crear categoría: {str(e)}"}
                ),
                500,
            )

    @staticmethod
    def generar_codigo(categoria_id):
        """Genera el próximo código para una categoría"""
        try:
            categoria = Categoria.query.get(categoria_id)
            if not categoria:
                return (
                    jsonify({"success": False, "message": "Categoría no encontrada"}),
                    404,
                )

            codigo = categoria.generar_proximo_codigo()

            return jsonify(
                {
                    "success": True,
                    "codigo": codigo,
                    "prefijo": categoria.prefijo,
                    "siguiente_numero": categoria.ultimo_numero,
                }
            )

        except Exception as e:
            return (
                jsonify(
                    {"success": False, "message": f"Error al generar código: {str(e)}"}
                ),
                500,
            )

    @staticmethod
    def actualizar(categoria_id):
        """Actualiza una categoría existente"""
        try:
            categoria = Categoria.query.get(categoria_id)
            if not categoria:
                return (
                    jsonify({"success": False, "message": "Categoría no encontrada"}),
                    404,
                )

            data = request.get_json()

            # Actualizar campos permitidos
            if "nombre" in data:
                categoria.nombre = data["nombre"]

            if "descripcion" in data:
                categoria.descripcion = data["descripcion"]

            if "color" in data:
                categoria.color = data["color"]

            if "activo" in data:
                categoria.activa = data["activo"]

            # No permitir cambiar el prefijo si ya tiene artículos asociados
            if "prefijo" in data:
                total_articulos = Inventario.query.filter_by(
                    categoria_id=categoria.id
                ).count()
                if total_articulos > 0:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "No se puede cambiar el prefijo de una categoría que ya tiene artículos asociados",
                            }
                        ),
                        400,
                    )

                # Verificar que el nuevo prefijo no exista
                prefijo_existente = Categoria.query.filter(
                    Categoria.prefijo == data["prefijo"].upper(),
                    Categoria.id != categoria.id,
                ).first()

                if prefijo_existente:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Ya existe una categoría con ese prefijo",
                            }
                        ),
                        400,
                    )

                categoria.prefijo = data["prefijo"].upper()

            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": "Categoría actualizada exitosamente",
                    "categoria": {
                        "id": categoria.id,
                        "nombre": categoria.nombre,
                        "prefijo": categoria.prefijo,
                        "color": categoria.color,
                        "descripcion": categoria.descripcion,
                        "activo": categoria.activa,
                    },
                }
            )

        except Exception as e:
            db.session.rollback()
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al actualizar categoría: {str(e)}",
                    }
                ),
                500,
            )

    @staticmethod
    def eliminar(categoria_id):
        """Elimina (desactiva) una categoría"""
        try:
            categoria = Categoria.query.get(categoria_id)
            if not categoria:
                return (
                    jsonify({"success": False, "message": "Categoría no encontrada"}),
                    404,
                )

            # Verificar si tiene artículos asociados
            total_articulos = Inventario.query.filter_by(
                categoria_id=categoria.id
            ).count()
            if total_articulos > 0:
                # Solo desactivar, no eliminar
                categoria.activa = False
                db.session.commit()

                return jsonify(
                    {
                        "success": True,
                        "message": f"Categoría desactivada. Tiene {total_articulos} artículos asociados.",
                    }
                )
            else:
                # Eliminar completamente si no tiene artículos
                db.session.delete(categoria)
                db.session.commit()

                return jsonify(
                    {"success": True, "message": "Categoría eliminada exitosamente"}
                )

        except Exception as e:
            db.session.rollback()
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al eliminar categoría: {str(e)}",
                    }
                ),
                500,
            )

    @staticmethod
    def obtener_estadisticas():
        """Obtiene estadísticas de las categorías"""
        try:
            # Total de categorías activas
            total_categorias = Categoria.query.filter_by(activa=True).count()

            # Categorías con más artículos
            categorias_con_articulos = (
                db.session.query(
                    Categoria.nombre,
                    Categoria.prefijo,
                    Categoria.color,
                    func.count(Inventario.id).label("total_articulos"),
                )
                .outerjoin(Inventario, Categoria.id == Inventario.categoria_id)
                .filter(Categoria.activa == True)
                .group_by(Categoria.id)
                .order_by(func.count(Inventario.id).desc())
                .limit(10)
                .all()
            )

            estadisticas_data = []
            for categoria in categorias_con_articulos:
                estadisticas_data.append(
                    {
                        "nombre": categoria.nombre,
                        "prefijo": categoria.prefijo,
                        "color": categoria.color,
                        "total_articulos": categoria.total_articulos,
                    }
                )

            return jsonify(
                {
                    "success": True,
                    "total_categorias": total_categorias,
                    "categorias_top": estadisticas_data,
                }
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al obtener estadísticas: {str(e)}",
                    }
                ),
                500,
            )
