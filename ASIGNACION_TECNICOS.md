# 🔧 Asignación Masiva de Técnicos a Órdenes

## Problema Identificado

**Diagnóstico**: Las órdenes de trabajo en producción **NO tienen técnicos asignados** (`tecnico_id = NULL`).

```
🔍 DEBUG Órdenes - Primera orden: ID=1, Técnico ID=None, Técnico Nombre=None
```

Esto causa que la columna "Técnico" aparezca vacía en la lista de órdenes, aunque el código del frontend y backend funciona correctamente.

---

## Solución Implementada

Se ha creado una **herramienta de administración** para asignar técnicos automáticamente a todas las órdenes que no tienen técnico asignado.

### Características:

- ✅ **Balanceo de carga automático**: Asigna técnicos equitativamente según su carga de trabajo actual
- ✅ **Solo para administradores**: Requiere permisos de administrador
- ✅ **Proceso masivo**: Asigna técnicos a todas las órdenes sin técnico en una sola operación
- ✅ **Seguro**: Incluye validaciones y rollback en caso de error

---

## Cómo Usar

### Opción 1: Página de Administración (Recomendada)

1. **Accede a la página de administración**:
   ```
   https://gmao-sistema-2025.ew.r.appspot.com/admin/asignar-tecnicos-page
   ```

2. **Haz clic en el botón**: "Asignar Técnicos Automáticamente"

3. **Espera la confirmación**: Verás un mensaje con:
   - Número de órdenes procesadas
   - Detalles de las asignaciones (primeras 10)
   - Estado de éxito o error

### Opción 2: API Directa (Para scripts)

```bash
# POST request al endpoint
curl -X POST https://gmao-sistema-2025.ew.r.appspot.com/admin/asignar-tecnicos \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -H "Content-Type: application/json"
```

**Respuesta exitosa**:
```json
{
  "success": true,
  "message": "Se asignaron técnicos a 15 órdenes",
  "asignadas": 15,
  "detalles": [
    {
      "orden_id": 1,
      "numero_orden": "OT-001",
      "tecnico": "Juan Pérez"
    },
    ...
  ]
}
```

---

## Algoritmo de Asignación

El sistema usa el **mismo algoritmo de balanceo de carga** que se utiliza al generar órdenes desde planes:

1. Obtiene todos los técnicos activos
2. Cuenta las órdenes pendientes/en proceso de cada técnico
3. Asigna la orden al técnico con **menor carga de trabajo**
4. Repite el proceso para cada orden sin técnico

Esto garantiza una **distribución equitativa** del trabajo entre todos los técnicos.

---

## Requisitos de Seguridad

- 🔒 **Solo administradores** pueden ejecutar esta acción
- 🔒 Requiere autenticación activa (sesión válida)
- 🔒 Validación de rol en backend y frontend

**Intentar acceder sin permisos resultará en**:
```json
{
  "error": "Acceso denegado. Solo administradores."
}
```

---

## Verificación Post-Asignación

Después de ejecutar la asignación:

1. **Ve a la lista de órdenes**: `/ordenes/`
2. **Verifica la columna "Técnico"**: Debe mostrar el nombre del técnico asignado
3. **Revisa órdenes individuales**: Edita una orden para confirmar que el técnico aparece en el formulario

---

## Archivos Involucrados

### Backend

- **`app/routes/web.py`**:
  - Endpoint POST: `/admin/asignar-tecnicos`
  - Endpoint GET: `/admin/asignar-tecnicos-page`

- **`app/controllers/ordenes_controller.py`**:
  - Ya retorna correctamente `tecnico_nombre` en la API

### Frontend

- **`app/templates/admin/asignar-tecnicos.html`**: Interfaz de administración
- **`static/js/ordenes.js`**: Renderiza técnicos correctamente

---

## Logs de Debug (Ya removidos)

Se agregaron temporalmente logs de debug para diagnosticar el problema:

```python
# ❌ REMOVIDO - Ya no necesario
print(f"🔍 DEBUG Órdenes - Primera orden: ID={ordenes_data[0]['id']}, "
      f"Técnico ID={ordenes_data[0]['tecnico_id']}, "
      f"Técnico Nombre={ordenes_data[0]['tecnico_nombre']}")
```

Los logs confirmaron que `tecnico_id = None` en la base de datos de producción.

---

## Próximos Pasos

1. ✅ **Ejecutar la asignación masiva** usando la herramienta
2. ✅ **Verificar resultados** en la lista de órdenes
3. ✅ **Configurar proceso automático** (opcional): 
   - Asignar técnicos automáticamente al crear nuevas órdenes
   - Ya implementado en generación desde planes

---

## Soporte Técnico

**Si encuentras problemas**:

1. Verifica que tienes rol de **administrador**
2. Verifica que hay **técnicos activos** en el sistema
3. Revisa los logs de App Engine: `gcloud app logs tail`
4. Contacta al equipo de desarrollo con el mensaje de error

---

## Historial de Cambios

- **2025-10-02**: Diagnóstico inicial con logs de debug
- **2025-10-02**: Implementación de endpoint de asignación masiva
- **2025-10-02**: Creación de interfaz de administración
- **2025-10-02**: Despliegue a producción
- **2025-10-02**: Remoción de logs de debug
