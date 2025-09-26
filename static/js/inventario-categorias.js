/**
 * Extensión para inventario.js - Gestión de Categorías Dinámicas
 * Se debe incluir después de inventario.js
 */

console.log('🔧 inventario-categorias.js cargado correctamente');

// Clase principal para gestión de categorías en inventario
class InventarioCategoriasManager {
    constructor() {
        this.categorias = [];
        this.init();
    }

    async init() {
        try {
            await this.cargarCategorias();
            this.setupEventListeners();
            console.log('✅ Gestor de categorías inicializado');
        } catch (error) {
            console.error('❌ Error inicializando gestor de categorías:', error);
        }
    }

    async cargarCategorias() {
        try {
            const response = await fetch('/api/categorias/');
            const data = await response.json();

            if (data.success) {
                this.categorias = data.categorias;
                this.actualizarSelectoresCategorias();
                console.log('✅ Categorías cargadas:', this.categorias.length);
            } else {
                console.error('Error cargando categorías:', data.message);
            }
        } catch (error) {
            console.error('Error en petición de categorías:', error);
        }
    }

    actualizarSelectoresCategorias() {
        const selectores = ['filtro-categoria', 'nuevo-categoria'];

        selectores.forEach(selectorId => {
            const select = document.getElementById(selectorId);
            if (select) {
                // Guardar la primera opción
                const primeraOpcion = select.querySelector('option[value=""]');
                const valorActual = select.value;

                // Limpiar opciones
                select.innerHTML = '';

                // Restaurar primera opción
                if (primeraOpcion) {
                    select.appendChild(primeraOpcion);
                }

                // Añadir categorías dinámicas
                this.categorias.forEach(categoria => {
                    if (categoria.activo) {
                        const option = document.createElement('option');
                        option.value = categoria.id;
                        option.textContent = `${categoria.nombre} (${categoria.prefijo})`;
                        option.dataset.prefijo = categoria.prefijo;
                        option.dataset.color = categoria.color;
                        option.dataset.ultimo = categoria.ultimo_numero;
                        select.appendChild(option);
                    }
                });

                // Restaurar valor seleccionado si existe
                if (valorActual) {
                    select.value = valorActual;
                }
            }
        });
    }

    categoriaSeleccionada() {
        const select = document.getElementById('nuevo-categoria');
        const previewSpan = document.getElementById('categoria-preview');
        const codigoInput = document.getElementById('nuevo-codigo');
        const codigoPreview = document.getElementById('codigo-preview');

        if (select && select.value) {
            const categoria = this.categorias.find(c => c.id == select.value);
            if (categoria) {
                const año = new Date().getFullYear();
                const siguienteNum = (categoria.ultimo_numero || 0) + 1;
                const proximoCodigo = `${categoria.prefijo}-${año}-${String(siguienteNum).padStart(3, '0')}`;

                // Mostrar preview de categoría
                if (previewSpan) {
                    previewSpan.innerHTML = `
                        <span class="badge" style="background-color: ${categoria.color}">
                            ${categoria.prefijo}
                        </span>
                        ${categoria.nombre}
                    `;
                }

                // Mostrar preview de código
                if (codigoPreview) {
                    codigoPreview.innerHTML = `Próximo código: <strong>${proximoCodigo}</strong>`;
                }

                // Limpiar código actual para generar uno nuevo
                if (codigoInput) {
                    codigoInput.value = '';
                    codigoInput.placeholder = 'Se generará automáticamente';
                }

                // Habilitar botón de generar código
                const btnGenerar = document.getElementById('btn-generar-codigo');
                if (btnGenerar) {
                    btnGenerar.disabled = false;
                }
            }
        } else {
            // Limpiar previews
            if (previewSpan) previewSpan.innerHTML = '';
            if (codigoPreview) codigoPreview.innerHTML = '';
            if (codigoInput) {
                codigoInput.placeholder = 'Ingrese código manualmente';
            }

            // Deshabilitar botón de generar código
            const btnGenerar = document.getElementById('btn-generar-codigo');
            if (btnGenerar) {
                btnGenerar.disabled = true;
            }
        }
    }

    async generarCodigoAutomatico() {
        const categoriaSelect = document.getElementById('nuevo-categoria');
        const codigoInput = document.getElementById('nuevo-codigo');

        if (!categoriaSelect || !categoriaSelect.value) {
            this.mostrarMensaje('Por favor seleccione una categoría primero', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/categorias/${categoriaSelect.value}/codigo`);
            const data = await response.json();

            if (data.success) {
                codigoInput.value = data.codigo;

                // Actualizar el último número en la categoría local
                const categoria = this.categorias.find(c => c.id == categoriaSelect.value);
                if (categoria) {
                    categoria.ultimo_numero = data.siguiente_numero;
                }

                this.mostrarMensaje(`Código generado: ${data.codigo}`, 'success');
                console.log('✅ Código generado:', data.codigo);
            } else {
                this.mostrarMensaje('Error al generar código: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('Error generando código:', error);
            this.mostrarMensaje('Error de conexión', 'error');
        }
    }

    async crearCategoriaRapida() {
        const nombre = document.getElementById('rapida-nombre').value.trim();
        const prefijo = document.getElementById('rapida-prefijo').value.trim().toUpperCase();
        const color = document.getElementById('rapida-color').value;

        if (!nombre || !prefijo) {
            this.mostrarMensaje('El nombre y prefijo son requeridos', 'warning');
            return;
        }

        if (prefijo.length > 10) {
            this.mostrarMensaje('El prefijo no debe exceder 10 caracteres', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/categorias/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, prefijo, color })
            });

            const data = await response.json();

            if (data.success) {
                // Recargar categorías
                await this.cargarCategorias();

                // Seleccionar la nueva categoría
                const select = document.getElementById('nuevo-categoria');
                if (select && data.categoria) {
                    select.value = data.categoria.id;
                    this.categoriaSeleccionada();
                }

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalCategoria'));
                if (modal) modal.hide();

                // Limpiar formulario
                document.getElementById('formCategoriaRapida').reset();

                this.mostrarMensaje('Categoría creada exitosamente', 'success');
            } else {
                this.mostrarMensaje('Error: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('Error creando categoría:', error);
            this.mostrarMensaje('Error de conexión', 'error');
        }
    }

    setupEventListeners() {
        // Prefijo automático en mayúsculas
        const prefijoInput = document.getElementById('rapida-prefijo');
        if (prefijoInput) {
            prefijoInput.addEventListener('input', function () {
                this.value = this.value.toUpperCase();
            });
        }

        // Event listener para cambio de categoría - GENERACIÓN AUTOMÁTICA DE CÓDIGO
        const categoriaSelect = document.getElementById('nuevo-categoria');
        if (categoriaSelect) {
            console.log('🔗 Vinculando evento change a selector de categoría');
            categoriaSelect.addEventListener('change', (event) => {
                console.log('🔄 Categoría seleccionada:', event.target.value);

                if (event.target.value) {
                    console.log('🚀 Generando código automáticamente...');
                    this.categoriaSeleccionada();

                    // Generar código automáticamente al seleccionar categoría
                    setTimeout(() => {
                        this.generarCodigoAutomatico();
                    }, 100);
                } else {
                    // Limpiar campos si no hay categoría seleccionada
                    const codigoInput = document.getElementById('nuevo-codigo');
                    const codigoPreview = document.getElementById('codigo-preview');
                    const categoriaPreview = document.getElementById('categoria-preview');

                    if (codigoInput) codigoInput.value = '';
                    if (codigoPreview) codigoPreview.innerHTML = 'Seleccione una categoría para generar el código automáticamente';
                    if (categoriaPreview) categoriaPreview.innerHTML = 'Seleccione una categoría';
                }
            });
        } else {
            console.warn('⚠️ No se encontró el elemento #nuevo-categoria');
        }

        console.log('✅ Event listeners de categorías configurados');
    }

    mostrarMensaje(mensaje, tipo = 'info') {
        // Implementar sistema de notificaciones
        console.log(`${tipo.toUpperCase()}: ${mensaje}`);

        // Por ahora usar alert, después se puede mejorar con toasts
        if (tipo === 'error' || tipo === 'warning') {
            alert(mensaje);
        } else {
            // Para mensajes de éxito, podrían usar console.log solamente
            console.log('ℹ️', mensaje);
        }
    }

    // Método para obtener categoría por ID
    obtenerCategoria(id) {
        return this.categorias.find(c => c.id == id);
    }

    // Método para filtrar por categoría (usar en búsquedas)
    obtenerCategoriasActivas() {
        return this.categorias.filter(c => c.activo);
    }
}

// Instancia global del gestor de categorías
let categoriasManager;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    console.log('🔧 DOM cargado, inicializando gestor de categorías...');

    // Esperar un poco para que inventario.js se haya cargado completamente
    setTimeout(() => {
        try {
            categoriasManager = new InventarioCategoriasManager();

            // Hacer global para acceso desde HTML
            window.inventarioApp = categoriasManager;

            console.log('✅ Gestor de categorías inicializado correctamente');
        } catch (error) {
            console.error('❌ Error inicializando gestor de categorías:', error);
        }
    }, 500);
});

// Funciones globales para compatibilidad con el HTML
window.categoriaSeleccionada = function () {
    if (categoriasManager) {
        categoriasManager.categoriaSeleccionada();
    }
};

window.generarCodigoAutomatico = function () {
    if (categoriasManager) {
        categoriasManager.generarCodigoAutomatico();
    }
};

window.crearCategoriaRapida = function () {
    if (categoriasManager) {
        categoriasManager.crearCategoriaRapida();
    }
};