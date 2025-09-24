// personal.js - JavaScript específico para el módulo de personal

document.addEventListener('DOMContentLoaded', function () {
    console.log('Personal module loaded');

    // Verificar que Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap no está disponible');
        return;
    }

    // Encontrar elementos del colapso para mejorar UX
    const filtroHeader = document.querySelector('[data-bs-toggle="collapse"]');
    const filtroCollapse = document.getElementById('filtros-collapse');

    if (filtroHeader && filtroCollapse) {
        // Asegurar que inicie colapsado
        if (!filtroCollapse.classList.contains('show')) {
            filtroHeader.classList.add('collapsed');
            filtroHeader.setAttribute('aria-expanded', 'false');
        }

        // Mejorar la indicación visual del estado
        filtroCollapse.addEventListener('show.bs.collapse', function () {
            filtroHeader.classList.remove('collapsed');
        });

        filtroCollapse.addEventListener('hide.bs.collapse', function () {
            filtroHeader.classList.add('collapsed');
        });
    }

    // Inicializar funcionalidades adicionales
    setupFormPersonal();
    setupFiltrosPersonal();
});

// Función para limpiar filtros
function limpiarFiltrosPersonal() {
    console.log('Limpiando filtros de personal');

    // Limpiar campos individuales
    document.getElementById('nombre').value = '';
    document.getElementById('departamento').value = '';
    document.getElementById('cargo').value = '';

    // Mostrar todas las filas de la tabla
    const filas = document.querySelectorAll('#tbody-personal tr');
    filas.forEach(fila => {
        fila.style.display = '';
    });

    // Actualizar contador
    const totalFilas = filas.length;
    document.getElementById('contador-empleados').textContent = `${totalFilas} empleados`;
}

// Función para manejar el formulario de personal
function setupFormPersonal() {
    const form = document.getElementById('form-personal');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Obtener datos del formulario
            const formData = new FormData(form);
            const data = {
                nombres: document.getElementById('nombres').value,
                apellidos: document.getElementById('apellidos').value,
                cedula: document.getElementById('cedula').value,
                email: document.getElementById('email').value,
                telefono: document.getElementById('telefono').value,
                fecha_ingreso: document.getElementById('fecha_ingreso').value,
                departamento: document.getElementById('departamento_modal').value,
                cargo: document.getElementById('cargo_modal').value,
                estado: document.getElementById('estado').value,
                salario: document.getElementById('salario').value
            };

            console.log('Datos del nuevo empleado:', data);

            // Aquí iría la lógica para enviar al servidor
            // Por ahora solo mostramos un mensaje
            alert('Empleado guardado correctamente (demo)');

            // Cerrar modal y limpiar formulario
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalPersonal'));
            if (modal) {
                modal.hide();
            }
            form.reset();
        });
    }
}

// Función para manejar filtros en tiempo real
function setupFiltrosPersonal() {
    const filtroNombre = document.getElementById('nombre');
    const filtroDepartamento = document.getElementById('departamento');
    const filtroCargo = document.getElementById('cargo');

    [filtroNombre, filtroDepartamento, filtroCargo].forEach(filtro => {
        if (filtro) {
            filtro.addEventListener('input', function () {
                filtrarTablaPersonal();
            });
        }
    });
}

// Función para filtrar la tabla de personal
function filtrarTablaPersonal() {
    const nombreFiltro = document.getElementById('nombre').value.toLowerCase();
    const departamentoFiltro = document.getElementById('departamento').value.toLowerCase();
    const cargoFiltro = document.getElementById('cargo').value.toLowerCase();

    const filas = document.querySelectorAll('#tbody-personal tr');

    filas.forEach(fila => {
        const nombre = fila.cells[1].textContent.toLowerCase();
        const departamento = fila.cells[2].textContent.toLowerCase();
        const cargo = fila.cells[3].textContent.toLowerCase();

        const coincideNombre = !nombreFiltro || nombre.includes(nombreFiltro);
        const coincideDepartamento = !departamentoFiltro || departamento.includes(departamentoFiltro);
        const coincideCargo = !cargoFiltro || cargo.includes(cargoFiltro);

        if (coincideNombre && coincideDepartamento && coincideCargo) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });

    // Actualizar contador de resultados
    const filasVisibles = document.querySelectorAll('#tbody-personal tr:not([style*="display: none"])');
    document.getElementById('contador-empleados').textContent = `${filasVisibles.length} empleados`;
    console.log(`Mostrando ${filasVisibles.length} empleados de ${filas.length} total`);
}

// Función para exportar CSV
function exportarCSVPersonal() {
    console.log('Exportando datos de personal a CSV...');

    // Obtener datos de la tabla
    const tabla = document.getElementById('tabla-personal');
    const filas = tabla.querySelectorAll('tbody tr:not([style*="display: none"])');

    if (filas.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    // Preparar datos CSV
    let csvContent = 'ID,Nombre,Departamento,Cargo,Email,Telefono,Estado\n';

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        const id = celdas[0].textContent.trim();
        const nombre = celdas[1].querySelector('.fw-bold').textContent.trim();
        const departamento = celdas[2].querySelector('.badge').textContent.trim();
        const cargo = celdas[3].textContent.trim();

        // Extraer email y teléfono del contenido HTML
        const contactoDiv = celdas[4];
        const email = contactoDiv.querySelector('div:first-child').textContent.replace('📧', '').trim();
        const telefono = contactoDiv.querySelector('div:last-child').textContent.replace('📞', '').trim();

        const estado = celdas[5].querySelector('.badge').textContent.trim();

        csvContent += `"${id}","${nombre}","${departamento}","${cargo}","${email}","${telefono}","${estado}"\n`;
    });

    // Descargar archivo
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `personal_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}