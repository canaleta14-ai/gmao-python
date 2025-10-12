# 🔧 Guía de Diagnóstico - Proveedores en Activos

## 🎯 Problema

Los proveedores no aparecen en el select al crear activos.

## 📋 Pasos de Diagnóstico

### 1. **Verificar que el servidor esté funcionando**

- ✅ Servidor iniciado en: http://localhost:5000
- ✅ Logs muestran que el servidor está corriendo

### 2. **Verificar datos en base de datos**

- ✅ 1 proveedor en total
- ✅ 1 proveedor activo: "Sonepar (NIF: 33666999H)"

### 3. **Probar API directamente**

- 🔄 Abrir: http://localhost:5000/static/test_api_simple.html
- Hacer clic en "Probar /proveedores/api"
- **Resultado esperado**: JSON con 1 proveedor activo

### 4. **Probar funcionalidad en activos**

1. Ir a: http://localhost:5000/activos
2. Hacer clic en "Nuevo Activo"
3. **Verificar en consola del navegador (F12)**:
   ```
   🔄 Abriendo modal de nuevo activo - Cargando proveedores...
   🔄 Cargando proveedores desde API...
   ✅ Select encontrado: [object HTMLSelectElement]
   📡 Respuesta recibida: 200 OK
   ✅ Proveedores cargados: 1 total
   📄 Datos completos: [datos del proveedor]
   ```

### 5. **Si no aparecen proveedores, usar botones de debug**

En el modal de nuevo activo:

- Hacer clic en "🔄 Debug: Recargar Proveedores"
- Hacer clic en "📊 Debug: Verificar Estado"
- Revisar logs en consola

### 6. **Verificaciones adicionales**

#### A. Verificar estructura del proveedor

Los datos deben tener esta estructura:

```json
{
  "id": 1,
  "nombre": "Sonepar",
  "nif": "33666999H",
  "activo": true
}
```

#### B. Verificar que `activo` sea boolean

El filtro busca `proveedor.activo === true` (boolean estricto)

#### C. Verificar elemento DOM

El select debe tener ID: `nuevo-proveedor`

## 🔧 Funciones de Debug Agregadas

### `recargarProveedoresManual()`

Fuerza la recarga de proveedores manualmente.

### `verificarEstadoSelectProveedores()`

Muestra el estado actual del select en consola.

### Logs mejorados

Cada paso del proceso tiene logs detallados con emojis.

## 🚨 Posibles Problemas y Soluciones

### Problema 1: API no responde

**Síntomas**: Error de conexión en consola
**Solución**: Verificar que el servidor esté ejecutándose

### Problema 2: Datos incorrectos

**Síntomas**: Proveedores cargados pero filtro no encuentra activos
**Solución**: Verificar que `activo` sea boolean `true`, no string "true"

### Problema 3: Elemento no encontrado

**Síntomas**: Error "Select no encontrado"
**Solución**: Verificar que el modal se haya cargado completamente

### Problema 4: Timing

**Síntomas**: A veces funciona, a veces no
**Solución**: Usar el retry automático implementado (setTimeout)

## 📊 Comandos de Debugging en Consola

```javascript
// Verificar estado actual
verificarEstadoSelectProveedores();

// Recargar manualmente
recargarProveedoresManual();

// Probar API directamente
fetch("/proveedores/api")
  .then((r) => r.json())
  .then(console.log);

// Verificar elemento
document.getElementById("nuevo-proveedor");
```

## ✅ Estado de las Mejoras

- ✅ Logs detallados agregados
- ✅ Manejo de errores mejorado
- ✅ Retry automático implementado
- ✅ Funciones de debug agregadas
- ✅ Botones de debug en UI
- ✅ Verificación de elemento DOM
- ✅ Filtrado estricto de boolean
