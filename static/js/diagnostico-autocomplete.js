// Script de diagnóstico para autocompletado
// Ejecutar en la consola del navegador: diagnosticarAutocompletado()

window.diagnosticarAutocompletado = function () {
    console.log('🔍 === DIAGNÓSTICO AUTOCOMPLETADO ===');

    // 1. Verificar si existe autocomplete.js
    console.log('1️⃣ Verificando autocomplete.js...');
    if (typeof AutoComplete === 'undefined') {
        console.error('❌ AutoComplete no está definido - script no cargado');
        return;
    } else {
        console.log('✅ AutoComplete está disponible');
    }

    // 2. Verificar el input
    console.log('2️⃣ Verificando input...');
    const input = document.getElementById('movimiento-articulo-info');
    if (!input) {
        console.error('❌ Input movimiento-articulo-info no encontrado');
        return;
    } else {
        console.log('✅ Input encontrado:', input);
        console.log('📋 Estado del input:', {
            value: input.value,
            type: input.type,
            id: input.id,
            classes: input.className,
            initialized: input.dataset.autocompleteInitialized
        });
    }

    // 3. Probar API directamente
    console.log('3️⃣ Probando API...');
    fetch('/inventario/api/articulos?q=a&per_page=5')
        .then(response => {
            console.log('📡 Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📊 API Data:', data);
            if (data.success && data.articulos && data.articulos.length > 0) {
                console.log('✅ API funciona correctamente con', data.articulos.length, 'artículos');

                // 4. Probar inicialización de autocompletado
                console.log('4️⃣ Probando inicialización...');
                try {
                    const autoComplete = new AutoComplete({
                        selector: '#movimiento-articulo-info',
                        minChars: 1,
                        source: function (term, suggest) {
                            console.log('🔍 Source llamado con término:', term);
                            fetch(`/inventario/api/articulos?q=${encodeURIComponent(term)}&per_page=10`)
                                .then(response => response.json())
                                .then(data => {
                                    if (data.success && data.articulos) {
                                        const suggestions = data.articulos.map(articulo => ({
                                            label: `${articulo.codigo} - ${articulo.descripcion}`,
                                            value: articulo.id
                                        }));
                                        console.log('💡 Suggestions:', suggestions);
                                        suggest(suggestions);
                                    } else {
                                        suggest([]);
                                    }
                                })
                                .catch(error => {
                                    console.error('❌ Error en source:', error);
                                    suggest([]);
                                });
                        },
                        renderItem: function (item, search) {
                            console.log('🎨 Renderizando item:', item);
                            const label = item.label || item;
                            return `<div class="autocomplete-suggestion" data-val="${item.value || item}">${label}</div>`;
                        },
                        onSelect: function (e, term, item) {
                            console.log('✅ Item seleccionado:', { term, item });
                        }
                    });
                    console.log('✅ AutoComplete inicializado correctamente');

                    // 5. Simular escritura
                    console.log('5️⃣ Simulando escritura...');
                    input.focus();
                    input.value = 'a';
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    console.log('📝 Evento de input disparado');

                } catch (error) {
                    console.error('❌ Error inicializando AutoComplete:', error);
                }
            } else {
                console.error('❌ API no devuelve datos válidos');
            }
        })
        .catch(error => {
            console.error('❌ Error en API:', error);
        });

    console.log('🏁 Diagnóstico completo');
};

// Función para limpiar y reinicializar
window.limpiarYReinicializar = function () {
    console.log('🧹 Limpiando y reinicializando...');

    const input = document.getElementById('movimiento-articulo-info');
    if (input) {
        // Limpiar atributos
        input.dataset.autocompleteInitialized = '';
        input.value = '';

        // Remover cualquier wrapper existente
        const wrapper = input.closest('.autocomplete-wrapper');
        if (wrapper) {
            console.log('🗑️ Removiendo wrapper existente');
            wrapper.parentNode.insertBefore(input, wrapper);
            wrapper.remove();
        }

        // Reinicializar
        setTimeout(() => {
            diagnosticarAutocompletado();
        }, 100);
    }
};

console.log('🛠️ Funciones de diagnóstico cargadas:');
console.log('- diagnosticarAutocompletado()');
console.log('- limpiarYReinicializar()');