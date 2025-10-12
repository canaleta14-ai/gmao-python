#!/usr/bin/env python3
"""
Endpoint web para limpiar inventario - Agregar a las rutas de la aplicación
"""

from flask import Blueprint, jsonify, request, render_template_string
from app.models import db, Inventario
from sqlalchemy import text
from datetime import datetime
import logging

# Blueprint para limpieza de inventario
limpiar_bp = Blueprint("limpiar", __name__, url_prefix="/admin/limpiar")


def disable_csrf(f):
    """Decorator para deshabilitar CSRF en una función específica"""
    try:
        from app.extensions import csrf

        csrf.exempt(f)
    except ImportError:
        pass
    return f


@limpiar_bp.route("/inventario", methods=["GET"])
def mostrar_inventario():
    """Mostrar página para limpiar inventario"""

    template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Limpiar Inventario - GMAO</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .danger-zone { border: 2px solid #dc3545; border-radius: 10px; padding: 20px; background-color: #f8d7da; }
            .warning-box { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-8 mx-auto">
                    <h1 class="text-center mb-4">
                        <i class="fas fa-trash-alt text-danger"></i>
                        Limpiar Inventario
                    </h1>
                    
                    <!-- Información actual -->
                    <div class="card mb-4">
                        <div class="card-header bg-info text-white">
                            <h5><i class="fas fa-info-circle"></i> Estado Actual del Inventario</h5>
                        </div>
                        <div class="card-body">
                            <div id="inventario-info">
                                <div class="text-center">
                                    <div class="spinner-border" role="status">
                                        <span class="visually-hidden">Cargando...</span>
                                    </div>
                                    <p>Cargando información del inventario...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Zona de peligro -->
                    <div class="danger-zone">
                        <h3 class="text-danger">
                            <i class="fas fa-exclamation-triangle"></i>
                            Zona de Peligro
                        </h3>
                        
                        <div class="warning-box mb-3">
                            <strong>⚠️ ADVERTENCIA:</strong>
                            <ul class="mb-0 mt-2">
                                <li>Esta acción eliminará <strong>TODOS</strong> los artículos del inventario</li>
                                <li>La acción <strong>NO SE PUEDE DESHACER</strong></li>
                                <li>Se recomienda hacer una copia de seguridad antes</li>
                            </ul>
                        </div>
                        
                        <div class="text-center">
                            <button id="btn-limpiar" class="btn btn-danger btn-lg" onclick="confirmarLimpieza()">
                                <i class="fas fa-trash-alt"></i>
                                Eliminar Todos los Artículos
                            </button>
                        </div>
                    </div>
                    
                    <!-- Resultado -->
                    <div id="resultado" class="mt-4" style="display: none;"></div>
                    
                    <!-- Botón volver -->
                    <div class="text-center mt-4">
                        <a href="/inventario/" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i>
                            Volver al Inventario
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Cargar información del inventario al cargar la página
            document.addEventListener('DOMContentLoaded', function() {
                cargarInventarioInfo();
            });
            
            async function cargarInventarioInfo() {
                try {
                    const response = await fetch('/admin/limpiar/inventario/info');
                    const data = await response.json();
                    
                    let html = '';
                    if (data.success) {
                        html = `
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><i class="fas fa-box"></i> Total de Artículos:</h6>
                                    <h3 class="text-primary">${data.total}</h3>
                                </div>
                                <div class="col-md-6">
                                    <h6><i class="fas fa-database"></i> Base de Datos:</h6>
                                    <p class="mb-0">${data.database}</p>
                                </div>
                            </div>
                        `;
                        
                        if (data.articulos && data.articulos.length > 0) {
                            html += `
                                <hr>
                                <h6><i class="fas fa-list"></i> Artículos Encontrados:</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>ID</th>
                                                <th>Código</th>
                                                <th>Nombre</th>
                                                <th>Stock</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                            `;
                            
                            data.articulos.forEach(art => {
                                html += `
                                    <tr>
                                        <td>${art.id}</td>
                                        <td>${art.codigo || 'N/A'}</td>
                                        <td>${art.nombre || 'N/A'}</td>
                                        <td>${art.stock}</td>
                                    </tr>
                                `;
                            });
                            
                            html += `
                                        </tbody>
                                    </table>
                                </div>
                            `;
                        }
                    } else {
                        html = `<div class="alert alert-danger">Error: ${data.error}</div>`;
                    }
                    
                    document.getElementById('inventario-info').innerHTML = html;
                    
                } catch (error) {
                    document.getElementById('inventario-info').innerHTML = 
                        `<div class="alert alert-danger">Error al cargar la información: ${error.message}</div>`;
                }
            }
            
            function confirmarLimpieza() {
                if (confirm('¿Está ABSOLUTAMENTE SEGURO de que quiere eliminar TODOS los artículos del inventario?\\n\\nEsta acción NO se puede deshacer.')) {
                    if (confirm('ÚLTIMA CONFIRMACIÓN:\\n\\n¿Confirma la eliminación de TODOS los artículos?')) {
                        limpiarInventario();
                    }
                }
            }
            
            async function limpiarInventario() {
                const btnLimpiar = document.getElementById('btn-limpiar');
                const resultado = document.getElementById('resultado');
                
                // Deshabilitar botón y mostrar loading
                btnLimpiar.disabled = true;
                btnLimpiar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Eliminando...';
                
                try {
                    // Usar fetch sin CSRF token para evitar errores
                    const response = await fetch('/admin/limpiar/inventario/ejecutar', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        resultado.innerHTML = `
                            <div class="alert alert-success">
                                <h5><i class="fas fa-check-circle"></i> Limpieza Completada</h5>
                                <p><strong>Artículos eliminados:</strong> ${data.eliminados}</p>
                                <p><strong>Tiempo:</strong> ${data.tiempo}</p>
                                <p class="mb-0">El inventario está ahora completamente vacío.</p>
                            </div>
                        `;
                        
                        // Recargar información
                        setTimeout(cargarInventarioInfo, 1000);
                        
                    } else {
                        resultado.innerHTML = `
                            <div class="alert alert-danger">
                                <h5><i class="fas fa-exclamation-circle"></i> Error</h5>
                                <p>${data.error}</p>
                            </div>
                        `;
                    }
                    
                } catch (error) {
                    resultado.innerHTML = `
                        <div class="alert alert-danger">
                            <h5><i class="fas fa-exclamation-circle"></i> Error de Conexión</h5>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
                
                // Mostrar resultado y rehabilitar botón
                resultado.style.display = 'block';
                btnLimpiar.disabled = false;
                btnLimpiar.innerHTML = '<i class="fas fa-trash-alt"></i> Eliminar Todos los Artículos';
            }
        </script>
    </body>
    </html>
    """

    return render_template_string(template)


@limpiar_bp.route("/inventario/info", methods=["GET"])
def info_inventario():
    """API para obtener información del inventario"""

    try:
        # Contar artículos
        total = Inventario.query.count()

        # Obtener todos los artículos para mostrar
        articulos = Inventario.query.order_by(Inventario.id).all()

        articulos_data = []
        for art in articulos:
            articulos_data.append(
                {
                    "id": art.id,
                    "codigo": art.codigo,
                    "nombre": art.nombre,
                    "stock": getattr(art, "stock_actual", 0),
                }
            )

        return jsonify(
            {
                "success": True,
                "total": total,
                "database": "Google Cloud SQL PostgreSQL",
                "articulos": articulos_data,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@limpiar_bp.route("/inventario/ejecutar", methods=["POST"])
@disable_csrf
def ejecutar_limpieza():
    """API para ejecutar la limpieza del inventario"""

    try:
        inicio = datetime.now()

        # Contar artículos antes de eliminar
        total_antes = Inventario.query.count()

        if total_antes == 0:
            return jsonify(
                {
                    "success": True,
                    "eliminados": 0,
                    "mensaje": "El inventario ya estaba vacío",
                    "tiempo": "0ms",
                }
            )

        # Eliminar todos los artículos usando SQL directo para ser más eficiente
        result = db.session.execute(text("DELETE FROM inventario"))

        # Reiniciar secuencia de IDs
        db.session.execute(text("ALTER SEQUENCE inventario_id_seq RESTART WITH 1"))

        # Confirmar cambios
        db.session.commit()

        # Calcular tiempo
        fin = datetime.now()
        tiempo = (fin - inicio).total_seconds() * 1000

        # Log de la acción
        logging.info(f"Inventario limpiado: {total_antes} artículos eliminados")

        return jsonify(
            {
                "success": True,
                "eliminados": total_antes,
                "tiempo": f"{tiempo:.0f}ms",
                "mensaje": "Inventario limpiado exitosamente",
            }
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al limpiar inventario: {str(e)}")

        return jsonify({"success": False, "error": str(e)}), 500


# Función para registrar el blueprint en factory.py
def register_limpiar_blueprint(app):
    """Registrar el blueprint de limpieza en la aplicación"""
    app.register_blueprint(limpiar_bp)
    return app
