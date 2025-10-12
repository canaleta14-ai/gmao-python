# Test de Proveedores API - Diagnóstico

## Problema Reportado

El select de proveedores no funciona en producción pero sí en local.

## Cambios Realizados para Debug

### 1. Cache Busting en activos.html

```html
<script src="{{ url_for('static', filename='js/activos.js') }}?v=20251012_proveedores_fix"></script>
```

### 2. Logging Mejorado en activos.js

- Prefijos `[ACTIVOS]` para identificar logs
- Verificación de estructura de datos
- Debug de estado de proveedores (activo/inactivo)
- Headers de respuesta HTTP

### 3. Verificación de Datos

- Validación de array de proveedores
- Debug individual de cada proveedor
- Información sobre tipos de datos

## Comandos de Verificación Local

```bash
# 1. Verificar que hay proveedores activos
python -c "
from app.factory import create_app
from app.controllers.proveedores_controller import listar_proveedores
app = create_app()
with app.app_context():
    proveedores = listar_proveedores()
    print('Total proveedores:', len(proveedores))
    activos = [p for p in proveedores if p.get('activo', False)]
    print('Proveedores activos:', len(activos))
    for p in activos[:3]:
        print('  -', p.get('nombre'), '(activo:', p.get('activo'), ')')
"

# 2. Verificar endpoint API
curl http://localhost:5000/proveedores/api
```

## Debug en Producción

1. **Abrir Consola del Navegador** en la página de activos
2. **Intentar crear un nuevo activo** para activar la carga de proveedores
3. **Revisar logs** que aparecen con prefijo `[ACTIVOS]`
4. **Verificar** si aparecen errores de red o datos

## Posibles Causas del Problema

### En Producción:

1. **Cache del navegador** no actualizado
2. **CDN/Proxy cache** sirviendo versión antigua
3. **Error en el API** de proveedores (permisos, DB)
4. **JavaScript bundle** no actualizado

### Soluciones Aplicadas:

- ✅ **Cache busting** con versión timestamp
- ✅ **Logging detallado** para identificar el punto de fallo
- ✅ **Validación robusta** de datos

## Próximos Pasos

1. **Deploy** de estos cambios
2. **Probar en producción** con console abierta
3. **Verificar logs** para identificar el problema exacto
4. **Implementar fix** específico basado en los logs

## Fallback de Emergencia

Si el problema persiste, se puede implementar:

```javascript
// Cargar proveedores con datos hardcodeados temporales
if (proveedoresActivos.length === 0) {
  console.warn("🚨 FALLBACK: Usando proveedores de emergencia");
  // Cargar desde cache local o datos por defecto
}
```
