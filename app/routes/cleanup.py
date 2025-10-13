"""
Endpoint para eliminar datos de prueba desde la aplicación web
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.inventario import Inventario
from app.models.usuario import Usuario
from app.models.orden_recambio import OrdenRecambio
from app.models.movimiento_inventario import MovimientoInventario
import logging

cleanup_bp = Blueprint("cleanup", __name__, url_prefix="/admin")

logger = logging.getLogger(__name__)

@cleanup_bp.route("/clean-demo-data", methods=["GET", "POST"])
@login_required
def clean_demo_data():
    """Endpoint para limpiar datos de prueba - solo para administradores"""
    
    # Verificar que el usuario sea administrador
    if not current_user.rol == "Administrador":
        return jsonify({
            "success": False,
            "error": "Acceso denegado. Solo administradores pueden eliminar datos de prueba."
        }), 403
    
    try:
        # Identificar datos de demo
        datos_demo = identificar_datos_demo()
        
        if request.method == "GET":
            # Solo mostrar qué se encontró
            return jsonify({
                "success": True,
                "message": "Datos de prueba identificados",
                "datos_encontrados": {
                    "inventario": len(datos_demo['inventario']),
                    "usuarios": len(datos_demo['usuarios'])
                },
                "detalle": datos_demo
            })
        
        elif request.method == "POST":
            # Ejecutar eliminación
            data = request.get_json() or {}
            confirmar = data.get("confirmar", False)
            
            if not confirmar:
                return jsonify({
                    "success": False,
                    "error": "Debe confirmar la eliminación enviando 'confirmar': true"
                }), 400
            
            # Eliminar datos
            resultados = eliminar_datos_demo(datos_demo, dry_run=False)
            
            return jsonify({
                "success": True,
                "message": "Datos de prueba eliminados correctamente",
                "resultados": resultados
            })
    
    except Exception as e:
        logger.error(f"Error en clean_demo_data: {e}")
        return jsonify({
            "success": False,
            "error": f"Error interno: {str(e)}"
        }), 500

def identificar_datos_demo():
    """Identificar todos los datos de prueba en el sistema"""
    datos_demo = {
        'inventario': [],
        'usuarios': []
    }
    
    # Artículos de inventario de demo (basado en códigos conocidos)
    codigos_demo = ['ART-001', 'ART-002', 'ART-003']
    
    for codigo in codigos_demo:
        articulo = Inventario.query.filter_by(codigo=codigo).first()
        if articulo:
            datos_demo['inventario'].append({
                'id': articulo.id,
                'codigo': articulo.codigo,
                'descripcion': articulo.descripcion or 'Sin descripción'
            })
    
    # Buscar otros artículos que puedan ser de demo por descripción
    try:
        articulos_sospechosos = Inventario.query.filter(
            db.or_(
                Inventario.descripcion.ilike('%demo%'),
                Inventario.descripcion.ilike('%prueba%'),
                Inventario.descripcion.ilike('%test%'),
                Inventario.codigo.ilike('%DEMO%'),
                Inventario.codigo.ilike('%TEST%'),
                Inventario.codigo.ilike('%PRUEBA%')
            )
        ).all()
        
        for articulo in articulos_sospechosos:
            if articulo.codigo not in [item['codigo'] for item in datos_demo['inventario']]:
                datos_demo['inventario'].append({
                    'id': articulo.id,
                    'codigo': articulo.codigo,
                    'descripcion': articulo.descripcion or 'Sin descripción'
                })
    except Exception as e:
        logger.warning(f"Error buscando artículos sospechosos: {e}")
    
    # Usuarios de demo (excluyendo admin)
    try:
        usuarios_demo = Usuario.query.filter(
            db.and_(
                Usuario.username != 'admin',
                db.or_(
                    Usuario.username.ilike('%demo%'),
                    Usuario.username.ilike('%test%'),
                    Usuario.username.ilike('%prueba%'),
                    Usuario.nombre.ilike('%demo%'),
                    Usuario.nombre.ilike('%test%'),
                    Usuario.nombre.ilike('%prueba%'),
                    Usuario.email.ilike('%demo%'),
                    Usuario.email.ilike('%test%'),
                    Usuario.email.ilike('%prueba%')
                )
            )
        ).all()
        
        for usuario in usuarios_demo:
            datos_demo['usuarios'].append({
                'id': usuario.id,
                'username': usuario.username,
                'nombre': usuario.nombre,
                'email': usuario.email
            })
    except Exception as e:
        logger.warning(f"Error buscando usuarios demo: {e}")
    
    return datos_demo

def eliminar_datos_demo(datos_demo, dry_run=True):
    """Eliminar los datos de demo identificados"""
    if dry_run:
        logger.info("MODO DRY RUN - Solo simulando eliminación")
        return {"simulacion": True}
    
    resultados = {
        'inventario_eliminado': 0,
        'usuarios_eliminados': 0,
        'movimientos_eliminados': 0,
        'recambios_eliminados': 0
    }
    
    try:
        # Obtener IDs de inventario para eliminar dependencias
        inventario_ids = [item['id'] for item in datos_demo['inventario']]
        
        if inventario_ids:
            # Eliminar recambios de órdenes que usen estos artículos
            recambios_count = OrdenRecambio.query.filter(
                OrdenRecambio.inventario_id.in_(inventario_ids)
            ).count()
            
            OrdenRecambio.query.filter(
                OrdenRecambio.inventario_id.in_(inventario_ids)
            ).delete(synchronize_session=False)
            
            resultados['recambios_eliminados'] = recambios_count
            
            # Eliminar movimientos de inventario
            movimientos_count = MovimientoInventario.query.filter(
                MovimientoInventario.inventario_id.in_(inventario_ids)
            ).count()
            
            MovimientoInventario.query.filter(
                MovimientoInventario.inventario_id.in_(inventario_ids)
            ).delete(synchronize_session=False)
            
            resultados['movimientos_eliminados'] = movimientos_count
        
        # Eliminar artículos de inventario
        for item in datos_demo['inventario']:
            Inventario.query.filter_by(id=item['id']).delete()
            resultados['inventario_eliminado'] += 1
        
        # Eliminar usuarios demo (excepto admin)
        for item in datos_demo['usuarios']:
            if item['username'] != 'admin':
                Usuario.query.filter_by(id=item['id']).delete()
                resultados['usuarios_eliminados'] += 1
        
        db.session.commit()
        logger.info("Datos de prueba eliminados correctamente")
        
        return resultados
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error durante la eliminación: {e}")
        raise