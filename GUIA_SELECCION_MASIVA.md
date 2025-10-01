# Guía de Implementación: Sistema de Selección Masiva

## 📋 Descripción General

Este documento explica cómo implementar checkboxes de selección múltiple y acciones masivas en las listas del sistema GMAO.

## 🎯 Funcionalidades

- ✅ Checkbox "Seleccionar todo" en el encabezado de la tabla
- ✅ Checkboxes individuales por cada fila
- ✅ Contador de elementos seleccionados
- ✅ Barra de acciones masivas (activar, desactivar, exportar, eliminar)
- ✅ Estado intermedio del checkbox principal
- ✅ Animaciones suaves
- ✅ Responsive y accesible

---

## 📦 Archivos Requeridos

### 1. JavaScript: `static/js/seleccion-masiva.js`
Módulo reutilizable con toda la lógica de selección.

### 2. CSS: `static/css/seleccion-masiva.css`
Estilos para checkboxes y acciones masivas.

---

## 🚀 Implementación Paso a Paso

### Paso 1: Incluir Archivos en el Template

En el bloque `extra_head` de tu template HTML:

```html
{% block extra_head %}
<!-- CSS existente -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/tu-modulo.css') }}">

<!-- Agregar CSS de selección masiva -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/seleccion-masiva.css') }}">
{% endblock %}
```

Al final del archivo, antes del `{% endblock %}` principal:

```html
<!-- Script de selección masiva -->
<script src="{{ url_for('static', filename='js/seleccion-masiva.js') }}"></script>

<!-- Script del módulo (debe ir después) -->
<script src="{{ url_for('static', filename='js/tu-modulo.js') }}"></script>
{% endblock %}
```

---

### Paso 2: Modificar el Encabezado de la Tabla

Agregar checkbox en el `<thead>` y la barra de acciones masivas:

```html
<div class="card-header">
    <div class="d-flex justify-content-between align-items-center">
        <h6 class="mb-0">
            <i class="bi bi-table me-2"></i>Listado de [Entidad]
            <span class="badge bg-secondary ms-2" id="contador-items">0 elementos</span>
            <!-- Contador de selección -->
            <span class="badge bg-primary ms-1" id="contador-seleccion" style="display: none;">
                0 seleccionados
            </span>
        </h6>
        
        <!-- Barra de acciones masivas -->
        <div id="acciones-masivas" style="display: none;" class="btn-group btn-group-sm">
            <button class="btn btn-outline-success" onclick="activarSeleccionados()" 
                title="Activar seleccionados">
                <i class="bi bi-check-circle me-1"></i>Activar
            </button>
            <button class="btn btn-outline-warning" onclick="desactivarSeleccionados()" 
                title="Desactivar seleccionados">
                <i class="bi bi-pause-circle me-1"></i>Desactivar
            </button>
            <button class="btn btn-outline-primary" onclick="exportarSeleccionados()" 
                title="Exportar seleccionados">
                <i class="bi bi-download me-1"></i>Exportar
            </button>
            <button class="btn btn-outline-danger" onclick="eliminarSeleccionados()" 
                title="Eliminar seleccionados">
                <i class="bi bi-trash me-1"></i>Eliminar
            </button>
        </div>
    </div>
</div>
```

---

### Paso 3: Agregar Columna de Checkbox en la Tabla

Modificar el `<thead>`:

```html
<thead class="table-dark">
    <tr>
        <!-- NUEVA COLUMNA DE CHECKBOX -->
        <th style="width: 50px;">
            <input type="checkbox" class="form-check-input" id="select-all">
        </th>
        
        <!-- Columnas existentes -->
        <th style="width: 60px;"><i class="bi bi-hash me-1"></i>ID</th>
        <th><i class="bi bi-card-text me-1"></i>Código</th>
        <th><i class="bi bi-text-left me-1"></i>Nombre</th>
        <!-- ... más columnas ... -->
    </tr>
</thead>
```

---

### Paso 4: Agregar Checkbox en cada Fila

Modificar la función que genera las filas (en JavaScript):

```javascript
function renderizarFila(item) {
    return `
        <tr>
            <!-- NUEVO CHECKBOX -->
            <td>
                <input class="form-check-input" 
                       type="checkbox" 
                       data-id="${item.id}">
            </td>
            
            <!-- Celdas existentes -->
            <td>${item.id}</td>
            <td>${item.codigo}</td>
            <td>${item.nombre}</td>
            <!-- ... más celdas ... -->
        </tr>
    `;
}
```

**IMPORTANTE:** El `data-id="${item.id}"` es obligatorio para que funcione.

---

### Paso 5: Inicializar el Sistema en JavaScript

Al final de tu archivo JS del módulo:

```javascript
// Variable global para el sistema de selección
let seleccionMasiva;

// Inicializar al cargar el DOM
document.addEventListener('DOMContentLoaded', function() {
    // ... código existente ...
    
    // Inicializar selección masiva
    initSeleccionMasivaModulo();
});

// Función de inicialización
function initSeleccionMasivaModulo() {
    seleccionMasiva = initSeleccionMasiva({
        // IDs de los elementos
        selectAllId: 'select-all',
        tableBodyId: 'tabla-items',  // Cambiar según tu tabla
        contadorId: 'contador-seleccion',
        accionesMasivasId: 'acciones-masivas',
        
        // Nombres para mensajes
        entityName: 'elementos',  // plural
        entityNameSingular: 'elemento',  // singular
        
        // Función para obtener los datos actuales
        getData: () => itemsGlobal,  // Array con tus datos
        
        // Callback cuando cambia la selección (opcional)
        onSelectionChange: (seleccionados) => {
            console.log(`${seleccionados.length} elementos seleccionados`);
        }
    });
}
```

---

### Paso 6: Implementar Funciones de Acciones Masivas

```javascript
// Activar elementos seleccionados
function activarSeleccionados() {
    seleccionMasiva.confirmarAccionMasiva('activar', async (seleccionados) => {
        try {
            // Realizar la acción para cada elemento
            for (const item of seleccionados) {
                await cambiarEstado(item.id, true);
            }
            
            mostrarMensaje(
                `${seleccionados.length} elemento(s) activado(s) exitosamente`,
                'success'
            );
            
            // Recargar datos
            cargarItems();
        } catch (error) {
            mostrarMensaje('Error al activar elementos: ' + error.message, 'danger');
        }
    });
}

// Desactivar elementos seleccionados
function desactivarSeleccionados() {
    seleccionMasiva.confirmarAccionMasiva('desactivar', async (seleccionados) => {
        try {
            for (const item of seleccionados) {
                await cambiarEstado(item.id, false);
            }
            
            mostrarMensaje(
                `${seleccionados.length} elemento(s) desactivado(s) exitosamente`,
                'success'
            );
            
            cargarItems();
        } catch (error) {
            mostrarMensaje('Error al desactivar elementos: ' + error.message, 'danger');
        }
    });
}

// Exportar elementos seleccionados
async function exportarSeleccionados() {
    const seleccionados = seleccionMasiva.obtenerSeleccionados();
    
    if (seleccionados.length === 0) {
        mostrarMensaje('No hay elementos seleccionados', 'warning');
        return;
    }
    
    try {
        // Convertir a CSV
        const csv = convertirACSV(seleccionados);
        
        // Descargar archivo
        descargarCSV(csv, 'elementos-seleccionados.csv');
        
        mostrarMensaje(
            `${seleccionados.length} elemento(s) exportado(s) exitosamente`,
            'success'
        );
    } catch (error) {
        mostrarMensaje('Error al exportar: ' + error.message, 'danger');
    }
}

// Eliminar elementos seleccionados
function eliminarSeleccionados() {
    seleccionMasiva.confirmarAccionMasiva('eliminar', async (seleccionados) => {
        try {
            // Eliminar cada elemento
            for (const item of seleccionados) {
                await eliminarItem(item.id);
            }
            
            mostrarMensaje(
                `${seleccionados.length} elemento(s) eliminado(s) exitosamente`,
                'success'
            );
            
            // Recargar datos
            cargarItems();
        } catch (error) {
            mostrarMensaje('Error al eliminar elementos: ' + error.message, 'danger');
        }
    });
}
```

---

## 📝 Ejemplos por Módulo

### Ejemplo 1: Activos

```javascript
// En activos.js

let seleccionMasivaActivos;

function initSeleccionMasivaActivos() {
    seleccionMasivaActivos = initSeleccionMasiva({
        selectAllId: 'select-all',
        tableBodyId: 'tabla-activos',
        contadorId: 'contador-seleccion',
        accionesMasivasId: 'acciones-masivas',
        entityName: 'activos',
        entityNameSingular: 'activo',
        getData: () => activos
    });
}

function activarActivosSeleccionados() {
    seleccionMasivaActivos.confirmarAccionMasiva('activar', async (seleccionados) => {
        for (const activo of seleccionados) {
            await fetch(`/api/activos/${activo.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ activo: true })
            });
        }
        cargarActivos();
        mostrarMensaje(`${seleccionados.length} activo(s) activado(s)`, 'success');
    });
}
```

---

### Ejemplo 2: Inventario

```javascript
// En inventario.js

let seleccionMasivaInventario;

function initSeleccionMasivaInventario() {
    seleccionMasivaInventario = initSeleccionMasiva({
        selectAllId: 'select-all',
        tableBodyId: 'tabla-inventario',
        contadorId: 'contador-seleccion',
        accionesMasivasId: 'acciones-masivas',
        entityName: 'artículos',
        entityNameSingular: 'artículo',
        getData: () => inventario
    });
}

function exportarInventarioSeleccionado() {
    const seleccionados = seleccionMasivaInventario.obtenerSeleccionados();
    
    if (seleccionados.length === 0) {
        mostrarMensaje('No hay artículos seleccionados', 'warning');
        return;
    }
    
    // Generar CSV con columnas específicas de inventario
    const headers = ['Código', 'Descripción', 'Stock', 'Precio', 'Categoría'];
    const rows = seleccionados.map(item => [
        item.codigo,
        item.descripcion,
        item.stock_actual,
        item.precio_promedio,
        item.categoria
    ]);
    
    const csv = generarCSV(headers, rows);
    descargarCSV(csv, 'inventario-seleccionado.csv');
}
```

---

### Ejemplo 3: Órdenes de Trabajo

```javascript
// En ordenes.js

let seleccionMasivaOrdenes;

function initSeleccionMasivaOrdenes() {
    seleccionMasivaOrdenes = initSeleccionMasiva({
        selectAllId: 'select-all',
        tableBodyId: 'tabla-ordenes',
        contadorId: 'contador-seleccion',
        accionesMasivasId: 'acciones-masivas',
        entityName: 'órdenes',
        entityNameSingular: 'orden',
        getData: () => ordenes
    });
}

function cambiarEstadoOrdenesSeleccionadas(nuevoEstado) {
    seleccionMasivaOrdenes.confirmarAccionMasiva(
        `cambiar estado a "${nuevoEstado}"`,
        async (seleccionados) => {
            for (const orden of seleccionados) {
                await fetch(`/api/ordenes/${orden.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ estado: nuevoEstado })
                });
            }
            cargarOrdenes();
            mostrarMensaje(
                `${seleccionados.length} orden(es) actualizada(s)`,
                'success'
            );
        }
    );
}
```

---

### Ejemplo 4: Proveedores

```javascript
// En proveedores.js

let seleccionMasivaProveedores;

function initSeleccionMasivaProveedores() {
    seleccionMasivaProveedores = initSeleccionMasiva({
        selectAllId: 'select-all',
        tableBodyId: 'tabla-proveedores',
        contadorId: 'contador-seleccion',
        accionesMasivasId: 'acciones-masivas',
        entityName: 'proveedores',
        entityNameSingular: 'proveedor',
        getData: () => proveedores
    });
}

function enviarEmailProveedoresSeleccionados() {
    const seleccionados = seleccionMasivaProveedores.obtenerSeleccionados();
    
    if (seleccionados.length === 0) {
        mostrarMensaje('No hay proveedores seleccionados', 'warning');
        return;
    }
    
    // Abrir modal de email con proveedores seleccionados
    const emails = seleccionados.map(p => p.email).filter(e => e);
    mostrarModalEmail(emails);
}
```

---

## 🎨 Personalización de Acciones

Puedes personalizar las acciones masivas según cada módulo:

```html
<!-- Acciones específicas para Órdenes -->
<div id="acciones-masivas" style="display: none;" class="btn-group btn-group-sm">
    <button class="btn btn-outline-primary" onclick="asignarTecnicoMasivo()">
        <i class="bi bi-person-plus me-1"></i>Asignar Técnico
    </button>
    <button class="btn btn-outline-success" onclick="completarOrdenesSeleccionadas()">
        <i class="bi bi-check-circle me-1"></i>Completar
    </button>
    <button class="btn btn-outline-warning" onclick="cambiarPrioridadMasiva()">
        <i class="bi bi-exclamation-circle me-1"></i>Cambiar Prioridad
    </button>
    <button class="btn btn-outline-info" onclick="exportarSeleccionados()">
        <i class="bi bi-download me-1"></i>Exportar
    </button>
</div>

<!-- Acciones específicas para Inventario -->
<div id="acciones-masivas" style="display: none;" class="btn-group btn-group-sm">
    <button class="btn btn-outline-primary" onclick="ajustarStockMasivo()">
        <i class="bi bi-arrows-expand me-1"></i>Ajustar Stock
    </button>
    <button class="btn btn-outline-warning" onclick="marcarCriticosMasivo()">
        <i class="bi bi-exclamation-triangle me-1"></i>Marcar Críticos
    </button>
    <button class="btn btn-outline-success" onclick="generarOrdenCompraMasiva()">
        <i class="bi bi-cart-plus me-1"></i>Orden de Compra
    </button>
    <button class="btn btn-outline-info" onclick="exportarSeleccionados()">
        <i class="bi bi-download me-1"></i>Exportar
    </button>
</div>
```

---

## 🔧 Métodos Disponibles

La instancia de `seleccionMasiva` proporciona los siguientes métodos:

```javascript
// Obtener IDs seleccionados
const ids = seleccionMasiva.obtenerIdsSeleccionados();

// Obtener objetos completos seleccionados
const items = seleccionMasiva.obtenerSeleccionados();

// Limpiar toda la selección
seleccionMasiva.limpiarSeleccion();

// Seleccionar por IDs específicos
seleccionMasiva.seleccionarPorIds([1, 3, 5]);

// Actualizar estado manualmente
seleccionMasiva.actualizarEstadoSeleccion();

// Confirmar acción con modal
seleccionMasiva.confirmarAccionMasiva('acción', (seleccionados) => {
    // Tu código aquí
});

// Exportar seleccionados (básico)
seleccionMasiva.exportarSeleccionados('csv');
```

---

## ✅ Checklist de Implementación

Por cada módulo que implementes:

- [ ] Agregar `seleccion-masiva.css` en el `{% block extra_head %}`
- [ ] Agregar `seleccion-masiva.js` antes del script del módulo
- [ ] Agregar checkbox en `<thead>` con `id="select-all"`
- [ ] Agregar columna de checkbox en cada `<tr>` con `data-id`
- [ ] Agregar contador de selección con `id="contador-seleccion"`
- [ ] Agregar barra de acciones con `id="acciones-masivas"`
- [ ] Inicializar `initSeleccionMasiva()` en el JavaScript
- [ ] Implementar funciones de acciones masivas
- [ ] Probar selección individual
- [ ] Probar selección total
- [ ] Probar acciones masivas
- [ ] Verificar responsive en móvil

---

## 🐛 Troubleshooting

### Problema: El checkbox "Seleccionar todo" no funciona

**Solución:** Verificar que el ID sea `select-all` y que esté configurado en `initSeleccionMasiva()`.

### Problema: Los checkboxes individuales no se marcan

**Solución:** Asegurarse de que tengan el atributo `data-id="${item.id}"`.

### Problema: No aparecen las acciones masivas

**Solución:** Verificar que el ID sea `acciones-masivas` y que esté configurado correctamente.

### Problema: El contador no se actualiza

**Solución:** Verificar que el ID sea `contador-seleccion` y que esté dentro del `card-header`.

---

## 📚 Recursos Adicionales

- **Archivo JavaScript:** `static/js/seleccion-masiva.js`
- **Archivo CSS:** `static/css/seleccion-masiva.css`
- **Ejemplo completo:** Ver `usuarios.html` y `usuarios.js`

---

## 🎉 Conclusión

Con este sistema modular, puedes agregar funcionalidad de selección múltiple a cualquier lista del sistema en menos de 30 minutos.

Las principales ventajas son:
- ✅ Código reutilizable
- ✅ Fácil de implementar
- ✅ Consistencia en toda la aplicación
- ✅ Mantenible y escalable

**Fecha:** 1 de octubre de 2025  
**Versión:** 1.0  
**Estado:** ✅ Listo para implementar
