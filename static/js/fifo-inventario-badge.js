/**
 * Script para el badge FIFO en la página de inventario
 * Actualiza el botón con notificaciones de lotes próximos a vencer
 */

document.addEventListener("DOMContentLoaded", function () {
  // Actualizar badge FIFO al cargar la página
  updateFifoInventoryBadge();

  // Actualizar cada 5 minutos
  setInterval(updateFifoInventoryBadge, 5 * 60 * 1000);
});

async function updateFifoInventoryBadge() {
  try {
    const btnFifo = document.getElementById("btn-fifo");
    const badge = document.getElementById("fifo-notification-badge");
    const countElement = document.getElementById("fifo-notification-count");

    if (!btnFifo || !badge || !countElement) {
      return; // Elementos no encontrados
    }

    // Obtener datos del API de lotes
    const response = await fetch("/lotes/api/inventario/activos");

    if (!response.ok) {
      throw new Error("Error al obtener datos FIFO");
    }

    const data = await response.json();

    // Calcular lotes próximos a vencer (próximos 30 días)
    const hoy = new Date();
    const treintaDias = new Date(hoy.getTime() + 30 * 24 * 60 * 60 * 1000);

    let lotesProximosVencer = 0;
    let lotesVencidos = 0;

    if (data.lotes && Array.isArray(data.lotes)) {
      data.lotes.forEach((lote) => {
        if (lote.fecha_vencimiento) {
          const fechaVencimiento = new Date(lote.fecha_vencimiento);

          if (fechaVencimiento < hoy) {
            lotesVencidos++;
          } else if (fechaVencimiento <= treintaDias) {
            lotesProximosVencer++;
          }
        }
      });
    }

    // Actualizar el botón y badge según el estado
    if (lotesVencidos > 0) {
      // Lotes vencidos - badge rojo y botón con alerta
      btnFifo.className = "btn btn-outline-danger position-relative";
      btnFifo.title = `¡${lotesVencidos} lote(s) vencido(s)! Haga clic para gestionar`;

      badge.className =
        "position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger";
      badge.style.display = "block";
      countElement.textContent = lotesVencidos;

      // Animación de alerta
      btnFifo.style.animation = "pulse 1.5s infinite";
    } else if (lotesProximosVencer > 0) {
      // Lotes próximos a vencer - badge naranja
      btnFifo.className = "btn btn-outline-warning position-relative";
      btnFifo.title = `${lotesProximosVencer} lote(s) próximo(s) a vencer en 30 días`;

      badge.className =
        "position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-dark";
      badge.style.display = "block";
      countElement.textContent = lotesProximosVencer;

      // Animación sutil
      btnFifo.style.animation = "fadeInOut 3s infinite";
    } else {
      // Todo ok - sin badge
      btnFifo.className = "btn btn-outline-warning position-relative";
      btnFifo.title = "Gestión FIFO - Sistema sin alertas";

      badge.style.display = "none";

      // Sin animación
      btnFifo.style.animation = "none";
    }

    console.log("🏷️ Badge FIFO actualizado en inventario:", {
      vencidos: lotesVencidos,
      proximosVencer: lotesProximosVencer,
      totalLotes: data.lotes ? data.lotes.length : 0,
    });
  } catch (error) {
    console.error("❌ Error actualizando badge FIFO en inventario:", error);

    // Badge de error
    const btnFifo = document.getElementById("btn-fifo");
    const badge = document.getElementById("fifo-notification-badge");

    if (btnFifo && badge) {
      btnFifo.className = "btn btn-outline-secondary position-relative";
      btnFifo.title = "Error al obtener datos FIFO";
      badge.style.display = "none";
      btnFifo.style.animation = "none";
    }
  }
}

// Función para actualizar badge cuando se realicen operaciones de inventario
window.updateFifoInventoryBadgeAfterOperation = function () {
  setTimeout(updateFifoInventoryBadge, 1000); // Actualizar después de 1 segundo
};

// CSS animations para el botón
const fifoBadgeStyle = document.createElement("style");
fifoBadgeStyle.textContent = `
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.02); }
}

@keyframes fadeInOut {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.9; }
}

#btn-fifo {
    transition: all 0.3s ease;
}

#btn-fifo:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

#fifo-notification-badge {
    font-size: 0.6rem !important;
    padding: 0.2rem 0.4rem !important;
    min-width: 18px;
    text-align: center;
    font-weight: 700;
}
`;
document.head.appendChild(fifoBadgeStyle);
