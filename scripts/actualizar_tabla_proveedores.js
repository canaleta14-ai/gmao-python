// Función actualizada para mostrar proveedores en la tabla con campos separados
function mostrarProveedores(proveedoresAMostrar) {
  console.log(
    "mostrarProveedores llamada con:",
    proveedoresAMostrar.length,
    "proveedores"
  );
  const tbody = document.getElementById("tbody-proveedores");
  console.log("tbody encontrado:", tbody);
  if (!tbody) return;

  tbody.innerHTML = "";

  if (proveedoresAMostrar.length === 0) {
    console.log("No hay proveedores para mostrar");
    tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                    No se encontraron proveedores
                </td>
            </tr>
        `;
    return;
  }

  console.log("Renderizando", proveedoresAMostrar.length, "proveedores");
  proveedoresAMostrar.forEach((proveedor) => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
            <td>
                <div class="fw-bold">${proveedor.nombre}</div>
            </td>
            <td><code>${proveedor.nif}</code></td>
            <td>${
              proveedor.direccion || '<span class="text-muted">—</span>'
            }</td>
            <td>${
              proveedor.contacto || '<span class="text-muted">—</span>'
            }</td>
            <td>
                ${
                  proveedor.telefono
                    ? `<a href="tel:${proveedor.telefono}" class="text-decoration-none"><i class="bi bi-telephone me-1"></i>${proveedor.telefono}</a>`
                    : '<span class="text-muted">—</span>'
                }
            </td>
            <td>
                ${
                  proveedor.email
                    ? `<a href="mailto:${proveedor.email}" class="text-decoration-none"><i class="bi bi-envelope me-1"></i>${proveedor.email}</a>`
                    : '<span class="text-muted">—</span>'
                }
            </td>
            <td><code class="small">${proveedor.cuenta_contable}</code></td>
            <td class="text-center">
                <span class="badge ${
                  proveedor.activo ? "bg-success" : "bg-secondary"
                }">
                    ${proveedor.activo ? "Activo" : "Inactivo"}
                </span>
            </td>
            <td class="text-center">
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-sm btn-outline-primary action-btn view" onclick="verProveedor(${
                      proveedor.id
                    })" title="Ver">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary action-btn edit" onclick="editarProveedor(${
                      proveedor.id
                    })" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm ${
                      proveedor.activo
                        ? "btn-outline-warning"
                        : "btn-outline-success"
                    } action-btn toggle" onclick="toggleProveedor(${
      proveedor.id
    })" title="${proveedor.activo ? "Desactivar" : "Activar"}">
                        <i class="bi ${
                          proveedor.activo ? "bi-toggle-off" : "bi-toggle-on"
                        }"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger action-btn delete" onclick="eliminarProveedor(${
                      proveedor.id
                    }, '${proveedor.nombre}')" title="Eliminar">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        `;
    tbody.appendChild(fila);
  });

  // Actualizar contador
  const contador = document.getElementById("contador-proveedores");
  if (contador) {
    contador.textContent = `${proveedoresAMostrar.length} proveedores`;
  }
}
