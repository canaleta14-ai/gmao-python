/**
 * Componente de Paginación Reutilizable para GMAO
 * 
 * Uso:
 * 1. Crear instancia: const pagination = new Pagination('elemento-paginacion', cargarDatos);
 * 2. Renderizar: pagination.render(page, perPage, total);
 * 3. Configurar: pagination.setPerPage(20);
 * 
 * Ejemplo:
 * const paginacionUsuarios = new Pagination('paginacion-usuarios', cargarUsuarios);
 * paginacionUsuarios.render(1, 10, 150);
 */

class Pagination {
    constructor(containerId, loadFunction, options = {}) {
        this.containerId = containerId;
        this.loadFunction = loadFunction;
        this.perPage = options.perPage || 10;
        this.currentPage = 1;
        this.total = 0;
        this.maxVisiblePages = options.maxVisiblePages || 5;

        // Configuraciones adicionales
        this.showInfo = options.showInfo !== false; // Por defecto true
        this.showSizeSelector = options.showSizeSelector !== false; // Por defecto true
        this.pageSizes = options.pageSizes || [10, 25, 50, 100];
        this.className = options.className || '';
    }

    /**
     * Renderiza la paginación completa
     */
    render(page, perPage, total) {
        this.currentPage = page;
        this.perPage = perPage;
        this.total = total;

        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found`);
            return;
        }

        container.innerHTML = this.generateHTML();
    }

    /**
     * Genera el HTML completo de la paginación
     */
    generateHTML() {
        const totalPages = Math.ceil(this.total / this.perPage);

        if (totalPages <= 1 && !this.showInfo && !this.showSizeSelector) {
            return '';
        }

        let html = `<div class="d-flex justify-content-between align-items-center ${this.className}">`;

        // Información de registros
        if (this.showInfo) {
            html += this.generateInfo();
        }

        // Navegación de páginas
        if (totalPages > 1) {
            html += this.generateNavigation(totalPages);
        }

        // Selector de tamaño de página
        if (this.showSizeSelector) {
            html += this.generateSizeSelector();
        }

        html += '</div>';
        return html;
    }

    /**
     * Genera información de registros
     */
    generateInfo() {
        const start = ((this.currentPage - 1) * this.perPage) + 1;
        const end = Math.min(this.currentPage * this.perPage, this.total);

        return `
            <div class="pagination-info">
                <small class="text-muted">
                    Mostrando ${start} - ${end} de ${this.total} registros
                </small>
            </div>
        `;
    }

    /**
     * Genera la navegación de páginas
     */
    generateNavigation(totalPages) {
        let html = `
            <nav aria-label="Navegación de páginas">
                <ul class="pagination mb-0">
        `;

        // Botón anterior
        const prevDisabled = this.currentPage === 1;
        html += `
            <li class="page-item ${prevDisabled ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="event.preventDefault(); ${this.getFunctionCall(this.currentPage - 1)}" 
                   ${prevDisabled ? 'tabindex="-1" aria-disabled="true"' : ''}>
                    <i class="bi bi-chevron-left"></i>
                    <span class="sr-only">Anterior</span>
                </a>
            </li>
        `;

        // Números de página
        const pageNumbers = this.calculateVisiblePages(totalPages);

        // Primera página si no está visible
        if (pageNumbers[0] > 1) {
            html += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="event.preventDefault(); ${this.getFunctionCall(1)}">1</a>
                </li>
            `;
            if (pageNumbers[0] > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }

        // Páginas visibles
        pageNumbers.forEach(pageNum => {
            const isActive = pageNum === this.currentPage;
            html += `
                <li class="page-item ${isActive ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="event.preventDefault(); ${this.getFunctionCall(pageNum)}"
                       ${isActive ? 'aria-current="page"' : ''}>${pageNum}</a>
                </li>
            `;
        });

        // Última página si no está visible
        if (pageNumbers[pageNumbers.length - 1] < totalPages) {
            if (pageNumbers[pageNumbers.length - 1] < totalPages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="event.preventDefault(); ${this.getFunctionCall(totalPages)}">${totalPages}</a>
                </li>
            `;
        }

        // Botón siguiente
        const nextDisabled = this.currentPage === totalPages;
        html += `
            <li class="page-item ${nextDisabled ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="event.preventDefault(); ${this.getFunctionCall(this.currentPage + 1)}"
                   ${nextDisabled ? 'tabindex="-1" aria-disabled="true"' : ''}>
                    <i class="bi bi-chevron-right"></i>
                    <span class="sr-only">Siguiente</span>
                </a>
            </li>
        `;

        html += `
                </ul>
            </nav>
        `;

        return html;
    }

    /**
     * Genera selector de tamaño de página
     */
    generateSizeSelector() {
        let html = `
            <div class="pagination-size-selector">
                <div class="d-flex align-items-center">
                    <label for="${this.containerId}-page-size" class="form-label mb-0 me-2">
                        <small>Mostrar:</small>
                    </label>
                    <select id="${this.containerId}-page-size" class="form-select form-select-sm" 
                            onchange="${this.getChangeSizeCall()}" style="width: auto;">
        `;

        this.pageSizes.forEach(size => {
            const selected = size === this.perPage ? 'selected' : '';
            html += `<option value="${size}" ${selected}>${size}</option>`;
        });

        html += `
                    </select>
                </div>
            </div>
        `;

        return html;
    }

    /**
     * Calcula las páginas visibles
     */
    calculateVisiblePages(totalPages) {
        const half = Math.floor(this.maxVisiblePages / 2);
        let start = Math.max(1, this.currentPage - half);
        let end = Math.min(totalPages, start + this.maxVisiblePages - 1);

        // Ajustar si estamos cerca del final
        if (end - start + 1 < this.maxVisiblePages) {
            start = Math.max(1, end - this.maxVisiblePages + 1);
        }

        const pages = [];
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }
        return pages;
    }

    /**
     * Genera la llamada a la función con parámetros
     */
    getFunctionCall(page) {
        return `${this.loadFunction.name}(${page})`;
    }

    /**
     * Genera la llamada para cambio de tamaño
     */
    getChangeSizeCall() {
        return `window.paginationInstances['${this.containerId}'].changePageSize(this.value)`;
    }

    /**
     * Cambia el tamaño de página
     */
    changePageSize(newSize) {
        this.perPage = parseInt(newSize);
        this.loadFunction(1); // Volver a la primera página
    }

    /**
     * Configuración del tamaño de página
     */
    setPerPage(perPage) {
        this.perPage = perPage;
    }

    /**
     * Obtiene información actual
     */
    getInfo() {
        return {
            currentPage: this.currentPage,
            perPage: this.perPage,
            total: this.total,
            totalPages: Math.ceil(this.total / this.perPage)
        };
    }

    /**
     * Navega a una página específica
     */
    goToPage(page) {
        const totalPages = Math.ceil(this.total / this.perPage);
        if (page >= 1 && page <= totalPages) {
            this.loadFunction(page);
        }
    }

    /**
     * Refresca la paginación actual
     */
    refresh() {
        this.loadFunction(this.currentPage);
    }
}

// Registro global de instancias para callbacks
window.paginationInstances = window.paginationInstances || {};

/**
 * Función helper para crear y registrar una instancia de paginación
 */
function createPagination(containerId, loadFunction, options = {}) {
    const pagination = new Pagination(containerId, loadFunction, options);
    window.paginationInstances[containerId] = pagination;
    return pagination;
}

/**
 * Función helper para paginación simple (solo números de página)
 */
function createSimplePagination(containerId, loadFunction, options = {}) {
    const simpleOptions = {
        ...options,
        showInfo: false,
        showSizeSelector: false
    };
    return createPagination(containerId, loadFunction, simpleOptions);
}

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Pagination, createPagination, createSimplePagination };
}