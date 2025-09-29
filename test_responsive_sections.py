from flask import Flask
import os

# Crear una app Flask simple para probar los estilos
app = Flask(__name__)


@app.route("/")
def test_responsive_sections():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Responsive - Proveedores, Reportes, Solicitudes</title>
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
              overflow-x: auto;
              overflow-y: hidden;
              -webkit-overflow-scrolling: touch;
            }

            .table td {
              padding: 0.4rem 0.6rem !important;
              vertical-align: middle;
              font-size: 0.9rem;
              overflow: visible;
              text-overflow: ellipsis;
              white-space: nowrap;
              max-width: 150px;
            }

            .table th {
              padding: 0.6rem 0.6rem !important;
              vertical-align: middle;
              font-size: 0.9rem;
              font-weight: 600;
              overflow: visible;
              text-overflow: ellipsis;
              white-space: nowrap;
              max-width: 150px;
            }

            .badge-estado {
              padding: 5px 10px;
              border-radius: 20px;
              font-size: 0.85rem;
            }

            .action-btn {
              padding: 0.25rem 0.5rem !important;
              font-size: 0.75rem !important;
              line-height: 1.2 !important;
              border-radius: 0.375rem !important;
              transition: all 0.2s ease !important;
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

              /* Proveedores: Ocultar Dirección, Contacto, Email, Cuenta Contable */
              #tabla-proveedores-main th:nth-child(3), #tabla-proveedores-main td:nth-child(3),
              #tabla-proveedores-main th:nth-child(4), #tabla-proveedores-main td:nth-child(4),
              #tabla-proveedores-main th:nth-child(5), #tabla-proveedores-main td:nth-child(5),
              #tabla-proveedores-main th:nth-child(6), #tabla-proveedores-main td:nth-child(6) {
                display: none;
              }

              /* Reportes - Análisis frecuencia: Ocultar Próximos, Vencidos */
              #analisis-frecuencia th:nth-child(4), #analisis-frecuencia td:nth-child(4),
              #analisis-frecuencia th:nth-child(5), #analisis-frecuencia td:nth-child(5) {
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

              .container-fluid {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
              }

              /* Estilos para cards en solicitudes */
              .card-body .row .col-md-6 {
                margin-bottom: 1rem;
              }

              .card-body .d-flex.align-items-center {
                flex-wrap: wrap;
                gap: 0.5rem;
              }

              .card-body .d-flex.align-items-center > div:last-child {
                flex: 1;
                min-width: 0;
              }
            }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <h5 class="mb-4">Test Responsive - Proveedores, Reportes, Solicitudes (375px)</h5>

            <!-- Proveedores -->
            <div class="card mb-4">
                <div class="card-header">
                    <h6 class="mb-0"><i class="bi bi-building me-2"></i>Proveedores</h6>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover" id="tabla-proveedores-main">
                            <thead class="table-dark">
                                <tr>
                                    <th><i class="bi bi-building me-1"></i>Proveedor</th>
                                    <th><i class="bi bi-card-text me-1"></i>NIF</th>
                                    <th><i class="bi bi-geo-alt me-1"></i>Dirección</th>
                                    <th><i class="bi bi-person me-1"></i>Contacto</th>
                                    <th><i class="bi bi-envelope me-1"></i>Email</th>
                                    <th><i class="bi bi-calculator me-1"></i>Cuenta Contable</th>
                                    <th><i class="bi bi-circle me-1"></i>Estado</th>
                                    <th class="text-center"><i class="bi bi-three-dots me-1"></i>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Proveedor ABC S.L.</td>
                                    <td>B12345678</td>
                                    <td>Calle Mayor 123, Madrid</td>
                                    <td>Juan García</td>
                                    <td>juan@proveedorabc.com</td>
                                    <td>41000001</td>
                                    <td><span class="badge-estado bg-success">Activo</span></td>
                                    <td class="text-center">
                                        <button class="btn btn-sm btn-outline-primary action-btn">Ver</button>
                                        <button class="btn btn-sm btn-outline-success action-btn">Editar</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Reportes -->
            <div class="card mb-4">
                <div class="card-header">
                    <h6 class="mb-0"><i class="bi bi-bar-chart me-2"></i>Análisis por Frecuencia</h6>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Frecuencia</th>
                                    <th>Cantidad de Planes</th>
                                    <th>Planes Activos</th>
                                    <th>Próximos</th>
                                    <th>Vencidos</th>
                                    <th>Porcentaje</th>
                                </tr>
                            </thead>
                            <tbody id="analisis-frecuencia">
                                <tr>
                                    <td>Diario</td>
                                    <td>5</td>
                                    <td>4</td>
                                    <td>3</td>
                                    <td>1</td>
                                    <td>80%</td>
                                </tr>
                                <tr>
                                    <td>Semanal</td>
                                    <td>12</td>
                                    <td>10</td>
                                    <td>8</td>
                                    <td>2</td>
                                    <td>83%</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Solicitudes (Cards) -->
            <div class="card mb-4">
                <div class="card-header">
                    <h6 class="mb-0"><i class="bi bi-card-text me-2"></i>Información de Solicitud</h6>
                </div>
                <div class="card-body p-4">
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <div class="d-flex align-items-center p-3 bg-light rounded">
                                <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px">
                                    <i class="bi bi-circle-fill fs-4"></i>
                                </div>
                                <div>
                                    <small class="text-muted d-block">Estado Actual</small>
                                    <strong class="fs-5">En Revisión</strong>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="d-flex align-items-center p-3 bg-light rounded">
                                <div class="rounded-circle bg-warning text-white d-flex align-items-center justify-content-center me-3" style="width: 50px; height: 50px">
                                    <i class="bi bi-flag-fill fs-4"></i>
                                </div>
                                <div>
                                    <small class="text-muted d-block">Prioridad</small>
                                    <strong class="fs-5">Alta</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Simular redimensionamiento a 375px
            function test375px() {
                // Forzar estilos de 375px
                const style = document.createElement('style');
                style.textContent = `
                    body { width: 375px !important; margin: 0 auto !important; }
                    .container-fluid { max-width: 375px !important; }
                `;
                document.head.appendChild(style);
                console.log('Simulando pantalla de 375px - Columnas ocultas activas');
                console.log('Proveedores: Dirección, Contacto, Email, Cuenta Contable ocultos');
                console.log('Reportes: Próximos, Vencidos ocultos');
                console.log('Scroll horizontal habilitado en todas las tablas');
            }

            // Ejecutar test automáticamente
            setTimeout(test375px, 1000);
        </script>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    print("Iniciando servidor de prueba en http://localhost:5002")
    print("Abre la URL para probar proveedores, reportes y solicitudes en 375px")
    app.run(port=5002, debug=False)
