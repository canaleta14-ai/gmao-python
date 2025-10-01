# Sistema de Gestión de Repuestos en Órdenes de Trabajo

## Descripción General

El sistema GMAO cuenta con un **módulo completo de gestión de repuestos** que permite controlar exactamente el inventario utilizado en cada orden de trabajo. Este módulo integra las órdenes de trabajo con el inventario para mantener un control preciso del stock.

## Funcionalidades Implementadas

### 1. Asignación de Repuestos a Órdenes

#### Interfaz de Usuario:
- **Modal de agregar repuesto** con búsqueda por código o descripción
- **Autocompletado** para facilitar la selección de artículos
- **Vista de stock actual** del artículo seleccionado
- **Información de disponibilidad** en tiempo real

#### Campos Capturados:
- Artículo/Repuesto (con autocompletado)
- Cantidad solicitada
- Cantidad utilizada (opcional, puede ser diferente de la solicitada)
- Observaciones

### 2. Visualización de Repuestos por Orden

#### Lista de Repuestos Asignados:
```
+----------------+------------------+---------------+---------------+-----------+
| Artículo       | Descripción      | Solicitado    | Utilizado     | Estado    |
+----------------+------------------+---------------+---------------+-----------+
| REP-001        | Filtro de aire   | 2             | 2             | ✅        |
| REP-015        | Rodamiento       | 4             | 3             | ✅        |
+----------------+------------------+---------------+---------------+-----------+
```

#### Información Mostrada:
- ✅ Código del artículo
- ✅ Descripción completa
- ✅ Cantidad solicitada
- ✅ Cantidad utilizada
- ✅ Stock disponible actual
- ✅ Estado del descuento (descontado/pendiente)
- ✅ Fecha de descuento (si aplica)

### 3. Descuento de Repuestos del Inventario

#### Modo Manual:
**Botón:** "Descontar del Stock"

**Flujo:**
1. Usuario hace clic en "Descontar del Stock"
2. Se muestra modal de confirmación
3. Al confirmar:
   - Se descuenta la cantidad utilizada de cada repuesto
   - Se actualiza el stock en tiempo real
   - Se crea movimiento de inventario por cada repuesto
   - Se marca el repuesto como "descontado"
   - Se registra fecha y usuario

**Validaciones:**
- ✅ Verifica stock suficiente antes de descontar
- ✅ No permite descontar repuestos ya descontados
- ✅ Muestra errores específicos si hay problemas
- ✅ Continúa con otros repuestos si uno falla

#### Modo Automático:
**Trigger:** Al completar una orden de trabajo

**Flujo:**
1. Usuario cambia estado de orden a "Completada"
2. Sistema automáticamente:
   - Descuenta todos los repuestos pendientes
   - Crea movimientos de inventario
   - Actualiza stock
   - Registra la operación

**Ventajas:**
- ⚡ Sin intervención manual
- 🎯 Garantiza que se descuenten al finalizar
- 📊 Control automático del inventario

### 4. Trazabilidad Completa

#### Movimientos de Inventario Generados:

**Información Registrada:**
```python
MovimientoInventario(
    tipo="salida",
    subtipo="orden_trabajo",
    cantidad=cantidad_utilizada,
    precio_unitario=precio_al_momento,
    valor_total=cantidad * precio,
    documento_referencia="OT-{numero_orden}",
    observaciones="Recambio utilizado en orden...",
    usuario_id=usuario_responsable,
    orden_trabajo_id=orden_id,
    fecha=fecha_descuento
)
```

#### Información de Auditoría:
- 📅 Fecha exacta del descuento
- 👤 Usuario que realizó el descuento
- 📋 Orden de trabajo asociada
- 💰 Precio unitario al momento del descuento
- 📊 Stock antes y después del descuento
- 📝 Observaciones adicionales

## Arquitectura Técnica

### Base de Datos

#### Tabla: `orden_recambio`
```sql
CREATE TABLE orden_recambio (
    id INTEGER PRIMARY KEY,
    orden_trabajo_id INTEGER NOT NULL,
    inventario_id INTEGER NOT NULL,
    cantidad_solicitada INTEGER NOT NULL,
    cantidad_utilizada INTEGER DEFAULT 0,
    precio_unitario FLOAT,
    observaciones TEXT,
    fecha_asignacion DATETIME,
    fecha_descuento DATETIME,
    descontado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (orden_trabajo_id) REFERENCES orden_trabajo(id),
    FOREIGN KEY (inventario_id) REFERENCES inventario(id)
);
```

#### Campos Clave:
- `descontado`: Flag booleano para control de descuento
- `cantidad_solicitada`: Cantidad originalmente pedida
- `cantidad_utilizada`: Cantidad realmente consumida
- `fecha_descuento`: Timestamp del descuento
- `precio_unitario`: Precio en el momento de la asignación

### Backend (Python/Flask)

#### Controlador: `orden_recambios_controller.py`

**Funciones Principales:**

1. **`agregar_recambio_a_orden()`**
   - Valida orden y artículo
   - Verifica duplicados (suma cantidades)
   - Captura precio actual del inventario

2. **`descontar_recambios_orden()`**
   - Filtra recambios no descontados
   - Valida stock disponible
   - Crea movimientos de inventario
   - Actualiza stock
   - Marca como descontado
   - Retorna detalles y errores

3. **`obtener_recambios_orden()`**
   - Lista todos los recambios de una orden
   - Incluye información del artículo
   - Estado de descuento

4. **`eliminar_recambio()`**
   - Solo permite eliminar si NO está descontado
   - Validación de seguridad

#### API Endpoints:

```python
# Agregar recambio
POST /api/ordenes/{orden_id}/recambios
Body: {
    "inventario_id": 123,
    "cantidad_solicitada": 5,
    "observaciones": "..."
}

# Listar recambios
GET /api/ordenes/{orden_id}/recambios

# Descontar del stock
POST /api/ordenes/{orden_id}/recambios/descontar
Body: {
    "usuario_id": "usuario_actual",
    "es_automatico": false
}

# Eliminar recambio
DELETE /api/recambios/{recambio_id}
```

### Frontend (JavaScript)

#### Funciones JavaScript:

```javascript
// Agregar repuesto
async function agregarRecambioOrden()

// Cargar lista de repuestos
async function cargarRecambiosOrden(ordenId)

// Descontar manualmente
async function descontarRecambios()
async function descontarRecambiosConfirmado()

// Descontar automáticamente al completar
async function descontarRecambiosAutomaticamente(ordenId)

// Eliminar repuesto
async function eliminarRecambio(recambioId)
```

## Flujo de Trabajo Completo

### Escenario 1: Descuento Manual

```mermaid
1. Técnico abre orden de trabajo
   ↓
2. Hace clic en "Agregar Recambio"
   ↓
3. Busca y selecciona artículo
   ↓
4. Ingresa cantidad solicitada
   ↓
5. Guarda (artículo agregado a lista)
   ↓
6. Repite para todos los repuestos necesarios
   ↓
7. Al terminar trabajo: clic en "Descontar del Stock"
   ↓
8. Confirma descuento
   ↓
9. Sistema descuenta y actualiza inventario
   ↓
10. Se crean movimientos de inventario
    ↓
11. Repuestos marcados como "descontados"
```

### Escenario 2: Descuento Automático

```mermaid
1. Técnico abre orden de trabajo
   ↓
2. Agrega repuestos utilizados (igual que arriba)
   ↓
3. Completa el trabajo
   ↓
4. Cambia estado a "Completada"
   ↓
5. Sistema AUTOMÁTICAMENTE:
   - Descuenta repuestos
   - Actualiza inventario
   - Crea movimientos
   ↓
6. Orden completada con inventario actualizado
```

## Ventajas del Sistema

### 1. Control Exacto del Inventario
- ✅ Stock siempre actualizado
- ✅ No hay descuadres
- ✅ Trazabilidad completa

### 2. Información en Tiempo Real
- ✅ Stock disponible visible al agregar
- ✅ Alertas de stock insuficiente
- ✅ Historial de movimientos

### 3. Costeo Preciso
- ✅ Precio capturado al momento
- ✅ Valor total calculado
- ✅ Costo real de cada orden

### 4. Auditoría Completa
- ✅ Quién desconto qué y cuándo
- ✅ Orden asociada
- ✅ Cantidad antes/después

### 5. Flexibilidad
- ✅ Modo manual o automático
- ✅ Cantidad solicitada vs utilizada
- ✅ Múltiples repuestos por orden

## Reportes Disponibles

### Por Orden de Trabajo:
- Lista de repuestos utilizados
- Costo total de repuestos
- Estado de descuento

### Por Artículo:
- Órdenes donde se utilizó
- Cantidad total consumida
- Tendencias de uso

### Movimientos de Inventario:
- Filtro por tipo "orden_trabajo"
- Reporte de consumos por período
- Valor total de repuestos

## Validaciones y Seguridad

### Validaciones Implementadas:

1. **Stock Suficiente:**
   - ❌ No permite descontar si no hay stock
   - ⚠️ Muestra error específico

2. **No Duplicar Descuentos:**
   - ❌ No permite descontar dos veces
   - ✅ Flag `descontado` previene duplicación

3. **No Eliminar Descontados:**
   - ❌ No permite eliminar repuestos ya descontados
   - 🔒 Protección de integridad de datos

4. **Orden Válida:**
   - ✅ Verifica que la orden exista
   - ✅ Valida permisos de usuario

### Manejo de Errores:

```javascript
// Respuesta con errores parciales
{
  "success": true,
  "message": "Proceso completado. 3 recambios descontados",
  "recambios_descontados": [
    {
      "articulo": "REP-001",
      "cantidad": 2,
      "stock_anterior": 50,
      "stock_actual": 48
    },
    // ...
  ],
  "errores": [
    {
      "articulo": "REP-015",
      "error": "Stock insuficiente. Disponible: 1, Requerido: 5"
    }
  ]
}
```

## Ejemplos de Uso

### Ejemplo 1: Mantenimiento Preventivo

**Orden:** Cambio de filtros de compresor
**Repuestos:**
- Filtro de aire (1 unidad)
- Filtro de aceite (1 unidad)
- Aceite lubricante (5 litros)

**Proceso:**
1. Se crea la orden
2. Se agregan los 3 repuestos
3. Técnico realiza el trabajo
4. Al completar, sistema descuenta automáticamente
5. Inventario actualizado en tiempo real

### Ejemplo 2: Mantenimiento Correctivo

**Orden:** Reparación de motor eléctrico
**Repuestos solicitados:**
- Rodamientos (4 unidades)
- Grasa (2 kg)

**Repuestos utilizados:**
- Rodamientos (3 unidades) ← Solo se usaron 3
- Grasa (1.5 kg) ← Se usó menos

**Proceso:**
1. Se agregan repuestos solicitados
2. Durante trabajo, se actualiza cantidad utilizada
3. Técnico hace clic en "Descontar del Stock"
4. Sistema descuenta solo lo utilizado (3 rod., 1.5 kg)
5. Stock refleja consumo real

## Integración con Otros Módulos

### Con Inventario:
- ✅ Actualización automática de stock
- ✅ Creación de movimientos
- ✅ Alertas de stock mínimo

### Con Órdenes de Trabajo:
- ✅ Lista de repuestos por orden
- ✅ Costo total de la orden
- ✅ Estado de completitud

### Con Contabilidad:
- ✅ Movimientos contables por cuenta
- ✅ Centro de costo de la orden
- ✅ Valorización del consumo

## Configuración y Personalización

### Modos de Descuento:

**1. Solo Manual:**
```javascript
// En ordenes.js, línea ~358
// Comentar línea de descuento automático:
// await descontarRecambiosAutomaticamente(ordenId);
```

**2. Solo Automático:**
```html
<!-- En ordenes.html -->
<!-- Ocultar botón manual -->
<button style="display: none" onclick="descontarRecambios()">
```

**3. Ambos (Actual):**
- Botón manual visible
- Descuento automático al completar
- Máxima flexibilidad

### Permisos:

Se pueden implementar restricciones por rol:
```python
# Ejemplo en el route
@login_required
@require_role(['admin', 'tecnico'])
def descontar_recambios(orden_id):
```

## Mantenimiento y Soporte

### Logs y Auditoría:

Todo descuento genera:
1. Movimiento en `movimiento_inventario`
2. Actualización de `orden_recambio.descontado`
3. Timestamp en `orden_recambio.fecha_descuento`
4. Usuario en `movimiento_inventario.usuario_id`

### Consultas SQL Útiles:

```sql
-- Repuestos descontados hoy
SELECT or.*, i.codigo, i.descripcion, ot.numero_orden
FROM orden_recambio or
JOIN inventario i ON or.inventario_id = i.id
JOIN orden_trabajo ot ON or.orden_trabajo_id = ot.id
WHERE DATE(or.fecha_descuento) = CURRENT_DATE;

-- Stock consumido por orden
SELECT ot.numero_orden, 
       SUM(or.cantidad_utilizada * or.precio_unitario) as costo_total
FROM orden_trabajo ot
JOIN orden_recambio or ON ot.id = or.orden_trabajo_id
WHERE or.descontado = TRUE
GROUP BY ot.numero_orden;

-- Órdenes con repuestos pendientes
SELECT ot.numero_orden, COUNT(or.id) as repuestos_pendientes
FROM orden_trabajo ot
JOIN orden_recambio or ON ot.id = or.orden_trabajo_id
WHERE or.descontado = FALSE
GROUP BY ot.numero_orden;
```

## Conclusión

El sistema de gestión de repuestos en órdenes de trabajo proporciona:

✅ **Control exacto** del inventario utilizado  
✅ **Trazabilidad completa** de movimientos  
✅ **Flexibilidad** en modos de operación  
✅ **Integración** con otros módulos  
✅ **Auditoría** completa de operaciones  
✅ **Validaciones** robustas  
✅ **Interfaz intuitiva** para usuarios  

El sistema está **completamente funcional** y listo para uso en producción. 🚀

---

**Última actualización:** 1 de octubre de 2025  
**Versión del sistema:** 1.0  
**Estado:** ✅ Operacional
