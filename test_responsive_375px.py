import os
import webbrowser
import time
from flask import Flask

# Crear una app Flask simple para probar los estilos
app = Flask(__name__)


@app.route("/")
def test_375px():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Responsive 375px</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            /* Simular los estilos de la app */
            :root {
              --primary-color: #2c3e50;
              --secondary-color: #34495e;
              --success-color: #27ae60;
              --warning-color: #f39c12;
              --danger-color: #e74c3c;
              --info-color: #3498db;
              --light-gray: #ecf0f1;
              --medium-gray: #bdc3c7;
              --dark-gray: #7f8c8d;
            }

            body {
              font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
              background-color: #f8f9fa;
              color: var(--primary-color);
            }

            .table-responsive {
              box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
              border-radius: 10px;
              overflow: hidden;
            }

            .table td {
              padding: 0.4rem 0.6rem !important;
              vertical-align: middle;
              font-size: 0.9rem;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .table th {
              padding: 0.6rem 0.6rem !important;
              vertical-align: middle;
              font-size: 0.9rem;
              font-weight: 600;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .badge-estado {
              padding: 5px 10px;
              border-radius: 20px;
              font-size: 0.85rem;
            }

            /* ========== ESTILOS PARA PANTALLAS MUY PEQUEÑAS (375px) ========== */
            @media (max-width: 375px) {
              .table-responsive {
                font-size: 0.75rem;
              }

              .table td, .table th {
                padding: 0.2rem 0.3rem !important;
                font-size: 0.75rem;
                white-space: normal !important;
                word-wrap: break-word;
                overflow: visible !important;
                text-overflow: clip !important;
              }

              .table th {
                font-size: 0.7rem;
                font-weight: 700;
              }

              .table th:nth-child(5),
              .table td:nth-child(5) {
                display: none;
              }

              .table th:nth-child(8),
              .table td:nth-child(8) {
                display: none;
              }

              .action-btn {
                padding: 0.15rem 0.3rem !important;
                font-size: 0.65rem !important;
              }

              .table-responsive {
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
              }
            }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <h5>Test de Tabla Responsive 375px</h5>
            <div class="table-responsive">
                <table class="table table-striped table-hover mb-0">
                    <thead class="table-dark">
                        <tr>
                            <th><i class="bi bi-hash me-1"></i>Número</th>
                            <th><i class="bi bi-calendar me-1"></i>Fecha</th>
                            <th><i class="bi bi-cpu me-1"></i>Activo</th>
                            <th><i class="bi bi-gear me-1"></i>Tipo</th>
                            <th><i class="bi bi-chat-text me-1"></i>Descripción</th>
                            <th><i class="bi bi-exclamation-triangle me-1"></i>Prioridad</th>
                            <th><i class="bi bi-circle me-1"></i>Estado</th>
                            <th><i class="bi bi-person me-1"></i>Técnico</th>
                            <th class="text-center"><i class="bi bi-three-dots me-1"></i>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>OT-2025-0001</td>
                            <td>2025-01-15</td>
                            <td>Máquina CNC 001</td>
                            <td>Preventivo</td>
                            <td>Mantenimiento preventivo mensual completo del sistema</td>
                            <td><span class="badge bg-warning text-dark">Media</span></td>
                            <td><span class="badge-estado bg-warning text-dark">Pendiente</span></td>
                            <td>Juan Pérez</td>
                            <td class="text-center">
                                <button class="btn btn-sm btn-outline-primary action-btn">Ver</button>
                                <button class="btn btn-sm btn-outline-success action-btn">Editar</button>
                            </td>
                        </tr>
                        <tr>
                            <td>OT-2025-0002</td>
                            <td>2025-01-16</td>
                            <td>Compresor Principal</td>
                            <td>Correctivo</td>
                            <td>Reparación de fuga en válvula de alivio de presión</td>
                            <td><span class="badge bg-danger">Alta</span></td>
                            <td><span class="badge-estado bg-primary">En Proceso</span></td>
                            <td>María García</td>
                            <td class="text-center">
                                <button class="btn btn-sm btn-outline-primary action-btn">Ver</button>
                                <button class="btn btn-sm btn-outline-success action-btn">Editar</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            // Simular redimensionamiento a 375px
            function test375px() {
                document.body.style.width = '375px';
                document.body.style.margin = '0 auto';
                console.log('Simulando pantalla de 375px');
            }

            // Ejecutar test automáticamente
            setTimeout(test375px, 1000);
        </script>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    print("Iniciando servidor de prueba en http://localhost:5001")
    print("Abre la URL en un navegador y redimensiona a 375px de ancho")
    app.run(port=5001, debug=False)
