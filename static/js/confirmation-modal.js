// Sistema de confirmación con modales Bootstrap
function showConfirmModal(options) {
  const defaults = {
    title: "Confirmación",
    message: "¿Está seguro que desea continuar?",
    confirmText: "Confirmar",
    cancelText: "Cancelar",
    type: "warning", // success, warning, danger, info
    onConfirm: () => {},
    onCancel: () => {},
  };

  const config = { ...defaults, ...options };

  // Crear el modal HTML
  const modalId = "confirmModal_" + Date.now();
  const modalHTML = `
        <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0">
                        <h5 class="modal-title d-flex align-items-center" id="${modalId}Label">
                            <i class="bi ${getModalIcon(
                              config.type
                            )} me-2 ${getModalIconColor(config.type)}"></i>
                            ${config.title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">${config.message}</p>
                    </div>
                    <div class="modal-footer border-0">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle me-1"></i>${
                              config.cancelText
                            }
                        </button>
                        <button type="button" class="btn ${getModalButtonClass(
                          config.type
                        )}" id="${modalId}Confirm">
                            <i class="bi ${getModalConfirmIcon(
                              config.type
                            )} me-1"></i>${config.confirmText}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

  // Agregar el modal al DOM
  document.body.insertAdjacentHTML("beforeend", modalHTML);

  // Obtener referencias al modal
  const modalElement = document.getElementById(modalId);
  const confirmButton = document.getElementById(modalId + "Confirm");

  // Configurar eventos
  confirmButton.addEventListener("click", function () {
    config.onConfirm();
    const modal = bootstrap.Modal.getInstance(modalElement);
    modal.hide();
  });

  modalElement.addEventListener("hidden.bs.modal", function () {
    modalElement.remove(); // Limpiar el DOM
  });

  modalElement.addEventListener("hide.bs.modal", function (e) {
    // Si se cierra sin confirmar, ejecutar onCancel
    if (e.target === modalElement && !confirmButton.disabled) {
      config.onCancel();
    }
  });

  // Mostrar el modal
  const modal = new bootstrap.Modal(modalElement);
  modal.show();

  return modal;
}

function getModalIcon(type) {
  const icons = {
    success: "bi-check-circle",
    warning: "bi-exclamation-triangle",
    danger: "bi-exclamation-triangle",
    info: "bi-info-circle",
  };
  return icons[type] || icons["info"];
}

function getModalIconColor(type) {
  const colors = {
    success: "text-success",
    warning: "text-warning",
    danger: "text-danger",
    info: "text-info",
  };
  return colors[type] || colors["info"];
}

function getModalButtonClass(type) {
  const classes = {
    success: "btn-success",
    warning: "btn-warning",
    danger: "btn-danger",
    info: "btn-primary",
  };
  return classes[type] || classes["info"];
}

function getModalConfirmIcon(type) {
  const icons = {
    success: "bi-check-circle",
    warning: "bi-exclamation-triangle",
    danger: "bi-trash",
    info: "bi-check-circle",
  };
  return icons[type] || icons["info"];
}

// Función de conveniencia para confirmación de logout
function showLogoutConfirmation(onConfirm) {
  showConfirmModal({
    title: "Cerrar Sesión",
    message: "¿Está seguro que desea cerrar sesión?",
    confirmText: "Cerrar Sesión",
    cancelText: "Cancelar",
    type: "warning",
    onConfirm: onConfirm,
  });
}

// Función de conveniencia para confirmación de eliminación
function showDeleteConfirmation(itemName, onConfirm) {
  showConfirmModal({
    title: "Eliminar Elemento",
    message: `¿Está seguro que desea eliminar "${itemName}"? Esta acción no se puede deshacer.`,
    confirmText: "Eliminar",
    cancelText: "Cancelar",
    type: "danger",
    onConfirm: onConfirm,
  });
}

// Exportar función globalmente
window.showConfirmModal = showConfirmModal;
