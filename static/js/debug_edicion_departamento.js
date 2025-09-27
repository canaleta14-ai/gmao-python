document.addEventListener('DOMContentLoaded', function () {
    console.log('Debug: DOM cargado');

    // Verificar si el botón de edición existe y agregar un listener de debug
    setTimeout(() => {
        const botonesEditar = document.querySelectorAll('[onclick*="editarActivo"]');
        console.log(`Debug: Encontrados ${botonesEditar.length} botones de editar`);

        botonesEditar.forEach((boton, index) => {
            const originalOnclick = boton.onclick;
            boton.onclick = function (e) {
                console.log(`Debug: Haciendo clic en editar activo ${index + 1}`);

                // Interceptar la función editarActivo
                const originalEditarActivo = window.editarActivo;
                window.editarActivo = function (id) {
                    console.log(`Debug: editarActivo llamado con ID: ${id}`);

                    // Llamar a la función original
                    return originalEditarActivo.call(this, id).then(() => {
                        console.log('Debug: editarActivo completado');

                        // Verificar el estado del select después de la edición
                        setTimeout(() => {
                            const select = document.getElementById('nuevo-departamento');
                            if (select) {
                                console.log('Debug: Estado del select después de editar:');
                                console.log('- Valor seleccionado:', select.value);
                                console.log('- Opciones disponibles:', Array.from(select.options).map(o => `${o.value} - ${o.text}`));
                            }
                        }, 500);
                    });
                };

                // Ejecutar el onclick original
                if (originalOnclick) {
                    return originalOnclick.call(this, e);
                }
            };
        });
    }, 1000);
});