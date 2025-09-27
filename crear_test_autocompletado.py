"""
Test simple del autocompletado de recambios
"""


def crear_test_html():
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Autocompletado Recambios</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="http://127.0.0.1:5000/static/js/autocomplete.js"></script>
</head>
<body>
    <div class="container mt-5">
        <h3>Test Autocompletado de Recambios</h3>
        
        <div class="mb-3">
            <label for="test-articulo" class="form-label">Artículo/Repuesto</label>
            <input type="text" class="form-control" id="test-articulo" placeholder="Buscar artículo...">
            <input type="hidden" id="test-inventario-id">
        </div>
        
        <div class="mb-3">
            <label class="form-label">Stock Actual</label>
            <input type="text" class="form-control" id="test-stock" readonly>
        </div>
        
        <div id="test-info" class="mt-3">
            Información del artículo seleccionado aparecerá aquí
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Inicializando test...');
            
            if (typeof AutoComplete === 'undefined') {
                console.error('AutoComplete no está disponible');
                return;
            }
            
            const autoComplete = new AutoComplete({
                selector: '#test-articulo',
                placeHolder: 'Buscar artículo...',
                threshold: 2,
                data: {
                    src: async (query) => {
                        console.log('Buscando:', query);
                        try {
                            const response = await fetch(`http://127.0.0.1:5000/inventario/api/articulos?q=\${encodeURIComponent(query)}&activo=true`);
                            const data = await response.json();
                            console.log('Respuesta:', data);
                            
                            if (data.articulos) {
                                return data.articulos;
                            }
                            return [];
                        } catch (error) {
                            console.error('Error:', error);
                            return [];
                        }
                    },
                    keys: ['codigo', 'descripcion']
                },
                onSelection: (feedback) => {
                    const selection = feedback.selection.value;
                    console.log('Seleccionado:', selection);
                    
                    document.getElementById('test-articulo').value = `\${selection.codigo} - \${selection.descripcion}`;
                    document.getElementById('test-inventario-id').value = selection.id;
                    document.getElementById('test-stock').value = selection.stock_actual || 0;
                    
                    document.getElementById('test-info').innerHTML = `
                        <strong>\${selection.codigo}</strong> - \${selection.descripcion}<br>
                        Stock: \${selection.stock_actual || 0}<br>
                        Precio: $\${(selection.precio_promedio || 0).toFixed(2)}
                    `;
                }
            });
            
            console.log('AutoComplete inicializado');
        });
    </script>
</body>
</html>
    """

    with open("test_autocompletado_recambios.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ Archivo test_autocompletado_recambios.html creado")
    print("📋 Abre este archivo en el navegador para probar el autocompletado")


if __name__ == "__main__":
    crear_test_html()
