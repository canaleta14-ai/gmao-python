// ============================================================================
// MEJORAS DE ACCESIBILIDAD - Sistema GMAO
// ============================================================================
// Este script aplica mejoras automáticas de accesibilidad en toda la aplicación
// Objetivo: Mejorar puntuación Lighthouse de 79 a 90+
// ============================================================================

(function() {
    'use strict';
    
    console.log('🔍 Aplicando mejoras de accesibilidad...');
    
    // ========================================================================
    // 1. AGREGAR ARIA-LABELS A BOTONES SOLO CON ICONOS
    // ========================================================================
    
    function agregarAriaLabelsABotones() {
        // Seleccionar todos los botones que solo tienen iconos
        const botonesIcono = document.querySelectorAll('button:not([aria-label]), a.btn:not([aria-label])');
        
        botonesIcono.forEach(boton => {
            // Solo procesar si el botón tiene un icono pero no texto
            const icono = boton.querySelector('i.bi');
            const textoBoton = boton.textContent.trim();
            
            if (icono && textoBoton.length === 0) {
                // Determinar la acción basada en la clase del icono
                const claseIcono = icono.className;
                let ariaLabel = '';
                
                if (claseIcono.includes('bi-pencil')) {
                    ariaLabel = 'Editar';
                } else if (claseIcono.includes('bi-trash')) {
                    ariaLabel = 'Eliminar';
                } else if (claseIcono.includes('bi-eye')) {
                    ariaLabel = 'Ver detalles';
                } else if (claseIcono.includes('bi-plus')) {
                    ariaLabel = 'Agregar';
                } else if (claseIcono.includes('bi-x') || claseIcono.includes('bi-x-lg')) {
                    ariaLabel = 'Cerrar';
                } else if (claseIcono.includes('bi-download')) {
                    ariaLabel = 'Descargar';
                } else if (claseIcono.includes('bi-upload')) {
                    ariaLabel = 'Subir archivo';
                } else if (claseIcono.includes('bi-search')) {
                    ariaLabel = 'Buscar';
                } else if (claseIcono.includes('bi-filter')) {
                    ariaLabel = 'Filtrar';
                } else if (claseIcono.includes('bi-printer')) {
                    ariaLabel = 'Imprimir';
                } else if (claseIcono.includes('bi-save')) {
                    ariaLabel = 'Guardar';
                } else if (claseIcono.includes('bi-arrow-left')) {
                    ariaLabel = 'Volver';
                } else if (claseIcono.includes('bi-arrow-right')) {
                    ariaLabel = 'Siguiente';
                } else if (claseIcono.includes('bi-check')) {
                    ariaLabel = 'Confirmar';
                }
                
                if (ariaLabel) {
                    boton.setAttribute('aria-label', ariaLabel);
                    console.log(`  ✅ Aria-label agregado: "${ariaLabel}" a botón con ${claseIcono}`);
                }
            }
        });
    }
    
    // ========================================================================
    // 2. MEJORAR INPUTS DE BÚSQUEDA SIN LABEL
    // ========================================================================
    
    function mejorarInputsBusqueda() {
        // Buscar inputs de búsqueda sin label asociado
        const inputsBusqueda = document.querySelectorAll('input[type="search"]:not([aria-label]), input[placeholder*="uscar"]:not([aria-label])');
        
        inputsBusqueda.forEach(input => {
            // Verificar si tiene label asociado
            const labelAsociado = document.querySelector(`label[for="${input.id}"]`);
            
            if (!labelAsociado) {
                const placeholder = input.getAttribute('placeholder') || 'Buscar';
                input.setAttribute('aria-label', placeholder);
                console.log(`  ✅ Aria-label agregado a input de búsqueda: "${placeholder}"`);
            }
        });
    }
    
    // ========================================================================
    // 3. ASEGURAR TAMAÑO MÍNIMO TOUCH (44x44px)
    // ========================================================================
    
    function asegurarTamañoTouch() {
        const botonesPequeños = document.querySelectorAll('.btn-sm, .btn-icon, .badge');
        
        botonesPequeños.forEach(boton => {
            const rect = boton.getBoundingClientRect();
            
            // Verificar si es menor a 44x44px
            if (rect.width < 44 || rect.height < 44) {
                // Agregar clase para forzar tamaño mínimo
                boton.classList.add('touch-friendly');
            }
        });
    }
    
    // ========================================================================
    // 4. MEJORAR FOCUS VISIBLE
    // ========================================================================
    
    function mejorarFocusVisible() {
        // Agregar clase al detectar navegación por teclado
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-nav');
            }
        });
        
        // Quitar clase al detectar mouse
        document.addEventListener('mousedown', function() {
            document.body.classList.remove('keyboard-nav');
        });
    }
    
    // ========================================================================
    // 5. AGREGAR ROLES Y ARIA ATTRIBUTES A TABLAS
    // ========================================================================
    
    function mejorarTablas() {
        const tablas = document.querySelectorAll('table');
        
        tablas.forEach(tabla => {
            // Verificar si tiene caption
            if (!tabla.querySelector('caption')) {
                // Buscar el heading más cercano
                const heading = tabla.closest('.card')?.querySelector('.card-header h5, .card-header h6');
                
                if (heading) {
                    const caption = document.createElement('caption');
                    caption.className = 'visually-hidden';
                    caption.textContent = heading.textContent.trim();
                    tabla.insertBefore(caption, tabla.firstChild);
                    console.log(`  ✅ Caption agregado a tabla: "${caption.textContent}"`);
                }
            }
            
            // Asegurar que headers tengan scope
            const headers = tabla.querySelectorAll('th');
            headers.forEach(th => {
                if (!th.hasAttribute('scope')) {
                    // Determinar si es row o col
                    const isRowHeader = th.parentElement?.tagName === 'TR' && th === th.parentElement.firstElementChild;
                    th.setAttribute('scope', isRowHeader ? 'row' : 'col');
                }
            });
        });
    }
    
    // ========================================================================
    // 6. VALIDAR CONTRASTE DE COLORES
    // ========================================================================
    
    function validarContraste() {
        // Esta función se ejecuta solo en desarrollo
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('  ℹ️ Validación de contraste disponible en modo desarrollo');
            console.log('  ℹ️ Usa herramientas como axe DevTools para análisis completo');
        }
    }
    
    // ========================================================================
    // 7. MEJORAR MODALES
    // ========================================================================
    
    function mejorarModales() {
        // Agregar aria-modal y role a modales de Bootstrap
        const modales = document.querySelectorAll('.modal');
        
        modales.forEach(modal => {
            if (!modal.hasAttribute('aria-modal')) {
                modal.setAttribute('aria-modal', 'true');
            }
            
            if (!modal.hasAttribute('role')) {
                modal.setAttribute('role', 'dialog');
            }
            
            // Asegurar que el botón de cerrar tenga aria-label
            const btnCerrar = modal.querySelector('.btn-close');
            if (btnCerrar && !btnCerrar.hasAttribute('aria-label')) {
                btnCerrar.setAttribute('aria-label', 'Cerrar');
            }
        });
    }
    
    // ========================================================================
    // INICIALIZACIÓN
    // ========================================================================
    
    function inicializar() {
        console.log('🚀 Inicializando mejoras de accesibilidad...');
        
        // Ejecutar al cargar la página
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', ejecutarMejoras);
        } else {
            ejecutarMejoras();
        }
        
        // Re-ejecutar cuando se cargue contenido dinámico
        // Observar cambios en el DOM
        const observer = new MutationObserver(function(mutations) {
            // Debounce para evitar múltiples ejecuciones
            clearTimeout(window.a11yTimeout);
            window.a11yTimeout = setTimeout(ejecutarMejoras, 500);
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    function ejecutarMejoras() {
        try {
            agregarAriaLabelsABotones();
            mejorarInputsBusqueda();
            asegurarTamañoTouch();
            mejorarFocusVisible();
            mejorarTablas();
            mejorarModales();
            validarContraste();
            
            console.log('✅ Mejoras de accesibilidad aplicadas correctamente');
        } catch (error) {
            console.error('❌ Error aplicando mejoras de accesibilidad:', error);
        }
    }
    
    // Iniciar
    inicializar();
    
    // Exponer función global para re-ejecutar manualmente si es necesario
    window.aplicarMejorasAccesibilidad = ejecutarMejoras;
    
})();

// ============================================================================
// ESTILOS ADICIONALES PARA ACCESIBILIDAD (inyectados vía JavaScript)
// ============================================================================

(function inyectarEstilosAccesibilidad() {
    const style = document.createElement('style');
    style.textContent = `
        /* Touch-friendly: Asegurar tamaño mínimo 44x44px */
        .touch-friendly {
            min-width: 44px !important;
            min-height: 44px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* Focus visible mejorado solo con teclado */
        body.keyboard-nav *:focus {
            outline: 3px solid #1e40af !important;
            outline-offset: 2px !important;
        }
        
        body:not(.keyboard-nav) *:focus {
            outline: none;
        }
        
        /* Skip links para navegación por teclado */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: #1e40af;
            color: white;
            padding: 8px;
            text-decoration: none;
            z-index: 100;
        }
        
        .skip-link:focus {
            top: 0;
        }
        
        /* Captions visualmente ocultos pero accesibles */
        caption.visually-hidden {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border-width: 0;
        }
    `;
    document.head.appendChild(style);
})();

console.log('♿ Script de accesibilidad cargado - Lighthouse Score Target: 90+');
