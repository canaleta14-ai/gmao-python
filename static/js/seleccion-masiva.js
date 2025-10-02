/**
 * Sistema de Selección Masiva para Tablas
 * 
 * Este módulo proporciona funcionalidad de selección múltiple con checkboxes
 * y acciones masivas para cualquier tabla del sistema.
 * 
 * Características:
 * - Checkbox "Seleccionar todo" en el encabezado
 * - Checkboxes individuales por fila
 * - Contador de elementos seleccionados
 * - Barra de acciones masivas
 * - Estado intermedio del checkbox principal
 * - Gestión automática de eventos
 * 
 * Uso:
 * 1. Incluir este script en la página
 * 2. Agregar checkboxes a la tabla con la estructura correcta
 * 3. Llamar a initSeleccionMasiva() con la configuración
 */

class SeleccionMasiva {
  constructor(config) {
    this.config = {
      // Selectores
      selectAllId: config.selectAllId || 'select-all',
      tableBodyId: config.tableBodyId || 'tabla-body',
      contadorId: config.contadorId || 'contador-seleccion',
      accionesMasivasId: config.accionesMasivasId || 'acciones-masivas',
      
      // Configuración
      entityName: config.entityName || 'elementos',
      entityNameSingular: config.entityNameSingular || 'elemento',
      
      // Callbacks
      onSelectionChange: config.onSelectionChange || null,
      
      // Datos
      getData: config.getData || (() => [])
    };
    
    this.init();
  }
  
  init() {
    this.setupSelectAllListener();
    this.setupCheckboxListeners();
  }
  
  setupSelectAllListener() {
    const selectAllCheckbox = document.getElementById(this.config.selectAllId);
    if (selectAllCheckbox) {
      selectAllCheckbox.addEventListener('change', (e) => {
        this.toggleSelectAll(e.target.checked);
      });
    }
  }
  
  setupCheckboxListeners() {
    // Usar event delegation para checkboxes individuales
    const tableBody = document.getElementById(this.config.tableBodyId);
    if (tableBody) {
      tableBody.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox' && e.target.dataset.id) {
          this.actualizarEstadoSeleccion();
          this.mostrarAccionesMasivas();
          
          if (this.config.onSelectionChange) {
            this.config.onSelectionChange(this.obtenerSeleccionados());
          }
        }
      });
    }
  }
  
  toggleSelectAll(seleccionado) {
    const checkboxes = this.getAllCheckboxes();
    checkboxes.forEach((checkbox) => {
      checkbox.checked = seleccionado;
    });
    this.actualizarEstadoSeleccion();
    this.mostrarAccionesMasivas();
    
    if (this.config.onSelectionChange) {
      this.config.onSelectionChange(this.obtenerSeleccionados());
    }
  }
  
  getAllCheckboxes() {
    return document.querySelectorAll(
      `#${this.config.tableBodyId} input[type="checkbox"][data-id]`
    );
  }
  
  getCheckedCheckboxes() {
    return document.querySelectorAll(
      `#${this.config.tableBodyId} input[type="checkbox"][data-id]:checked`
    );
  }
  
  actualizarEstadoSeleccion() {
    const checkboxes = this.getAllCheckboxes();
    const selectAllCheckbox = document.getElementById(this.config.selectAllId);
    const totalCheckboxes = checkboxes.length;
    const seleccionados = this.getCheckedCheckboxes();
    const totalSeleccionados = seleccionados.length;
    
    // Actualizar estado del checkbox "Seleccionar todo"
    if (selectAllCheckbox) {
      if (totalSeleccionados === 0) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = false;
      } else if (totalSeleccionados === totalCheckboxes) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = true;
      } else {
        selectAllCheckbox.indeterminate = true;
        selectAllCheckbox.checked = false;
      }
    }
    
    // Actualizar contador de seleccionados
    this.actualizarContador(totalSeleccionados);
  }
  
  actualizarContador(totalSeleccionados) {
    const contadorSeleccion = document.getElementById(this.config.contadorId);
    if (contadorSeleccion) {
      if (totalSeleccionados > 0) {
        contadorSeleccion.textContent = `${totalSeleccionados} seleccionado${
          totalSeleccionados > 1 ? 's' : ''
        }`;
        contadorSeleccion.style.display = 'inline';
      } else {
        contadorSeleccion.style.display = 'none';
      }
    }
  }
  
  mostrarAccionesMasivas() {
    const seleccionados = this.getCheckedCheckboxes();
    const accionesMasivas = document.getElementById(this.config.accionesMasivasId);
    
    if (accionesMasivas) {
      if (seleccionados.length > 0) {
        accionesMasivas.style.display = 'block';
      } else {
        accionesMasivas.style.display = 'none';
      }
    }
  }
  
  obtenerIdsSeleccionados() {
    const seleccionados = this.getCheckedCheckboxes();
    return Array.from(seleccionados).map((checkbox) =>
      parseInt(checkbox.getAttribute('data-id'))
    );
  }
  
  obtenerSeleccionados() {
    const ids = this.obtenerIdsSeleccionados();
    const data = this.config.getData();
    return data.filter((item) => ids.includes(item.id));
  }
  
  limpiarSeleccion() {
    const checkboxes = this.getAllCheckboxes();
    checkboxes.forEach((checkbox) => {
      checkbox.checked = false;
    });
    this.actualizarEstadoSeleccion();
    this.mostrarAccionesMasivas();
  }
  
  seleccionarPorIds(ids) {
    const checkboxes = this.getAllCheckboxes();
    checkboxes.forEach((checkbox) => {
      const id = parseInt(checkbox.getAttribute('data-id'));
      checkbox.checked = ids.includes(id);
    });
    this.actualizarEstadoSeleccion();
    this.mostrarAccionesMasivas();
  }
  
  // Métodos auxiliares para acciones masivas comunes
  
  async exportarSeleccionados(formato = 'csv') {
    const seleccionados = this.obtenerSeleccionados();
    if (seleccionados.length === 0) {
      mostrarMensaje('No hay elementos seleccionados', 'warning');
      return;
    }
    
    // Implementar exportación según el formato
    console.log(`Exportando ${seleccionados.length} elementos en formato ${formato}`);
    return seleccionados;
  }
  
  confirmarAccionMasiva(accion, callback) {
    const seleccionados = this.obtenerSeleccionados();
    if (seleccionados.length === 0) {
      mostrarMensaje('No hay elementos seleccionados', 'warning');
      return;
    }
    
    const mensaje = seleccionados.length === 1
      ? `¿Estás seguro de ${accion} este ${this.config.entityNameSingular}?`
      : `¿Estás seguro de ${accion} estos ${seleccionados.length} ${this.config.entityName}?`;
    
    showConfirmModal({
      title: `${accion.charAt(0).toUpperCase() + accion.slice(1)} ${this.config.entityName}`,
      message: mensaje,
      confirmText: 'Confirmar',
      cancelText: 'Cancelar',
      type: 'warning',
      onConfirm: () => {
        if (typeof callback === 'function') {
          callback(seleccionados);
        } else {
          console.warn('⚠️ Callback no proporcionado para acción masiva');
        }
        this.limpiarSeleccion();
      }
    });
  }
}

// Función auxiliar para inicializar en las páginas
function initSeleccionMasiva(config) {
  return new SeleccionMasiva(config);
}

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SeleccionMasiva, initSeleccionMasiva };
}
