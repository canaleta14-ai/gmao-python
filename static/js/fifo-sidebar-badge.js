/**
 * Script para actualizar el badge FIFO en el sidebar con información en tiempo real
 */

document.addEventListener("DOMContentLoaded", function () {
  // Actualizar badge FIFO al cargar la página
  updateFifoBadge();

  // Actualizar cada 5 minutos
  setInterval(updateFifoBadge, 5 * 60 * 1000);
});

async function updateFifoBadge() {
  try {
    const badge = document.getElementById("fifo-alert-badge");
    const countElement = document.getElementById("fifo-count");

    if (!badge || !countElement) {
      return; // No está en una página con sidebar
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

    // Actualizar el badge según el estado
    if (lotesVencidos > 0) {
      // Lotes vencidos - badge rojo
      badge.className = "badge bg-danger text-white rounded-pill fifo-badge";
      badge.innerHTML = `<i class="bi bi-exclamation-triangle-fill"></i> <span>${lotesVencidos}</span>`;
      badge.title = `${lotesVencidos} lote(s) vencido(s)`;

      // Animación de alerta
      badge.style.animation = "pulse 1.5s infinite";
    } else if (lotesProximosVencer > 0) {
      // Lotes próximos a vencer - badge naranja
      badge.className = "badge bg-warning text-dark rounded-pill fifo-badge";
      badge.innerHTML = `<i class="bi bi-clock-fill"></i> <span>${lotesProximosVencer}</span>`;
      badge.title = `${lotesProximosVencer} lote(s) próximo(s) a vencer`;

      // Animación sutil
      badge.style.animation = "fadeInOut 3s infinite";
    } else {
      // Todo ok - badge verde
      badge.className = "badge bg-success text-white rounded-pill fifo-badge";
      badge.innerHTML = `<i class="bi bi-check-circle-fill"></i> OK`;
      badge.title = "Sistema FIFO: Sin alertas";

      // Sin animación
      badge.style.animation = "none";
    }

    console.log("🏷️ Badge FIFO actualizado:", {
      vencidos: lotesVencidos,
      proximosVencer: lotesProximosVencer,
      totalLotes: data.lotes ? data.lotes.length : 0,
    });
  } catch (error) {
    console.error("❌ Error actualizando badge FIFO:", error);

    // Badge de error
    const badge = document.getElementById("fifo-alert-badge");
    const countElement = document.getElementById("fifo-count");

    if (badge && countElement) {
      badge.className = "badge bg-secondary text-white rounded-pill fifo-badge";
      badge.innerHTML = `<i class="bi bi-question-circle"></i> ?`;
      badge.title = "Error al obtener datos FIFO";
      badge.style.animation = "none";
    }
  }
}

// Función para actualizar badge cuando se realicen operaciones FIFO
window.updateFifoBadgeAfterOperation = function () {
  setTimeout(updateFifoBadge, 1000); // Actualizar después de 1 segundo
};

// CSS animations para el badge
const style = document.createElement("style");
style.textContent = `
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
}

@keyframes fadeInOut {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.fifo-badge {
    font-size: 0.7rem !important;
    padding: 0.25rem 0.5rem !important;
    font-weight: 600 !important;
    min-width: 35px;
    text-align: center;
    transition: all 0.3s ease;
}

.fifo-badge:hover {
    transform: scale(1.1);
}
`;
document.head.appendChild(style);
