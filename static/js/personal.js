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
    const filtroCollapse = document.getElementById('filtrosPersonal');

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
    const form = document.getElementById('filtros-personal-form');
    if (form) {
        form.reset();
    }
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
    console.log(`Mostrando ${filasVisibles.length} empleados de ${filas.length} total`);
}