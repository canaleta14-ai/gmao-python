/**
 * solicitudes.js
 * Módulo JavaScript para gestión de solicitudes de servicio
 */

console.log("📋 solicitudes.js cargado correctamente");

// ==========================================
// FUNCIONES PARA VISUALIZACIÓN DE ARCHIVOS
// ==========================================

/**
 * Muestra una imagen en un modal
 * @param {string} url - URL de la imagen
 * @param {string} nombre - Nombre del archivo
 */
function verImagen(url, nombre) {
    const modal = document.getElementById('modalVerImagen');
    const img = document.getElementById('imagenModal');
    const titulo = document.getElementById('tituloImagenModal');
    
    if (!modal || !img || !titulo) {
        console.error('❌ No se encontraron elementos del modal de imagen');
        return;
    }
    
    img.src = url;
    titulo.textContent = nombre;
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    console.log(`🖼️ Mostrando imagen: ${nombre}`);
}

/**
 * Descarga un archivo adjunto
 * @param {number} archivoId - ID del archivo
 */
function descargarArchivo(archivoId) {
    const url = `/solicitudes/api/archivos/${archivoId}/download`;
    window.open(url, "_blank");
    console.log(`⬇️ Descargando archivo ID: ${archivoId}`);
}

// ==========================================
// FUNCIONES PARA GESTIÓN DE ARCHIVOS
// ==========================================

/**
 * Valida archivos seleccionados antes de subir
 * @param {FileList} files - Lista de archivos
 * @returns {object} Objeto con resultado de validación
 */
function validarArchivos(files) {
    const MAX_FILES = 5;
    const MAX_SIZE = 10 * 1024 * 1024; // 10 MB
    const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'];
    
    const errores = [];
    const archivosValidos = [];
    
    // Validar cantidad
    if (files.length > MAX_FILES) {
        errores.push(`Máximo ${MAX_FILES} archivos permitidos`);
        return { valido: false, errores, archivos: [] };
    }
    
    // Validar cada archivo
    Array.from(files).forEach((file, index) => {
        // Validar tamaño
        if (file.size > MAX_SIZE) {
            errores.push(`El archivo "${file.name}" excede el tamaño máximo de 10 MB`);
            return;
        }
        
        // Validar extensión
        const extension = file.name.split('.').pop().toLowerCase();
        if (!ALLOWED_EXTENSIONS.includes(extension)) {
            errores.push(`El archivo "${file.name}" tiene una extensión no permitida`);
            return;
        }
        
        // Validar tipo MIME
        if (!ALLOWED_TYPES.includes(file.type) && file.type !== '') {
            errores.push(`El archivo "${file.name}" tiene un tipo no permitido`);
            return;
        }
        
        archivosValidos.push(file);
    });
    
    return {
        valido: errores.length === 0,
        errores,
        archivos: archivosValidos
    };
}

/**
 * Muestra preview de archivos seleccionados
 * @param {FileList} files - Lista de archivos
 * @param {string} containerId - ID del contenedor para el preview
 */
function mostrarPreviewArchivos(files, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`❌ No se encontró contenedor: ${containerId}`);
        return;
    }
    
    container.innerHTML = '';
    
    Array.from(files).forEach((file, index) => {
        const col = document.createElement('div');
        col.className = 'col-6 col-md-4 col-lg-3';
        
        const esImagen = file.type.startsWith('image/');
        const icono = esImagen ? 'bi-image' : 'bi-file-earmark-text';
        const colorIcono = esImagen ? 'text-primary' : 'text-secondary';
        
        const card = document.createElement('div');
        card.className = 'card h-100 border-0 shadow-sm';
        card.innerHTML = `
            <div class="card-body p-2 text-center">
                <i class="bi ${icono} fs-1 ${colorIcono}"></i>
                <small class="text-muted text-truncate d-block mt-2" title="${file.name}">${file.name}</small>
                <small class="text-muted">${(file.size / 1024).toFixed(1)} KB</small>
            </div>
        `;
        
        col.appendChild(card);
        container.appendChild(col);
    });
    
    console.log(`📎 Preview de ${files.length} archivo(s) mostrado`);
}

// ==========================================
// FUNCIONES PARA COMUNICACIÓN
// ==========================================

/**
 * Envia email al solicitante
 * @param {string} email - Email del solicitante
 */
function enviarEmail(email) {
    // Intentar copiar al portapapeles
    navigator.clipboard.writeText(email).then(() => {
        mostrarMensaje('Email copiado al portapapeles', 'success');
        
        // Intentar abrir cliente de email
        try {
            window.location.href = `mailto:${email}`;
        } catch (error) {
            console.log('Cliente de email no disponible, pero email copiado al portapapeles');
        }
    }).catch((error) => {
        console.error('Error al copiar email:', error);
        mostrarMensaje(`Email: ${email} - Copia este email manualmente`, 'warning');
    });
}

/**
 * Llama al solicitante
 * @param {string} telefono - Teléfono del solicitante
 */
function llamar(telefono) {
    window.location.href = `tel:${telefono}`;
    console.log(`📞 Llamando a: ${telefono}`);
}

// ==========================================
// FUNCIONES PARA GESTIÓN DE ESTADO
// ==========================================

/**
 * Cambia el estado de una solicitud
 * @param {number} solicitudId - ID de la solicitud
 * @param {string} nuevoEstado - Nuevo estado
 */
async function cambiarEstadoSolicitud(solicitudId, nuevoEstado) {
    try {
        const response = await fetch(`/admin/solicitudes/${solicitudId}/estado`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ estado: nuevoEstado })
        });
        
        if (response.ok) {
            const data = await response.json();
            mostrarMensaje('Estado actualizado correctamente', 'success');
            
            // Recargar página después de 1 segundo
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            const error = await response.json();
            mostrarMensaje(error.error || 'Error al actualizar estado', 'danger');
        }
    } catch (error) {
        console.error('Error al cambiar estado:', error);
        mostrarMensaje('Error de conexión al actualizar estado', 'danger');
    }
}

// ==========================================
// FUNCIONES PARA FORMULARIOS
// ==========================================

/**
 * Valida el formulario de nueva solicitud
 * @param {Event} e - Evento del formulario
 * @returns {boolean} true si es válido
 */
function validarFormularioSolicitud(e) {
    const email = document.getElementById('email_solicitante').value;
    const telefono = document.getElementById('telefono_solicitante').value;
    
    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        e.preventDefault();
        mostrarMensaje('Por favor ingrese un email válido.', 'warning');
        return false;
    }
    
    // Validar teléfono si se proporciona
    if (telefono && !/^[\d\s\-\+\(\)]{7,20}$/.test(telefono)) {
        e.preventDefault();
        mostrarMensaje('Por favor ingrese un teléfono válido.', 'warning');
        return false;
    }
    
    return true;
}

/**
 * Configura validación automática en formulario
 */
function configurarValidacionFormulario() {
    const form = document.getElementById('solicitudForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validarFormularioSolicitud(e)) {
                return false;
            }
            
            // Mostrar indicador de carga
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Enviando...';
                submitBtn.disabled = true;
            }
        });
        
        console.log('✅ Validación de formulario configurada');
    }
}

// ==========================================
// FUNCIONES DE FILTRADO Y BÚSQUEDA
// ==========================================

/**
 * Filtra tabla de solicitudes
 */
function filtrarSolicitudes() {
    const busqueda = document.getElementById('buscar-solicitud')?.value.toLowerCase() || '';
    const estado = document.getElementById('filtro-estado')?.value || '';
    const prioridad = document.getElementById('filtro-prioridad')?.value || '';
    
    const filas = document.querySelectorAll('#tabla-solicitudes tbody tr');
    
    filas.forEach(fila => {
        const texto = fila.textContent.toLowerCase();
        const estadoFila = fila.dataset.estado || '';
        const prioridadFila = fila.dataset.prioridad || '';
        
        const coincideBusqueda = texto.includes(busqueda);
        const coincideEstado = !estado || estadoFila === estado;
        const coincidePrioridad = !prioridad || prioridadFila === prioridad;
        
        if (coincideBusqueda && coincideEstado && coincidePrioridad) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
    
    console.log('🔍 Filtros aplicados');
}

// ==========================================
// INICIALIZACIÓN
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando módulo de solicitudes...');
    
    // Configurar validación de formulario
    configurarValidacionFormulario();
    
    // Configurar preview de archivos en nueva solicitud
    const inputArchivos = document.getElementById('archivos');
    if (inputArchivos) {
        inputArchivos.addEventListener('change', function(e) {
            const files = e.target.files;
            
            // Validar archivos
            const validacion = validarArchivos(files);
            
            if (!validacion.valido) {
                // Mostrar errores
                validacion.errores.forEach(error => {
                    mostrarMensaje(error, 'warning');
                });
                e.target.value = ''; // Limpiar selección
                document.getElementById('preview-archivos').innerHTML = '';
                return;
            }
            
            // Mostrar preview
            mostrarPreviewArchivos(files, 'preview-archivos');
        });
        
        console.log('✅ Preview de archivos configurado');
    }
    
    // Configurar filtros en listado
    const buscarInput = document.getElementById('buscar-solicitud');
    if (buscarInput) {
        buscarInput.addEventListener('input', filtrarSolicitudes);
    }
    
    const filtroEstado = document.getElementById('filtro-estado');
    if (filtroEstado) {
        filtroEstado.addEventListener('change', filtrarSolicitudes);
    }
    
    const filtroPrioridad = document.getElementById('filtro-prioridad');
    if (filtroPrioridad) {
        filtroPrioridad.addEventListener('change', filtrarSolicitudes);
    }
    
    console.log('✅ Módulo de solicitudes inicializado correctamente');
});

// ==========================================
// FUNCIONES DE UTILIDAD
// ==========================================

/**
 * Muestra mensaje de alerta
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo de alerta (success, danger, warning, info)
 */
function mostrarMensaje(mensaje, tipo = 'info') {
    // Si existe la función global mostrarAlerta, usarla
    if (typeof mostrarAlerta === 'function') {
        mostrarAlerta(mensaje, tipo);
        return;
    }
    
    // Si no, usar alert básico
    console.log(`${tipo.toUpperCase()}: ${mensaje}`);
    
    // Intentar crear alerta Bootstrap
    const alertContainer = document.querySelector('.container');
    if (alertContainer) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${tipo} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        alertContainer.insertBefore(alert, alertContainer.firstChild);
        
        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
}

/**
 * Formatea bytes a tamaño legible
 * @param {number} bytes - Tamaño en bytes
 * @returns {string} Tamaño formateado
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

console.log('✅ Funciones de solicitudes disponibles');
