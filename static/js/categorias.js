/**
 * Gestión de Categorías de Inventario
 * Funcionalidades para crear, editar, eliminar y gestionar categorías dinámicas
 */

class CategoriasManager {
    constructor() {
        this.categorias = [];
        this.categoriaEditando = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.cargarCategorias();
        this.cargarEstadisticas();
    }

    setupEventListeners() {
        // Formulario de categoría
        const formCategoria = document.getElementById('formCategoria');
        if (formCategoria) {
            formCategoria.addEventListener('submit', (e) => this.guardarCategoria(e));
        }

        // Prefijo input para preview
        const prefijoInput = document.getElementById('prefijo');
        if (prefijoInput) {
            prefijoInput.addEventListener('input', () => this.updatePreview());
        }

        // Confirmación de eliminación
        const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
        if (btnConfirmarEliminar) {
            btnConfirmarEliminar.addEventListener('click', () => this.confirmarEliminar());
        }

        // Limpiar modal al cerrar
        const modalCategoria = document.getElementById('modalCategoria');
        if (modalCategoria) {
            modalCategoria.addEventListener('hidden.bs.modal', () => this.limpiarModal());
        }
    }

    async cargarCategorias() {
        try {
            const response = await fetch('/api/categorias/');
            const data = await response.json();

            if (data.success) {
                this.categorias = data.categorias;
                this.renderizarCategorias();
            } else {
                console.error('Error al cargar categorías:', data.message);
                this.mostrarError('Error al cargar categorías');
            }
        } catch (error) {
            console.error('Error en la petición:', error);
            this.mostrarError('Error de conexión');
        }
    }

    async cargarEstadisticas() {
        try {
            const response = await fetch('/api/categorias/estadisticas');
            const data = await response.json();

            if (data.success) {
                this.actualizarEstadisticas(data);
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }

    actualizarEstadisticas(data) {
        // Total de categorías
        const totalCategorias = document.getElementById('totalCategorias');
        if (totalCategorias) {
            totalCategorias.textContent = data.total_categorias || 0;
        }

        // Total de artículos (suma de todas las categorías)
        const totalArticulos = document.getElementById('totalArticulos');
        if (totalArticulos && data.categorias_top) {
            const total = data.categorias_top.reduce((sum, cat) => sum + cat.total_articulos, 0);
            totalArticulos.textContent = total;
        }

        // Categoría más usada
        const categoriaTop = document.getElementById('categoriaTop');
        if (categoriaTop && data.categorias_top && data.categorias_top.length > 0) {
            const topCat = data.categorias_top[0];
            categoriaTop.textContent = `${topCat.prefijo} (${topCat.total_articulos})`;
        }

        // Próximo código (ejemplo con la primera categoría)
        const proximoCodigo = document.getElementById('proximoCodigo');
        if (proximoCodigo && this.categorias.length > 0) {
            const primeraCat = this.categorias[0];
            const año = new Date().getFullYear();
            const siguienteNum = (primeraCat.ultimo_numero || 0) + 1;
            proximoCodigo.textContent = `${primeraCat.prefijo}-${año}-${String(siguienteNum).padStart(3, '0')}`;
        }
    }

    renderizarCategorias() {
        const container = document.getElementById('categoriasContainer');
        if (!container) return;

        if (this.categorias.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <i class="fas fa-tags fa-3x mb-3"></i>
                        <h5>No hay categorías disponibles</h5>
                        <p>Crea tu primera categoría para empezar a organizar el inventario</p>
                    </div>
                </div>
            `;
            return;
        }

        let html = '';
        this.categorias.forEach(categoria => {
            const badgeClass = categoria.activo ? 'bg-success' : 'bg-secondary';
            const estadoText = categoria.activo ? 'Activa' : 'Inactiva';

            html += `
                <div class="col-lg-6 col-xl-4 mb-3">
                    <div class="card category-card h-100" style="border-left-color: ${categoria.color}">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div class="d-flex align-items-center">
                                    <div class="color-indicator" style="background-color: ${categoria.color}"></div>
                                    <h6 class="mb-0">${categoria.nombre}</h6>
                                </div>
                                <span class="badge ${badgeClass}">${estadoText}</span>
                            </div>
                            
                            <div class="category-prefix mb-2">${categoria.prefijo}</div>
                            
                            ${categoria.descripcion ? `<p class="text-muted small mb-2">${categoria.descripcion}</p>` : ''}
                            
                            <div class="category-stats d-flex justify-content-between">
                                <span><i class="fas fa-boxes"></i> ${categoria.total_articulos || 0} artículos</span>
                                <span><i class="fas fa-hashtag"></i> #${String(categoria.ultimo_numero || 0).padStart(3, '0')}</span>
                            </div>
                            
                            <div class="mt-3">
                                <div class="btn-group w-100">
                                    <button class="btn btn-outline-primary btn-sm" 
                                            onclick="categoriasManager.editarCategoria(${categoria.id})">
                                        <i class="fas fa-edit"></i> Editar
                                    </button>
                                    <button class="btn btn-outline-info btn-sm" 
                                            onclick="categoriasManager.generarCodigo(${categoria.id})">
                                        <i class="fas fa-barcode"></i> Código
                                    </button>
                                    <button class="btn btn-outline-danger btn-sm" 
                                            onclick="categoriasManager.eliminarCategoria(${categoria.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    async guardarCategoria(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const data = {
            nombre: document.getElementById('nombre').value.trim(),
            prefijo: document.getElementById('prefijo').value.trim().toUpperCase(),
            descripcion: document.getElementById('descripcion').value.trim(),
            color: document.getElementById('color').value
        };

        // Validaciones
        if (!data.nombre || !data.prefijo) {
            this.mostrarError('El nombre y prefijo son requeridos');
            return;
        }

        if (data.prefijo.length > 10) {
            this.mostrarError('El prefijo no debe exceder 10 caracteres');
            return;
        }

        try {
            const url = this.categoriaEditando ?
                `/api/categorias/${this.categoriaEditando}` :
                '/api/categorias/';

            const method = this.categoriaEditando ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.mostrarExito(result.message);
                this.cerrarModal();
                this.cargarCategorias();
                this.cargarEstadisticas();
            } else {
                this.mostrarError(result.message);
            }
        } catch (error) {
            console.error('Error guardando categoría:', error);
            this.mostrarError('Error de conexión');
        }
    }

    editarCategoria(id) {
        const categoria = this.categorias.find(c => c.id === id);
        if (!categoria) return;

        this.categoriaEditando = id;

        // Llenar el formulario
        document.getElementById('categoriaId').value = categoria.id;
        document.getElementById('nombre').value = categoria.nombre;
        document.getElementById('prefijo').value = categoria.prefijo;
        document.getElementById('descripcion').value = categoria.descripcion || '';
        document.getElementById('color').value = categoria.color;

        // Cambiar título del modal
        document.querySelector('#modalCategoria .modal-title').textContent = 'Editar Categoría';

        // Mostrar preview
        this.updatePreview();

        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('modalCategoria'));
        modal.show();
    }

    eliminarCategoria(id) {
        this.categoriaEditando = id;
        const modal = new bootstrap.Modal(document.getElementById('modalEliminar'));
        modal.show();
    }

    async confirmarEliminar() {
        if (!this.categoriaEditando) return;

        try {
            const response = await fetch(`/api/categorias/${this.categoriaEditando}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.mostrarExito(result.message);
                this.cerrarModalEliminar();
                this.cargarCategorias();
                this.cargarEstadisticas();
            } else {
                this.mostrarError(result.message);
            }
        } catch (error) {
            console.error('Error eliminando categoría:', error);
            this.mostrarError('Error de conexión');
        }
    }

    async generarCodigo(id) {
        try {
            const response = await fetch(`/api/categorias/${id}/codigo`);
            const result = await response.json();

            if (result.success) {
                // Mostrar el código generado en un modal o alert
                alert(`Próximo código: ${result.codigo}`);
            } else {
                this.mostrarError(result.message);
            }
        } catch (error) {
            console.error('Error generando código:', error);
            this.mostrarError('Error de conexión');
        }
    }

    updatePreview() {
        const prefijo = document.getElementById('prefijo').value.trim().toUpperCase();
        const previewContainer = document.getElementById('previewContainer');
        const previewCodigo = document.getElementById('previewCodigo');
        const ejemploCodigo = document.getElementById('ejemploCodigo');

        if (prefijo) {
            const año = new Date().getFullYear();
            previewCodigo.textContent = `${prefijo}-YYYY-NNN`;
            ejemploCodigo.textContent = `${prefijo}-${año}-001`;
            previewContainer.classList.remove('d-none');
        } else {
            previewContainer.classList.add('d-none');
        }
    }

    limpiarModal() {
        this.categoriaEditando = null;
        document.getElementById('formCategoria').reset();
        document.querySelector('#modalCategoria .modal-title').textContent = 'Nueva Categoría';
        document.getElementById('previewContainer').classList.add('d-none');
    }

    cerrarModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalCategoria'));
        if (modal) modal.hide();
    }

    cerrarModalEliminar() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalEliminar'));
        if (modal) modal.hide();
        this.categoriaEditando = null;
    }

    mostrarError(mensaje) {
        // Implementar sistema de notificaciones
        console.error(mensaje);
        alert(`Error: ${mensaje}`);
    }

    mostrarExito(mensaje) {
        // Implementar sistema de notificaciones
        console.log(mensaje);
        alert(`Éxito: ${mensaje}`);
    }
}

// Inicializar cuando la página esté lista
let categoriasManager;
document.addEventListener('DOMContentLoaded', function () {
    categoriasManager = new CategoriasManager();
});