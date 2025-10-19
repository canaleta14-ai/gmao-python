/**
 * Fix para forzar estilos morados en botones de inventario
 * Se ejecuta inmediatamente sin esperar DOMContentLoaded
 */

(function () {
  "use strict";

  function aplicarEstilosBotones() {
    // Seleccionar SOLO los 4 botones específicos del header de inventario
    const selectores = [
      'button[onclick="exportarCSV()"]',
      'button[onclick="mostrarModalMovimientoGeneral()"]',
      'button[onclick="mostrarMovimientos()"]',
      'a[href*="conteos_page"]',
    ];

    selectores.forEach((selector) => {
      const boton = document.querySelector(selector);
      if (!boton) return;

      // Remover cualquier clase conflictiva
      boton.classList.remove("btn-custom-purple");

      // Aplicar estilos base con !important
      const estilosBase = {
        background: "transparent",
        border: "2px solid #667eea",
        color: "#667eea",
        "border-radius": "2px",
        transition: "all 0.3s ease",
      };

      Object.entries(estilosBase).forEach(([prop, value]) => {
        boton.style.setProperty(prop, value, "important");
      });

      // Agregar eventos de hover
      boton.addEventListener("mouseenter", function () {
        this.style.setProperty(
          "background",
          "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          "important"
        );
        this.style.setProperty("color", "white", "important");
        this.style.setProperty("border-color", "#667eea", "important");
        this.style.setProperty("transform", "translateY(-2px)", "important");
        this.style.setProperty(
          "box-shadow",
          "0 5px 15px rgba(102, 126, 234, 0.4)",
          "important"
        );
      });

      boton.addEventListener("mouseleave", function () {
        this.style.setProperty("background", "transparent", "important");
        this.style.setProperty("color", "#667eea", "important");
        this.style.setProperty("border-color", "#667eea", "important");
        this.style.setProperty("transform", "translateY(0)", "important");
        this.style.setProperty("box-shadow", "none", "important");
      });

      console.log("✅ Estilos aplicados a:", selector);
    });
  }

  // Ejecutar inmediatamente
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", aplicarEstilosBotones);
  } else {
    aplicarEstilosBotones();
  }

  // Re-aplicar después de 100ms por si acaso
  setTimeout(aplicarEstilosBotones, 100);

  console.log("🎨 Script de fix de botones de inventario cargado");
})();
