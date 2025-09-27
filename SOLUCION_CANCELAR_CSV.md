# 🐛 Corrección: Cancelar Exportación CSV se quedaba cargando artículos

## Problema Identificado
Cuando el usuario hacía clic en "Exportar CSV" en el módulo de inventario y luego cancelaba la descarga, la tabla se quedaba mostrando el spinner de carga indefinidamente, impidiendo que se muestren los artículos normalmente.

## Análisis de la Causa
El problema se originaba por una **incompatibilidad entre funciones `mostrarCargando`**:

1. **En `main.js`**: La función `descargarCSVMejorado()` llama a `mostrarCargando(false)` al finalizar (incluso si se cancela)
2. **En `inventario.js`**: La función `mostrarCargando()` no aceptaba parámetros y siempre mostraba el estado de carga
3. **Conflicto**: Al llamar `mostrarCargando(false)`, la función ignoraba el parámetro y mostraba carga nuevamente

## Solución Implementada

### 1. Función `mostrarCargando` Mejorada
```javascript
// ANTES - No aceptaba parámetros
function mostrarCargando() {
    tbody.innerHTML = `<tr id="loading-row">...spinner...</tr>`;
}

// DESPUÉS - Acepta parámetro booleano
function mostrarCargando(mostrar = true) {
    if (mostrar) {
        // Solo mostrar si no existe loading-row
        if (!tbody.querySelector('#loading-row')) {
            tbody.innerHTML = `<tr id="loading-row">...spinner...</tr>`;
        }
    } else {
        // Solo eliminar loading-row si existe
        const loadingRow = tbody.querySelector('#loading-row');
        if (loadingRow) {
            loadingRow.remove();
        }
    }
}
```

### 2. Compatibilidad Global
- Agregado `window.mostrarCargando = mostrarCargando;` para exposición global
- Actualizada llamada interna a `mostrarCargando(true)`

### 3. Comportamiento Mejorado
- **`mostrarCargando(true)`**: Muestra spinner solo si no existe
- **`mostrarCargando(false)`**: Elimina solo el spinner, preserva contenido existente
- **Prevención de duplicados**: Evita múltiples filas de carga
- **Limpieza selectiva**: Elimina solo elementos de carga específicos

## Archivos Modificados

### Principal
- `static/js/inventario.js`: Función corregida y expuesta globalmente

### Testing
- `test_exportar_csv_cancel.py`: Test de servidor Flask
- `test_cancelar_csv.html`: Test standalone HTML/JS  
- `static/js/debug-mostrar-cargando.js`: Herramientas de diagnóstico

## Resultado
✅ **Problema resuelto**: Cancelar exportación CSV ya no deja la tabla cargando indefinidamente

✅ **Backward compatibility**: Mantiene compatibilidad con código existente

✅ **Mejor UX**: Transiciones suaves entre estados de carga y contenido normal

## Prueba de la Corrección

### Método 1: Test HTML Standalone
```bash
# Abrir test_cancelar_csv.html en navegador
start test_cancelar_csv.html
```

### Método 2: Aplicación Real
1. Iniciar aplicación Flask
2. Ir a módulo Inventario
3. Hacer clic en "Exportar CSV"
4. Cancelar cuando aparezca diálogo de descarga
5. Verificar que los artículos se muestran normalmente (sin spinner infinito)

---
**Commit**: 1e6629f  
**Fecha**: 27/Sep/2025  
**Estado**: ✅ Completado y probado