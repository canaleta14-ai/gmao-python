// Variables y funciones específicas de Planes
let planesData = [];
let paginacionPlanes;

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    console.log('🔧 Módulo de mantenimiento preventivo cargado');

    // Configurar paginación
    paginacionPlanes = new Pagination('paginacion-planes', cargarPlanes, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true,
        pageSizes: [10, 25, 50, 100]
    });

    // Configurar búsqueda y filtros
    configurarFiltrosPreventivo();

    // Configurar autocompletado
    setTimeout(() => {
        inicializarAutocompletadoPreventivo();
    }, 500);

    // Cargar datos iniciales
    cargarPlanes(1);
});

// Configurar filtros de mantenimiento preventivo
function configurarFiltrosPreventivo() {
    console.log('🔍 Configurando filtros de mantenimiento preventivo...');

    // Campo de búsqueda
    const campoBuscar = document.getElementById('search-planes');
    if (campoBuscar) {
        let timeoutBusqueda;
        campoBuscar.addEventListener('input', function () {
            clearTimeout(timeoutBusqueda);
            timeoutBusqueda = setTimeout(() => {
                console.log('🔍 Búsqueda en planes:', this.value);
                aplicarFiltrosPreventivo();
            }, 300);
        });
        console.log('✅ Campo de búsqueda configurado');
    }

    // Selectores de filtro
    const filtros = ['filtro-estado', 'filtro-frecuencia', 'filtro-vencimiento'];
    filtros.forEach(filtroId => {
        const elemento = document.getElementById(filtroId);
        if (elemento) {
            elemento.addEventListener('change', aplicarFiltrosPreventivo);
            console.log(`✅ Filtro ${filtroId} configurado`);
        }
    });
}

// Aplicar filtros a la lista de planes
function aplicarFiltrosPreventivo() {
    console.log('🔍 Aplicando filtros de preventivo...');
    cargarPlanes(1); // Recargar con filtros aplicados
}

// Inicializar autocompletado
function inicializarAutocompletadoPreventivo() {
    console.log('🔍 Inicializando autocompletado en preventivo...');

    if (!window.AutoComplete) {
        console.log('❌ AutoComplete no disponible');
        return;
    }

    const campoBuscar = document.getElementById('search-planes');
    if (campoBuscar) {
        new AutoComplete({
            element: campoBuscar,
            apiUrl: '/planes/api',
            searchKey: 'q',
            displayKey: item => `${item.codigo} - ${item.nombre} (${item.equipo})`,
            valueKey: 'codigo',
            placeholder: 'Buscar por código, nombre o equipo...',
            allowFreeText: true,
            customFilter: (item, query) => {
                const q = query.toLowerCase();
                return item.codigo.toLowerCase().includes(q) ||
                    item.nombre.toLowerCase().includes(q) ||
                    (item.equipo && item.equipo.toLowerCase().includes(q));
            },
            onSelect: (item) => {
                console.log('🔧 Plan seleccionado:', item);
                aplicarFiltrosPreventivo();
            }
        });
        console.log('✅ Autocompletado de preventivo configurado');
    }
}

// Función para limpiar filtros de preventivo
function limpiarFiltrosPreventivo() {
    console.log('🧹 Limpiando filtros de preventivo...');

    // Limpiar campos de filtro
    const filtros = [
        'search-planes',
        'filtro-estado',
        'filtro-frecuencia',
        'filtro-vencimiento'
    ];

    filtros.forEach(filtroId => {
        const elemento = document.getElementById(filtroId);
        if (elemento) {
            elemento.value = '';
            console.log(`✅ Filtro ${filtroId} limpiado`);
        }
    });

    // Aplicar filtros (mostrará todos los planes sin filtros)
    aplicarFiltrosPreventivo();
    console.log('✅ Filtros limpiados y vista actualizada');
}

function cargarPlanes(page = 1, per_page = null) {
    if (per_page) {
        paginacionPlanes.setPerPage(per_page);
    }

    const params = new URLSearchParams({
        page: page,
        per_page: paginacionPlanes.perPage
    });

    // Agregar filtros de búsqueda si existen
    const searchInput = document.getElementById('search-planes');
    if (searchInput && searchInput.value.trim()) {
        params.append('q', searchInput.value.trim());
    }

    // Agregar filtros adicionales
    const filtroEstado = document.getElementById('filtro-estado');
    if (filtroEstado && filtroEstado.value) {
        params.append('estado', filtroEstado.value);
    }

    const filtroFrecuencia = document.getElementById('filtro-frecuencia');
    if (filtroFrecuencia && filtroFrecuencia.value) {
        params.append('frecuencia', filtroFrecuencia.value);
    }

    const filtroVencimiento = document.getElementById('filtro-vencimiento');
    if (filtroVencimiento && filtroVencimiento.value) {
        params.append('vencimiento', filtroVencimiento.value);
    }

    fetch(`/planes/api?${params}`)
        .then(response => response.json())
        .then(data => {
            planesData = data.items || data;
            renderPlanes(data.items || data);

            // Renderizar paginación si hay datos paginados
            if (data.page && data.per_page && data.total) {
                paginacionPlanes.render(data.page, data.per_page, data.total);
            }
        })
        .catch(error => {
            console.error('Error cargando planes:', error);
            showNotificationToast('Error al cargar planes de mantenimiento', 'error');
        });
}

// Función legacy para compatibilidad
function loadPlanes() {
    cargarPlanes(1);
}
function renderPlanes(planes) {
    const tbody = document.getElementById('planesTableBody');
    if (!tbody) {
        console.error('Table body not found');
        return;
    }

    tbody.innerHTML = '';

    if (!planes || planes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="bi bi-calendar-check fs-1 d-block mb-2"></i>
                    No se encontraron planes de mantenimiento
                </td>
            </tr>
        `;
        return;
    }

    planes.forEach(plan => {
        tbody.innerHTML += `
            <tr>
                <td>${plan.codigo}</td>
                <td>${plan.nombre}</td>
                <td>${plan.equipo}</td>
                <td>${plan.frecuencia}</td>
                <td>${plan.ultima_ejecucion || 'N/A'}</td>
                <td>${plan.proxima_ejecucion || 'N/A'}</td>
                <td>${getEstadoPlanBadge(plan.estado)}</td>
                <td>
                    <button class="btn btn-sm btn-info" title="Ver detalles" onclick="viewPlan(${plan.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" title="Editar" onclick="editPlan(${plan.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" title="Eliminar" onclick="deletePlan(${plan.id}, '${plan.codigo}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
}
function guardarPlan() {
    const form = document.getElementById('formPlan');
    const editingId = form.dataset.editingId;
    const isEditing = !!editingId;

    // Recopilar datos básicos del formulario
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // Agregar datos específicos de frecuencia
    const tipoFrecuencia = document.getElementById('tipo_frecuencia').value;
    data.tipo_frecuencia = tipoFrecuencia;

    // Mapear tipo_frecuencia a frecuencia para el backend
    const mapeoFrecuencia = {
        'diario': 'Diario',
        'semanal': 'Semanal',
        'mensual': 'Mensual',
        'personalizado': 'Personalizado'
    };
    data.frecuencia = mapeoFrecuencia[tipoFrecuencia] || 'Personalizado';

    // Datos específicos según el tipo de frecuencia
    if (tipoFrecuencia === 'diaria') {
        data.intervalo_dias = document.getElementById('intervalo_dias').value;
    } else if (tipoFrecuencia === 'semanal') {
        data.intervalo_semanas = document.getElementById('intervalo_semanas').value;

        // Recopilar días de la semana seleccionados
        const diasSeleccionados = [];
        document.querySelectorAll('input[name="dias_semana"]:checked').forEach(cb => {
            diasSeleccionados.push(cb.value);
        });
        data.dias_semana = diasSeleccionados;
    } else if (tipoFrecuencia === 'mensual') {
        data.intervalo_meses = document.getElementById('intervalo_meses').value;
        data.tipo_mensual = document.getElementById('tipo_mensual').value;

        if (data.tipo_mensual === 'dia_mes') {
            data.dia_mes = document.getElementById('dia_mes').value;
        } else if (data.tipo_mensual === 'dia_semana_mes') {
            data.semana_mes = document.getElementById('semana_mes').value;
            data.dia_semana_mes = document.getElementById('dia_semana_mes').value;
        }
    } else if (tipoFrecuencia === 'personalizada') {
        data.patron_personalizado = document.getElementById('patron_personalizado').value;
        data.fechas_especificas = document.getElementById('fechas_especificas').value;
    }

    // Calcular próximas fechas para enviar al backend
    try {
        const proximasFechas = calcularProximasFechas();
        data.proximas_fechas = proximasFechas.slice(0, 10).map(fecha =>
            fecha.toISOString().split('T')[0]
        );
    } catch (error) {
        console.error('Error al calcular fechas:', error);
        data.proximas_fechas = [];
    }

    // Validar datos antes de enviar
    if (!data.nombre || !data.activo_id) {
        showNotificationToast('Por favor complete todos los campos obligatorios (nombre y activo)', 'warning');
        return;
    }

    // Convertir activo_id a entero
    if (data.activo_id) {
        data.activo_id = parseInt(data.activo_id);
    }

    // Convertir tiempo_estimado a float si existe
    if (data.tiempo_estimado) {
        data.tiempo_estimado = parseFloat(data.tiempo_estimado);
    }

    // El código se genera automáticamente si no se proporciona
    if (!data.codigo || data.codigo.trim() === '') {
        // El backend generará el código automáticamente
        delete data.codigo;
    }

    if (!tipoFrecuencia) {
        showNotificationToast('Por favor seleccione un tipo de frecuencia', 'warning');
        return;
    }

    // Validaciones específicas por tipo de frecuencia
    if (tipoFrecuencia === 'semanal' && data.dias_semana.length === 0) {
        showNotificationToast('Por favor seleccione al menos un día de la semana', 'warning');
        return;
    }

    console.log('Datos a enviar:', data); // Debug
    console.log('Modo:', isEditing ? 'Edición' : 'Creación', isEditing ? `(ID: ${editingId})` : ''); // Debug

    // Configurar URL y método según el modo
    const url = isEditing ? `/planes/api/${editingId}` : '/planes/api';
    const method = isEditing ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                // Si es error del servidor, intentar leer el mensaje de error
                return response.json().catch(() => {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }).then(errorData => {
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(result => {
            console.log('Resultado:', result);
            if (result.success) {
                const mensaje = isEditing ?
                    'Plan de mantenimiento editado exitosamente' :
                    'Plan de mantenimiento creado exitosamente';
                showNotificationToast(mensaje, 'success');
                bootstrap.Modal.getInstance(document.getElementById('planModal')).hide();
                cargarPlanes(1); // Recargar datos con paginación
            } else {
                showNotificationToast(result.message || result.error || 'Error al guardar el plan', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotificationToast('Error al comunicarse con el servidor', 'error');
        });
}

// Función de búsqueda con debounce (LEGACY - reemplazada por configurarFiltrosPreventivo)
// function setupPlanesSearch() {
//     const searchInput = document.getElementById('search-planes');
//     if (!searchInput) return;

//     let debounceTimer;
//     searchInput.addEventListener('input', function () {
//         clearTimeout(debounceTimer);
//         debounceTimer = setTimeout(() => {
//             cargarPlanes(1);
//         }, 300);
//     });
// }

// Función para cargar activos en el select
function cargarActivos() {
    const selectActivo = document.getElementById('activo_id');
    if (!selectActivo) {
        console.log('Select activo_id no encontrado');
        return;
    }

    console.log('Cargando activos...');
    fetch('/ordenes/activos')
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(activos => {
            console.log('Activos recibidos:', activos);

            // Limpiar opciones existentes excepto la primera
            selectActivo.innerHTML = '<option value="">Seleccionar activo...</option>';

            // Agregar opciones de activos
            if (Array.isArray(activos) && activos.length > 0) {
                activos.forEach(activo => {
                    const option = document.createElement('option');
                    option.value = activo.id;
                    option.textContent = activo.display || `${activo.codigo} - ${activo.nombre}`;
                    selectActivo.appendChild(option);
                });
                console.log(`Se cargaron ${activos.length} activos`);
            } else {
                console.log('No se encontraron activos o el formato es incorrecto');
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "No hay activos disponibles";
                option.disabled = true;
                selectActivo.appendChild(option);
            }
        })
        .catch(error => {
            console.error('Error cargando activos:', error);
            showNotificationToast('Error al cargar la lista de activos', 'error');

            // Agregar opción de error
            selectActivo.innerHTML = '<option value="">Error al cargar activos</option>';
        });
}// Función toast para notificaciones
function mostrarToast(mensaje, tipo = 'info') {
    showNotificationToast(mensaje, tipo);
}
// Utilidad para mostrar badge de estado
function getEstadoPlanBadge(estado) {
    if (estado === 'Activo') return '<span class="badge bg-success">Activo</span>';
    if (estado === 'Vencido') return '<span class="badge bg-danger">Vencido</span>';
    if (estado === 'Próximo') return '<span class="badge bg-warning">Próximo</span>';
    return '<span class="badge bg-secondary">Desconocido</span>';
}

function getPrioridadBadge(prioridad) {
    if (prioridad === 'Alta') return '<span class="badge bg-danger">Alta</span>';
    if (prioridad === 'Media') return '<span class="badge bg-warning">Media</span>';
    if (prioridad === 'Baja') return '<span class="badge bg-success">Baja</span>';
    return '<span class="badge bg-secondary">Desconocida</span>';
}

function formatearFecha(fechaStr) {
    if (!fechaStr) return 'N/A';
    try {
        const fecha = new Date(fechaStr);
        return fecha.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return fechaStr;
    }
}
// Funciones para manejo de frecuencias de mantenimiento preventivo
function cambiarTipoFrecuencia() {
    const tipoElement = document.getElementById('tipo_frecuencia');
    if (!tipoElement) return;

    const tipo = tipoElement.value;

    // Ocultar todas las secciones de configuración
    const secciones = ['config-diaria', 'config-semanal', 'config-mensual', 'config-personalizada'];
    secciones.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) elemento.style.display = 'none';
    });

    // Mostrar la sección correspondiente
    const seccionActiva = document.getElementById(`config-${tipo === 'personalizada' ? 'personalizada' : tipo === 'diaria' ? 'diaria' : tipo === 'semanal' ? 'semanal' : tipo === 'mensual' ? 'mensual' : ''}`);
    if (seccionActiva) {
        seccionActiva.style.display = 'block';
    }

    // Actualizar vista previa
    previsualizarFechas();
}

function cambiarTipoMensual() {
    const tipo = document.getElementById('tipo_mensual');
    if (!tipo) return; // Salir si el elemento no existe

    const tipoValue = tipo.value;

    // Ocultar todas las opciones mensuales
    const diaEspecificoMes = document.getElementById('dia-especifico-mes');
    const diaSemanaMs = document.getElementById('dia-semana-mes');

    if (diaEspecificoMes) diaEspecificoMes.style.display = 'none';
    if (diaSemanaMs) diaSemanaMs.style.display = 'none';

    // Mostrar la opción correspondiente
    if (tipoValue === 'dia_mes' && diaEspecificoMes) {
        diaEspecificoMes.style.display = 'block';
    } else if (tipoValue === 'dia_semana_mes' && diaSemanaMs) {
        diaSemanaMs.style.display = 'block';
    }

    // Actualizar vista previa
    previsualizarFechas();
}

function previsualizarFechas() {
    const previewContainer = document.getElementById('preview-fechas');
    const tipoElement = document.getElementById('tipo_frecuencia');

    if (!previewContainer) return;

    if (!tipoElement || !tipoElement.value) {
        previewContainer.innerHTML = '<p class="text-muted">Seleccione un tipo de frecuencia para ver la vista previa.</p>';
        return;
    }

    try {
        const fechas = calcularProximasFechas();

        if (fechas.length === 0) {
            previewContainer.innerHTML = '<p class="text-warning">No se pueden calcular fechas con la configuración actual.</p>';
            return;
        }

        let html = '<ul class="list-unstyled">';
        fechas.slice(0, 5).forEach((fecha, index) => {
            const fechaFormateada = fecha.toLocaleDateString('es-ES', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            html += `<li><i class="fas fa-calendar me-2"></i>${fechaFormateada}</li>`;
        });
        html += '</ul>';

        if (fechas.length > 5) {
            html += `<small class="text-muted">Y ${fechas.length - 5} fechas más...</small>`;
        }

        previewContainer.innerHTML = html;
    } catch (error) {
        console.error('Error al calcular fechas:', error);
        previewContainer.innerHTML = '<p class="text-danger">Error al calcular las fechas. Verifique la configuración.</p>';
    }
}

function calcularProximasFechas() {
    const tipoElement = document.getElementById('tipo_frecuencia');
    if (!tipoElement) return [];

    const tipo = tipoElement.value;

    // Usar fecha actual si no hay campo fecha_inicio
    const fechaInicioElement = document.getElementById('fecha_inicio');
    const fechaInicio = fechaInicioElement ?
        new Date(fechaInicioElement.value || new Date()) :
        new Date();

    const fechas = [];

    switch (tipo) {
        case 'diario':
            return calcularFechasDiarias(fechaInicio);
        case 'semanal':
            return calcularFechasSemanaless(fechaInicio);
        case 'mensual':
            return calcularFechasMensuales(fechaInicio);
        case 'personalizado':
            return calcularFechasPersonalizadas(fechaInicio);
        default:
            return [];
    }
}

function calcularFechasDiarias(fechaInicio) {
    const intervaloElement = document.getElementById('intervalo_dias');
    const intervalo = intervaloElement ? parseInt(intervaloElement.value) || 1 : 1;
    const fechas = [];
    let fecha = new Date(fechaInicio);

    for (let i = 0; i < 10; i++) {
        fechas.push(new Date(fecha));
        fecha.setDate(fecha.getDate() + intervalo);
    }

    return fechas;
}

function calcularFechasSemanaless(fechaInicio) {
    const intervaloElement = document.getElementById('intervalo_semanas');
    const intervalo = intervaloElement ? parseInt(intervaloElement.value) || 1 : 1;
    const diasSeleccionados = [];

    // Recopilar días seleccionados (0 = domingo, 1 = lunes, etc.)
    const checkboxes = document.querySelectorAll('input[name="dias_semana"]:checked');
    checkboxes.forEach(cb => {
        diasSeleccionados.push(parseInt(cb.value));
    });

    if (diasSeleccionados.length === 0) return [];

    const fechas = [];
    let fecha = new Date(fechaInicio);
    let semanaActual = 0;

    for (let i = 0; i < 50; i++) { // Generar hasta 50 fechas
        const diaSemana = fecha.getDay();

        if (diasSeleccionados.includes(diaSemana) && semanaActual % intervalo === 0) {
            fechas.push(new Date(fecha));
        }

        fecha.setDate(fecha.getDate() + 1);

        // Si es domingo, incrementar contador de semana
        if (fecha.getDay() === 0) {
            semanaActual++;
        }

        if (fechas.length >= 10) break;
    }

    return fechas;
}

function calcularFechasMensuales(fechaInicio) {
    const tipoMensualElement = document.getElementById('tipo_mensual');
    const intervalMesesElement = document.getElementById('intervalo_meses');

    if (!tipoMensualElement) return [];

    const tipoMensual = tipoMensualElement.value;
    const intervalMeses = intervalMesesElement ? parseInt(intervalMesesElement.value) || 1 : 1;
    const fechas = [];

    if (tipoMensual === 'dia_mes') {
        const diaMesElement = document.getElementById('dia_mes');
        const diaMes = diaMesElement ? parseInt(diaMesElement.value) || 1 : 1;
        let fecha = new Date(fechaInicio.getFullYear(), fechaInicio.getMonth(), diaMes);

        for (let i = 0; i < 12; i++) {
            if (fecha >= fechaInicio) {
                fechas.push(new Date(fecha));
            }
            fecha.setMonth(fecha.getMonth() + intervalMeses);
        }
    } else if (tipoMensual === 'dia_semana_mes') {
        const semanaMesElement = document.getElementById('semana_mes');
        const diaSemanaElement = document.getElementById('dia_semana_mes');

        const semanaDelMes = semanaMesElement ? parseInt(semanaMesElement.value) || 1 : 1;
        const diaSemana = diaSemanaElement ? parseInt(diaSemanaElement.value) || 1 : 1;

        let fecha = new Date(fechaInicio);
        fecha.setDate(1); // Primer día del mes

        for (let i = 0; i < 12; i++) {
            const fechaCalculada = calcularDiaSemanaDelMes(fecha.getFullYear(), fecha.getMonth(), semanaDelMes, diaSemana);
            if (fechaCalculada && fechaCalculada >= fechaInicio) {
                fechas.push(fechaCalculada);
            }
            fecha.setMonth(fecha.getMonth() + intervalMeses);
        }
    }

    return fechas;
}

function calcularDiaSemanaDelMes(año, mes, semana, diaSemana) {
    // semana: 1-4 (primera, segunda, tercera, cuarta semana)
    // diaSemana: 0-6 (domingo=0, lunes=1, etc.)

    const primerDia = new Date(año, mes, 1);
    const primerDiaSemana = primerDia.getDay();

    // Calcular el primer día de la semana especificada en el mes
    let diasHastaPrimerOcurrencia = (diaSemana - primerDiaSemana + 7) % 7;
    if (diasHastaPrimerOcurrencia === 0 && primerDiaSemana !== diaSemana) {
        diasHastaPrimerOcurrencia = 7;
    }

    const diaObjetivo = 1 + diasHastaPrimerOcurrencia + (semana - 1) * 7;

    // Verificar que el día existe en el mes
    const ultimoDiaDelMes = new Date(año, mes + 1, 0).getDate();
    if (diaObjetivo > ultimoDiaDelMes) {
        return null; // El día no existe en este mes
    }

    return new Date(año, mes, diaObjetivo);
}

function calcularFechasPersonalizadas(fechaInicio) {
    const fechasEspecificasElement = document.getElementById('fechas_especificas');
    const fechas = [];

    if (fechasEspecificasElement && fechasEspecificasElement.value) {
        const lineas = fechasEspecificasElement.value.split('\n');
        lineas.forEach(linea => {
            linea = linea.trim();
            if (linea) {
                try {
                    const fecha = new Date(linea);
                    if (!isNaN(fecha.getTime()) && fecha >= fechaInicio) {
                        fechas.push(fecha);
                    }
                } catch (error) {
                    console.warn('Fecha inválida:', linea);
                }
            }
        });
    }

    // Ordenar fechas
    fechas.sort((a, b) => a - b);

    return fechas;
}

// Función para resetear el formulario de mantenimiento preventivo
function resetearFormularioPreventivo() {
    document.getElementById('formPlan').reset();

    // Ocultar todas las secciones de configuración
    document.getElementById('config-diaria').style.display = 'none';
    document.getElementById('config-semanal').style.display = 'none';
    document.getElementById('config-mensual').style.display = 'none';
    document.getElementById('config-personalizada').style.display = 'none';

    // Limpiar vista previa
    document.getElementById('preview-fechas').innerHTML = '<p class="text-muted">Seleccione un tipo de frecuencia para ver la vista previa.</p>';
}

// Función para abrir el modal con reseteo
function openPlanModal() {
    // Limpiar formulario y remover datos de edición
    resetearFormularioPreventivo();
    delete document.getElementById('formPlan').dataset.editingId;

    // Configurar modal para creación
    document.getElementById('modalTitle').textContent = 'Nuevo Plan de Mantenimiento';

    new bootstrap.Modal(document.getElementById('planModal')).show();
}

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    // Configurar paginación
    paginacionPlanes = new Pagination('paginacion-planes', cargarPlanes, {
        perPage: 10,
        showInfo: true,
        showSizeSelector: true,
        pageSizes: [10, 25, 50, 100]
    });

    // Cargar datos iniciales
    cargarPlanes(1);
    cargarActivos(); // Cargar activos para el select

    // Configurar búsqueda
    setupPlanesSearch();

    // Agregar event listeners para las funciones de frecuencia
    const tipoFrecuenciaSelect = document.getElementById('tipo_frecuencia');
    if (tipoFrecuenciaSelect) {
        tipoFrecuenciaSelect.addEventListener('change', cambiarTipoFrecuencia);
    }

    const tipoMensualSelect = document.getElementById('tipo_mensual');
    if (tipoMensualSelect) {
        tipoMensualSelect.addEventListener('change', cambiarTipoMensual);
    }

    // Event listeners para actualizar vista previa cuando cambien los valores
    const inputsParaPreview = [
        'fecha_inicio', 'intervalo_dias', 'intervalo_semanas', 'intervalo_meses',
        'dia_mes', 'semana_mes', 'dia_semana_mes', 'fechas_especificas'
    ];

    inputsParaPreview.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', previsualizarFechas);
            element.addEventListener('input', previsualizarFechas);
        }
    });

    // Event listener para checkboxes de días de la semana
    document.addEventListener('change', function (e) {
        if (e.target.name === 'dias_semana') {
            previsualizarFechas();
        }
    });
});

// Funciones para manejar acciones de planes
function viewPlan(planId) {
    console.log('Ver detalles del plan:', planId);

    // Obtener datos completos del plan desde el servidor
    fetch(`/planes/api/${planId}`)
        .then(response => response.json())
        .then(result => {
            if (result.success && result.plan) {
                const plan = result.plan;

                // Crear modal de detalles dinámico
                const modalHtml = `
                    <div class="modal fade" id="viewPlanModal" tabindex="-1" aria-labelledby="viewPlanModalLabel" aria-hidden="true">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content">
                                <div class="modal-header bg-info text-white">
                                    <h5 class="modal-title" id="viewPlanModalLabel">
                                        <i class="bi bi-eye me-2"></i>Detalles del Plan de Mantenimiento
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="card h-100">
                                                <div class="card-header bg-light">
                                                    <h6 class="mb-0"><i class="bi bi-info-circle me-1"></i>Información General</h6>
                                                </div>
                                                <div class="card-body">
                                                    <table class="table table-sm table-borderless">
                                                        <tr>
                                                            <td><strong>Código:</strong></td>
                                                            <td>${plan.codigo_plan}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Nombre:</strong></td>
                                                            <td>${plan.nombre}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Descripción:</strong></td>
                                                            <td>${plan.descripcion || 'N/A'}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Estado:</strong></td>
                                                            <td>${getEstadoPlanBadge(plan.estado)}</td>
                                                        </tr>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="card h-100">
                                                <div class="card-header bg-light">
                                                    <h6 class="mb-0"><i class="bi bi-gear me-1"></i>Detalles Técnicos</h6>
                                                </div>
                                                <div class="card-body">
                                                    <table class="table table-sm table-borderless">
                                                        <tr>
                                                            <td><strong>Activo/Equipo:</strong></td>
                                                            <td>${plan.activo_nombre || 'N/A'}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Tiempo Estimado:</strong></td>
                                                            <td>${plan.tiempo_estimado ? plan.tiempo_estimado + ' horas' : 'N/A'}</td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Frecuencia:</strong></td>
                                                            <td><span class="badge bg-primary">${plan.frecuencia}</span></td>
                                                        </tr>
                                                        <tr>
                                                            <td><strong>Días de Frecuencia:</strong></td>
                                                            <td>${plan.frecuencia_dias ? plan.frecuencia_dias + ' días' : 'N/A'}</td>
                                                        </tr>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row mt-3">
                                        <div class="col-12">
                                            <div class="card">
                                                <div class="card-header bg-light">
                                                    <h6 class="mb-0"><i class="bi bi-calendar me-1"></i>Programación</h6>
                                                </div>
                                                <div class="card-body">
                                                    <div class="row">
                                                        <div class="col-md-6">
                                                            <strong>Última Ejecución:</strong><br>
                                                            <span class="text-muted">${plan.ultima_ejecucion ? formatearFecha(plan.ultima_ejecucion) : 'Nunca ejecutado'}</span>
                                                        </div>
                                                        <div class="col-md-6">
                                                            <strong>Próxima Ejecución:</strong><br>
                                                            <span class="text-muted">${plan.proxima_ejecucion ? formatearFecha(plan.proxima_ejecucion) : 'No programado'}</span>
                                                        </div>
                                                    </div>
                                                    ${plan.instrucciones ? `
                                                    <div class="mt-3">
                                                        <strong>Instrucciones:</strong><br>
                                                        <div class="border rounded p-2 bg-light">
                                                            ${plan.instrucciones}
                                                        </div>
                                                    </div>
                                                    ` : ''}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-warning" onclick="editPlan(${plan.id}); bootstrap.Modal.getInstance(document.getElementById('viewPlanModal')).hide();">
                                        <i class="bi bi-pencil me-1"></i>Editar Plan
                                    </button>
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // Agregar modal al DOM
                document.body.insertAdjacentHTML('beforeend', modalHtml);

                const modal = new bootstrap.Modal(document.getElementById('viewPlanModal'));

                // Limpiar modal del DOM cuando se cierre
                document.getElementById('viewPlanModal').addEventListener('hidden.bs.modal', function () {
                    this.remove();
                });

                // Mostrar modal
                modal.show();

            } else {
                showNotificationToast('Error al cargar los detalles del plan: ' + (result.error || 'Error desconocido'), 'error');
            }
        })
        .catch(error => {
            console.error('Error al obtener detalles del plan:', error);
            showNotificationToast('Error al cargar los detalles del plan', 'error');
        });
}

function editPlan(planId) {
    console.log('Editar plan:', planId);

    // Obtener detalles completos del plan desde el servidor
    fetch(`/planes/api/${planId}`)
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                const plan = result.plan;
                console.log('Datos del plan a editar:', plan);

                // Llenar el formulario con los datos del plan
                try {
                    document.getElementById('codigo_plan').value = plan.codigo_plan || '';
                    document.getElementById('nombre').value = plan.nombre || '';
                    document.getElementById('descripcion').value = plan.descripcion || '';
                    document.getElementById('instrucciones').value = plan.instrucciones || '';
                    document.getElementById('tiempo_estimado').value = plan.tiempo_estimado || '';
                } catch (error) {
                    console.error('Error al llenar campos básicos:', error);
                }

                // Seleccionar el activo correcto
                if (plan.activo_id) {
                    try {
                        const selectActivo = document.getElementById('activo_id');
                        if (selectActivo) {
                            selectActivo.value = plan.activo_id;
                        }
                    } catch (error) {
                        console.error('Error al seleccionar activo:', error);
                    }
                }

                // Configurar frecuencia básica
                if (plan.frecuencia) {
                    try {
                        const mapeoFrecuencia = {
                            'Diario': 'diario',
                            'Semanal': 'semanal',
                            'Mensual': 'mensual',
                            'Personalizado': 'personalizado'
                        };
                        const tipoFrecuencia = mapeoFrecuencia[plan.frecuencia] || 'personalizado';
                        const tipoFrecuenciaElement = document.getElementById('tipo_frecuencia');
                        if (tipoFrecuenciaElement) {
                            tipoFrecuenciaElement.value = tipoFrecuencia;
                            cambiarTipoFrecuencia(); // Mostrar la configuración correspondiente
                        }
                    } catch (error) {
                        console.error('Error al configurar frecuencia:', error);
                    }
                }

                // Configurar modal en modo edición
                document.getElementById('modalTitle').innerHTML = '<i class="bi bi-pencil me-2"></i>Editar Plan de Mantenimiento';
                document.getElementById('formPlan').dataset.editingId = planId;

                // Abrir el modal
                new bootstrap.Modal(document.getElementById('planModal')).show();

            } else {
                showNotificationToast('Error al cargar los datos del plan: ' + (result.error || 'Error desconocido'), 'error');
            }
        })
        .catch(error => {
            console.error('Error al obtener datos del plan:', error);
            showNotificationToast('Error al cargar los datos del plan', 'error');
        });
}

function deletePlan(planId, planCodigo) {
    console.log('Eliminar plan:', planId);

    // Crear modal de confirmación dinámico
    const modalHtml = `
        <div class="modal fade" id="confirmDeleteModal" tabindex="-1" aria-labelledby="confirmDeleteModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title" id="confirmDeleteModalLabel">
                            <i class="bi bi-exclamation-triangle me-2"></i>Confirmar Eliminación
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>¿Está seguro de que desea eliminar el plan de mantenimiento?</p>
                        <div class="alert alert-warning">
                            <strong>Código del Plan:</strong> ${planCodigo}<br>
                            <strong>Advertencia:</strong> Esta acción no se puede deshacer.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
                            <i class="bi bi-trash me-1"></i>Eliminar Plan
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));

    // Manejar confirmación
    document.getElementById('confirmDeleteBtn').addEventListener('click', async function () {
        try {
            console.log('Enviando solicitud DELETE para plan ID:', planId);

            const response = await fetch(`/planes/api/${planId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();
            console.log('Respuesta de eliminación:', result);

            if (response.ok && result.success) {
                showNotificationToast('Plan de mantenimiento eliminado exitosamente', 'success');
                modal.hide();
                cargarPlanes(); // Recargar la tabla
            } else {
                showNotificationToast('Error al eliminar el plan: ' + (result.error || 'Error desconocido'), 'error');
            }
        } catch (error) {
            console.error('Error al eliminar plan:', error);
            showNotificationToast('Error al eliminar el plan', 'error');
        }
    });

    // Limpiar modal del DOM cuando se cierre
    document.getElementById('confirmDeleteModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });

    // Mostrar modal
    modal.show();
}
