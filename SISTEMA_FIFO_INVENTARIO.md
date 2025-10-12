# Sistema FIFO para Inventario

## Descripción General

El sistema FIFO (First In, First Out) implementado permite el control detallado de lotes de inventario, asegurando que los artículos que entraron primero sean los primeros en salir. Esto es especialmente importante para:

- **Artículos perecederos** con fecha de vencimiento
- **Control de costos** más preciso usando precios específicos de cada lote
- **Trazabilidad completa** de origen y movimientos de cada artículo
- **Cumplimiento normativo** que requiere seguimiento de lotes

## Componentes Principales

### 1. Modelo `LoteInventario`

Cada entrada de stock crea un nuevo lote con:

- **Fecha de entrada**: Para determinar el orden FIFO
- **Cantidad inicial y actual**: Control de stock por lote
- **Precio unitario específico**: Costo real de cada lote
- **Trazabilidad**: Documento origen, proveedor, etc.
- **Fecha de vencimiento**: Para artículos con caducidad

### 2. Modelo `MovimientoLote`

Registra todos los movimientos de cada lote:

- **Consumos**: Salidas de stock siguiendo FIFO
- **Reservas**: Apartado de stock para órdenes específicas
- **Liberaciones**: Cancelación de reservas
- **Trazabilidad completa**: Vinculación con órdenes de trabajo

### 3. Servicio `ServicioFIFO`

Lógica de negocio centralizada para:

- Crear lotes automáticamente en entradas
- Consumir stock siguiendo orden FIFO
- Gestionar reservas y liberaciones
- Integración con sistema de movimientos existente

## Flujo de Operaciones

### Entrada de Stock (Creación de Lotes)

```python
# Al recibir mercancía
lote = ServicioFIFO.crear_lote_entrada(
    inventario_id=123,
    cantidad=100,
    precio_unitario=10.50,
    codigo_lote="LOTE-2025-001",
    documento_origen="FAC-00123",
    proveedor_id=456
)
```

### Consumo FIFO

```python
# Al usar artículos en una orden
consumos, faltante = ServicioFIFO.consumir_fifo(
    inventario_id=123,
    cantidad_total=75,
    orden_trabajo_id=789,
    documento_referencia="OT-2025-001"
)

# Resultado: se consumen primero los lotes más antiguos
# consumos = [(lote_viejo, 50), (lote_medio, 25)]
# faltante = 0 (si hay suficiente stock)
```

### Reservas de Stock

```python
# Reservar para una orden futura
reservas, faltante = ServicioFIFO.reservar_stock(
    inventario_id=123,
    cantidad_total=30,
    orden_trabajo_id=790
)

# Liberar si se cancela la orden
liberaciones = ServicioFIFO.liberar_reservas(
    orden_trabajo_id=790
)
```

## Algoritmo FIFO

### Lógica de Selección de Lotes

1. **Ordenar lotes** por fecha de entrada (más antiguos primero)
2. **Filtrar lotes activos** con stock disponible > 0
3. **Iterar secuencialmente** hasta completar la cantidad solicitada
4. **Registrar movimientos** en cada lote afectado

### Ejemplo Práctico

**Estado inicial:**

```
Lote A: 100 uds (entrada: 2025-01-01) - Precio: $8.00
Lote B: 150 uds (entrada: 2025-01-15) - Precio: $9.00
Lote C: 200 uds (entrada: 2025-02-01) - Precio: $10.00
```

**Consumo de 220 unidades:**

```
1. Lote A: consume 100 uds completas (queda 0)
2. Lote B: consume 120 uds (queda 30)
3. Lote C: no se toca (queda 200)
```

**Resultado:**

- Costo promedio ponderado: (100×$8.00 + 120×$9.00) ÷ 220 = $8.55
- Trazabilidad: 100 uds de FAC-001, 120 uds de FAC-002

## Beneficios del Sistema

### 1. Control de Costos Preciso

- Cálculo exacto del costo de bienes vendidos (COGS)
- Valoración de inventario por lotes específicos
- Análisis de márgenes por lote de compra

### 2. Gestión de Caducidad

- Alertas de vencimiento próximo
- Consumo automático de productos próximos a vencer
- Reducción de desperdicio por caducidad

### 3. Trazabilidad Completa

- Seguimiento desde proveedor hasta consumo final
- Facilita recalls de productos defectuosos
- Auditorías y cumplimiento normativo

### 4. Optimización de Stock

- Identificación de lotes de rotación lenta
- Prevención de acumulación de stock obsoleto
- Mejores decisiones de compra

## Integración con Sistema Existente

### Compatibilidad Backward

El sistema mantiene compatibilidad con:

- Modelos de `Inventario` existentes
- `MovimientoInventario` tradicionales
- Interfaces de usuario actuales

### Migración Gradual

1. **Fase 1**: Instalar nuevos modelos y servicios
2. **Fase 2**: Crear lotes para nuevas entradas
3. **Fase 3**: Convertir stock existente a lotes
4. **Fase 4**: Activar FIFO para todos los consumos

### Configuración por Artículo

Algunos artículos pueden requerir FIFO obligatorio:

- Medicamentos y productos químicos
- Alimentos y productos perecederos
- Artículos con lotes de fabricación específicos

Otros pueden usar agregación simple:

- Tornillos, pernos y materiales básicos
- Artículos de muy alta rotación
- Productos sin fecha de vencimiento

## Reportes y Consultas

### Stock por Lotes

```python
stock_info = ServicioFIFO.obtener_stock_disponible(inventario_id)
# Retorna información detallada de todos los lotes
```

### Trazabilidad de Consumos

```sql
SELECT
    l.codigo_lote,
    l.fecha_entrada,
    ml.fecha as fecha_consumo,
    ml.cantidad,
    ot.numero as orden_trabajo
FROM movimiento_lote ml
JOIN lote_inventario l ON ml.lote_id = l.id
JOIN orden_trabajo ot ON ml.orden_trabajo_id = ot.id
WHERE l.inventario_id = ?
ORDER BY ml.fecha DESC
```

### Análisis de Rotación

```sql
SELECT
    i.codigo,
    i.nombre,
    AVG(EXTRACT(DAY FROM ml.fecha - l.fecha_entrada)) as dias_promedio_rotacion
FROM inventario i
JOIN lote_inventario l ON i.id = l.inventario_id
JOIN movimiento_lote ml ON l.id = ml.lote_id
WHERE ml.tipo_movimiento = 'consumo'
GROUP BY i.id, i.codigo, i.nombre
ORDER BY dias_promedio_rotacion DESC
```

## Consideraciones de Rendimiento

### Índices Optimizados

- `(inventario_id, fecha_entrada)` para consultas FIFO
- `(inventario_id, activo, cantidad_actual)` para stock disponible
- `(orden_trabajo_id)` para operaciones de reserva

### Archivado de Lotes Agotados

- Lotes con cantidad_actual = 0 pueden marcarse como inactivos
- Mantener por período legal requerido
- Proceso de archivado automático

## Implementación Recomendada

### 1. Artículos Críticos Primero

Implementar FIFO inicialmente en:

- Medicamentos y productos químicos
- Repuestos costosos con fecha de fabricación
- Artículos con trazabilidad regulatoria requerida

### 2. Capacitación de Usuarios

- Explicar conceptos de lotes y FIFO
- Entrenar en verificación de fechas de vencimiento
- Procedimientos para manejo de productos vencidos

### 3. Monitoreo Continuo

- Alertas de productos próximos a vencer
- Reportes de rotación de inventario
- Análisis de eficiencia del sistema FIFO

## Próximos Pasos

1. **Ejecutar migración** para crear tablas de lotes
2. **Probar sistema** con artículos de prueba
3. **Configurar alertas** de vencimiento
4. **Capacitar usuarios** en nuevos procesos
5. **Migrar datos** existentes gradualmente
6. **Implementar reportes** específicos de FIFO
