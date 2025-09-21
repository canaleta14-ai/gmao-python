// ========== COMPONENTE DE AUTOCOMPLETADO ==========
/**
 * Sistema de autocompletado dinámico para inputs y selects
 * Soporta búsqueda en tiempo real con debouncing y filtrado local/remoto
 */

class AutoComplete {
    constructor(options) {
        this.element = options.element;
        this.apiUrl = options.apiUrl;
        this.searchKey = options.searchKey || 'q';
        this.displayKey = options.displayKey || 'name';
        this.valueKey = options.valueKey || 'id';
        this.minChars = options.minChars || 2;
        this.debounceTime = options.debounceTime || 300;
        this.maxResults = options.maxResults || 10;
        this.placeholder = options.placeholder || 'Buscar...';
        this.noResultsText = options.noResultsText || 'Sin resultados';
        this.loadingText = options.loadingText || 'Cargando...';
        this.onSelect = options.onSelect || (() => { });
        this.onInput = options.onInput || (() => { });
        this.customFilter = options.customFilter || null;
        this.localData = options.localData || null;
        this.allowFreeText = options.allowFreeText || false;

        this.debounceTimer = null;
        this.isLoading = false;
        this.currentResults = [];
        this.selectedIndex = -1;
        this.isOpen = false;

        this.init();
    }

    init() {
        this.createWrapper();
        this.createInput();
        this.createDropdown();
        this.bindEvents();

        // Si el elemento original ya tiene valor, mostrarlo
        if (this.originalElement.value) {
            this.input.value = this.originalElement.value;
        }
    }

    createWrapper() {
        this.originalElement = this.element;
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'autocomplete-wrapper position-relative';
        this.wrapper.style.width = '100%';

        // Insertar wrapper antes del elemento original
        this.originalElement.parentNode.insertBefore(this.wrapper, this.originalElement);
        this.wrapper.appendChild(this.originalElement);

        // Ocultar elemento original
        this.originalElement.style.display = 'none';
    }

    createInput() {
        this.input = document.createElement('input');
        this.input.type = 'text';
        this.input.className = this.originalElement.className;
        this.input.placeholder = this.placeholder;
        this.input.autocomplete = 'off';

        // Copiar atributos importantes
        ['id', 'name', 'required', 'disabled'].forEach(attr => {
            if (this.originalElement.hasAttribute(attr)) {
                this.input.setAttribute(attr, this.originalElement.getAttribute(attr));
            }
        });

        // Cambiar ID del original para evitar duplicados
        if (this.originalElement.id) {
            this.originalElement.id = this.originalElement.id + '_hidden';
        }

        this.wrapper.appendChild(this.input);
    }

    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown position-absolute w-100 bg-white border rounded shadow-sm';
        this.dropdown.style.cssText = `
            top: 100%;
            left: 0;
            z-index: 1050;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        `;
        this.wrapper.appendChild(this.dropdown);
    }

    bindEvents() {
        // Input events
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));
        this.input.addEventListener('blur', (e) => this.handleBlur(e));

        // Dropdown events
        this.dropdown.addEventListener('mousedown', (e) => e.preventDefault());
        this.dropdown.addEventListener('click', (e) => this.handleDropdownClick(e));

        // Document click para cerrar
        document.addEventListener('click', (e) => {
            if (!this.wrapper.contains(e.target)) {
                this.close();
            }
        });
    }

    handleInput(e) {
        const value = e.target.value;
        this.onInput(value);

        if (value.length >= this.minChars) {
            this.debouncedSearch(value);
        } else {
            this.close();
            this.clearOriginalValue();
        }
    }

    handleKeydown(e) {
        if (!this.isOpen) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.navigateDown();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateUp();
                break;
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectItem(this.currentResults[this.selectedIndex]);
                }
                break;
            case 'Escape':
                e.preventDefault();
                this.close();
                break;
        }
    }

    handleFocus(e) {
        if (this.input.value.length >= this.minChars) {
            this.search(this.input.value);
        }
    }

    handleBlur(e) {
        // Delay para permitir clicks en dropdown
        setTimeout(() => {
            if (!this.wrapper.contains(document.activeElement)) {
                this.close();
                this.validateInput();
            }
        }, 150);
    }

    handleDropdownClick(e) {
        const item = e.target.closest('.autocomplete-item');
        if (item) {
            const index = Array.from(this.dropdown.children).indexOf(item);
            if (index >= 0 && this.currentResults[index]) {
                this.selectItem(this.currentResults[index]);
            }
        }
    }

    debouncedSearch(query) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.search(query);
        }, this.debounceTime);
    }

    async search(query) {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading();

        try {
            let results = [];

            if (this.localData) {
                // Búsqueda local
                results = this.searchLocal(query, this.localData);
            } else if (this.apiUrl) {
                // Búsqueda remota
                results = await this.searchRemote(query);
            }

            this.currentResults = results.slice(0, this.maxResults);
            this.renderResults();

        } catch (error) {
            console.error('Error en autocompletado:', error);
            this.showError();
        } finally {
            this.isLoading = false;
        }
    }

    searchLocal(query, data) {
        const lowercaseQuery = query.toLowerCase();
        return data.filter(item => {
            if (this.customFilter) {
                return this.customFilter(item, query);
            }
            const displayValue = this.getDisplayValue(item).toLowerCase();
            return displayValue.includes(lowercaseQuery);
        });
    }

    async searchRemote(query) {
        const url = new URL(this.apiUrl, window.location.origin);
        url.searchParams.set(this.searchKey, query);
        url.searchParams.set('limit', this.maxResults);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        return Array.isArray(data) ? data : (data.items || data.results || []);
    }

    renderResults() {
        this.dropdown.innerHTML = '';
        this.selectedIndex = -1;

        if (this.currentResults.length === 0) {
            this.showNoResults();
            return;
        }

        this.currentResults.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item px-3 py-2 cursor-pointer hover-bg-light';
            div.innerHTML = this.formatItem(item);
            div.setAttribute('data-index', index);
            this.dropdown.appendChild(div);
        });

        this.open();
    }

    formatItem(item) {
        const displayValue = this.getDisplayValue(item);
        const query = this.input.value;

        // Resaltar texto coincidente
        if (query && displayValue.toLowerCase().includes(query.toLowerCase())) {
            const regex = new RegExp(`(${query})`, 'gi');
            return displayValue.replace(regex, '<strong>$1</strong>');
        }

        return displayValue;
    }

    getDisplayValue(item) {
        if (typeof item === 'string') return item;
        if (typeof this.displayKey === 'function') return this.displayKey(item);
        return item[this.displayKey] || item.name || item.label || String(item);
    }

    getValue(item) {
        if (typeof item === 'string') return item;
        if (typeof this.valueKey === 'function') return this.valueKey(item);
        return item[this.valueKey] || item.id || item.value || item;
    }

    navigateDown() {
        this.selectedIndex = Math.min(this.selectedIndex + 1, this.currentResults.length - 1);
        this.updateHighlight();
    }

    navigateUp() {
        this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
        this.updateHighlight();
    }

    updateHighlight() {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        items.forEach((item, index) => {
            item.classList.toggle('bg-primary', index === this.selectedIndex);
            item.classList.toggle('text-white', index === this.selectedIndex);
        });
    }

    selectItem(item) {
        const displayValue = this.getDisplayValue(item);
        const value = this.getValue(item);

        this.input.value = displayValue;
        this.originalElement.value = value;

        // Trigger change event
        this.originalElement.dispatchEvent(new Event('change', { bubbles: true }));

        this.close();
        this.onSelect(item, value, displayValue);
    }

    validateInput() {
        if (!this.allowFreeText && this.input.value) {
            // Verificar si el valor actual corresponde a una opción válida
            const currentValue = this.input.value.toLowerCase();
            const validItem = this.currentResults.find(item =>
                this.getDisplayValue(item).toLowerCase() === currentValue
            );

            if (!validItem) {
                this.input.value = '';
                this.clearOriginalValue();
            }
        }
    }

    clearOriginalValue() {
        this.originalElement.value = '';
        this.originalElement.dispatchEvent(new Event('change', { bubbles: true }));
    }

    open() {
        this.isOpen = true;
        this.dropdown.style.display = 'block';
    }

    close() {
        this.isOpen = false;
        this.dropdown.style.display = 'none';
        this.selectedIndex = -1;
    }

    showLoading() {
        this.dropdown.innerHTML = `
            <div class="px-3 py-2 text-muted">
                <i class="bi bi-hourglass-split me-2"></i>${this.loadingText}
            </div>
        `;
        this.open();
    }

    showNoResults() {
        this.dropdown.innerHTML = `
            <div class="px-3 py-2 text-muted">
                <i class="bi bi-search me-2"></i>${this.noResultsText}
            </div>
        `;
        this.open();
    }

    showError() {
        this.dropdown.innerHTML = `
            <div class="px-3 py-2 text-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>Error al cargar datos
            </div>
        `;
        this.open();
    }

    // Métodos públicos
    setValue(value, displayValue = null) {
        this.originalElement.value = value;
        this.input.value = displayValue || value;
    }

    clear() {
        this.input.value = '';
        this.originalElement.value = '';
        this.close();
    }

    destroy() {
        clearTimeout(this.debounceTimer);
        this.wrapper.parentNode.insertBefore(this.originalElement, this.wrapper);
        this.wrapper.remove();
        this.originalElement.style.display = '';
    }
}

// ========== HELPER FUNCTIONS ==========

/**
 * Inicializar autocompletado en un elemento
 */
function initAutoComplete(selector, options) {
    const elements = document.querySelectorAll(selector);
    const instances = [];

    elements.forEach(element => {
        const instance = new AutoComplete({
            element: element,
            ...options
        });
        instances.push(instance);
    });

    return instances.length === 1 ? instances[0] : instances;
}

/**
 * Configuraciones predefinidas para diferentes tipos de campos
 */
const AutoCompletePresets = {
    activos: {
        apiUrl: '/activos/api',
        searchKey: 'nombre',
        displayKey: item => `${item.nombre} (${item.codigo})`,
        valueKey: 'id',
        placeholder: 'Buscar activo...',
        customFilter: (item, query) => {
            const q = query.toLowerCase();
            return item.nombre.toLowerCase().includes(q) ||
                item.codigo.toLowerCase().includes(q) ||
                (item.ubicacion && item.ubicacion.toLowerCase().includes(q));
        }
    },

    usuarios: {
        apiUrl: '/usuarios/api',
        searchKey: 'nombre',
        displayKey: item => `${item.nombre} - ${item.rol}`,
        valueKey: 'id',
        placeholder: 'Buscar usuario...',
        customFilter: (item, query) => {
            const q = query.toLowerCase();
            return item.nombre.toLowerCase().includes(q) ||
                item.username.toLowerCase().includes(q) ||
                item.email.toLowerCase().includes(q);
        }
    },

    proveedores: {
        apiUrl: '/proveedores/api',
        searchKey: 'nombre',
        displayKey: item => `${item.nombre} (${item.nif})`,
        valueKey: 'id',
        placeholder: 'Buscar proveedor...',
        customFilter: (item, query) => {
            const q = query.toLowerCase();
            return item.nombre.toLowerCase().includes(q) ||
                item.nif.toLowerCase().includes(q) ||
                (item.contacto && item.contacto.toLowerCase().includes(q));
        }
    },

    ubicaciones: {
        localData: [], // Se llenará dinámicamente
        displayKey: 'ubicacion',
        valueKey: 'ubicacion',
        placeholder: 'Buscar ubicación...',
        allowFreeText: true
    },

    fabricantes: {
        localData: [], // Se llenará dinámicamente
        displayKey: 'fabricante',
        valueKey: 'fabricante',
        placeholder: 'Buscar fabricante...',
        allowFreeText: true
    }
};

// Exportar para uso global
window.AutoComplete = AutoComplete;
window.initAutoComplete = initAutoComplete;
window.AutoCompletePresets = AutoCompletePresets;