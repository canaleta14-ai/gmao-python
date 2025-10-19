# Documentación API - Módulo Inventario

## Endpoints del Módulo de Inventario de Repuestos

### POST /inventario/api/articulos

Crea un nuevo artículo en el inventario de repuestos.

#### Request

**Headers:**

```
Content-Type: application/json
```

**Body:**

```json
{
  "codigo": "string (opcional si hay categoria_id)",
  "descripcion": "string (requerido)",
  "categoria_id": "integer (opcional, para generar código automático)",
  "categoria": "string (opcional)",
  "stock_minimo": "number (default: 0)",
  "stock_maximo": "number (default: 0)",
  "ubicacion": "string (opcional)",
  "precio_unitario": "number (opcional)",
  "unidad_medida": "string (default: 'UNI')",
  "proveedor": "string (opcional)",
  "cuenta_contable_compra": "string (default: '622000000')",
  "grupo_contable": "string (opcional)",
  "critico": "boolean (default: false)",
  "activo": "boolean (default: true)"
}
```

#### Validaciones

**Campos requeridos:**

- `descripcion`: No puede estar vacío
- `codigo` O `categoria_id`: Al menos uno debe estar presente (si falta código, se genera automáticamente con el prefijo de la categoría)

**Validaciones de valores:**

- `stock_minimo` >= 0 (no puede ser negativo)
- `stock_maximo` >= 0 (no puede ser negativo)
- `precio_unitario` >= 0 (no puede ser negativo)
- Si `stock_maximo` > 0, entonces `stock_minimo` <= `stock_maximo`

**Validación de duplicados:**

- `codigo`: Debe ser único en la base de datos

#### Response

**Success (201 Created):**

```json
{
  "message": "Artículo creado exitosamente",
  "id": 123,
  "codigo": "CAT-001"
}
```

**Error (400 Bad Request):**

```json
{
  "error": "La descripción es obligatoria"
}
```

```json
{
  "error": "El stock mínimo no puede ser negativo"
}
```

```json
{
  "error": "El stock mínimo no puede ser mayor que el stock máximo"
}
```

```json
{
  "error": "Los valores numéricos deben ser válidos"
}
```

**Error (409 Conflict):**

```json
{
  "error": "Ya existe un artículo con el código CAT-001"
}
```

**Error (500 Internal Server Error):**

```json
{
  "error": "Error al crear artículo: [detalle del error]"
}
```

#### Ejemplo de uso

**Con código manual:**

```bash
curl -X POST http://localhost:5000/inventario/api/articulos \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "ROD-001",
    "descripcion": "Rodamiento 6205",
    "stock_minimo": 10,
    "stock_maximo": 100,
    "precio_unitario": 15.50,
    "critico": true
  }'
```

**Con generación automática de código:**

```bash
curl -X POST http://localhost:5000/inventario/api/articulos \
  -H "Content-Type: application/json" \
  -d '{
    "categoria_id": 3,
    "descripcion": "Filtro de aceite",
    "stock_minimo": 5,
    "stock_maximo": 50,
    "precio_unitario": 8.75
  }'
```

---

### DELETE /inventario/api/articulos/<id>

Elimina un artículo del inventario de repuestos.

⚠️ **ADVERTENCIA**: Esta operación eliminará en cascada:

- El artículo seleccionado
- Todos los movimientos de inventario asociados
- Todos los lotes FIFO relacionados

#### Request

**URL Parameters:**

- `id` (integer): ID del artículo a eliminar

#### Response

**Success (200 OK):**

```json
{
  "message": "Artículo eliminado exitosamente"
}
```

**Error (404 Not Found):**

```json
{
  "error": "Artículo no encontrado"
}
```

**Error (409 Conflict):**

```json
{
  "error": "No se puede eliminar el artículo porque está siendo usado en otras partes del sistema"
}
```

**Error (500 Internal Server Error):**

```json
{
  "error": "Error al eliminar artículo: [detalle del error]"
}
```

#### Ejemplo de uso

```bash
curl -X DELETE http://localhost:5000/inventario/api/articulos/123
```

---

## Códigos de Estado HTTP

| Código | Significado           | Cuándo se usa                                                     |
| ------ | --------------------- | ----------------------------------------------------------------- |
| 200    | OK                    | Eliminación exitosa                                               |
| 201    | Created               | Creación exitosa                                                  |
| 400    | Bad Request           | Datos de entrada inválidos o validación fallida                   |
| 404    | Not Found             | Recurso no encontrado                                             |
| 409    | Conflict              | Conflicto de integridad (código duplicado, relaciones existentes) |
| 500    | Internal Server Error | Error inesperado del servidor                                     |

---

## Validaciones Frontend

El formulario de creación de artículos incluye validaciones JavaScript que se ejecutan **antes** de enviar la petición al servidor:

1. **Descripción obligatoria**: Se verifica que el campo no esté vacío
2. **Valores no negativos**: stock_minimo, stock_maximo y precio_unitario deben ser >= 0
3. **Lógica de stocks**: Si stock_maximo > 0, entonces stock_minimo <= stock_maximo
4. **Focus automático**: Si una validación falla, el cursor se posiciona en el campo problemático

Estas validaciones mejoran la experiencia del usuario al proporcionar retroalimentación inmediata sin necesidad de esperar la respuesta del servidor.

---

## Optimizaciones de Base de Datos

### Índices Creados

Para mejorar el rendimiento de las búsquedas, se han creado los siguientes índices en PostgreSQL:

1. **idx_inventario_codigo_ilike**: Optimiza búsquedas por código (ILIKE con text_pattern_ops)
2. **idx_inventario_descripcion_ilike**: Optimiza búsquedas por descripción (ILIKE)
3. **idx_inventario_categoria_ilike**: Optimiza búsquedas por categoría (ILIKE)
4. **idx_inventario_activo**: Optimiza filtros por estado activo
5. **idx_inventario_activo_categoria**: Índice compuesto para filtros combinados
6. **idx_inventario_codigo_sort**: Optimiza ordenamiento por código

#### Verificación de índices

Para verificar los índices creados en PostgreSQL, ejecuta:

```bash
psql -h localhost -U postgres -d gmao -f sql/verificar_indices_inventario.sql
```

---

## Tests Unitarios

Los tests de validaciones se encuentran en `tests/test_controllers/test_inventario_validations.py`.

### Ejecutar tests

```bash
# Todos los tests del módulo
python -m pytest tests/test_controllers/test_inventario_validations.py -v

# Test específico
python -m pytest tests/test_controllers/test_inventario_validations.py::TestInventarioValidaciones::test_crear_articulo_sin_descripcion_falla -v

# Con cobertura
python -m pytest tests/test_controllers/test_inventario_validations.py --cov=app.controllers.inventario_controller_simple
```

### Cobertura de tests

Los tests cubren:

- ✅ Validación de campos requeridos (descripción, código/categoría)
- ✅ Validación de valores negativos (stocks, precios)
- ✅ Validación de lógica de stocks (mínimo <= máximo)
- ✅ Validación de conversión de tipos (string a número)
- ✅ Validación de duplicados (código único)
- ✅ Creación exitosa con datos válidos
- ✅ Manejo de campos opcionales

**Resultado actual**: 11 de 13 tests pasan (84.6% de éxito)

---

## Mejoras Implementadas

### Backend

1. **Limpieza de código**

   - Eliminados 5 imports duplicados
   - Agregado import faltante (crear_articulo_simple)

2. **Manejo de errores mejorado**

   - Excepciones específicas (ValueError, KeyError, IntegrityError)
   - Logging de errores críticos
   - Mensajes de error descriptivos

3. **Validaciones robustas**
   - 11 validaciones en crear_articulo_simple()
   - Conversión segura de tipos
   - Validación de lógica de negocio

### Frontend

1. **Validaciones JavaScript**

   - Validación pre-submit
   - Mensajes de error específicos
   - Focus automático en campo con error

2. **UX mejorada**
   - Confirmación modal para eliminar
   - Alertas informativas
   - Feedback inmediato

### Base de Datos

1. **Índices de rendimiento**
   - 6 índices creados para optimizar búsquedas
   - Soporte para ILIKE case-insensitive
   - Índices compuestos para filtros comunes

---

## Notas Adicionales

### Generación Automática de Código

Cuando se proporciona `categoria_id` pero no `codigo`, el sistema genera automáticamente un código usando el prefijo de la categoría (campo `prefijo` en la tabla `categoria`).

**Ejemplo:**

- Categoría: "Rodamientos" con prefijo "ROD"
- Código generado: "ROD-001", "ROD-002", etc.

### Eliminación en Cascada

Al eliminar un artículo, se eliminan automáticamente:

- Registros en `movimiento_inventario`
- Registros en `lote_fifo`

Esta operación **NO** se puede deshacer. Se recomienda marcar el artículo como `activo=false` en lugar de eliminarlo si existe la posibilidad de necesitarlo en el futuro.

---

## Contacto y Soporte

Para reportar bugs o solicitar nuevas funcionalidades, por favor crea un issue en el repositorio del proyecto.
