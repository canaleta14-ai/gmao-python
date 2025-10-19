# 🎯 Funcionalidades de Control de Vencimientos

## 📋 Resumen de Implementación

Se han añadido **3 funcionalidades principales** al módulo de Control de Vencimientos del sistema FIFO:

---

## ✅ 1. API para Obtener Lote Individual

### 📍 Endpoint

```
GET /lotes/api/lote/<lote_id>
```

### 🎯 Función

Obtiene información completa de un lote específico, incluyendo estado de vencimiento y días restantes.

### 📊 Respuesta

```json
{
  "success": true,
  "lote": {
    "id": 1,
    "codigo_lote": "LOTE-2024-001",
    "inventario_codigo": "ART-001",
    "inventario_nombre": "Tornillo M8x20",
    "cantidad_actual": 150.0,
    "cantidad_reservada": 20.0,
    "unidad_medida": "UN",
    "precio_unitario": 0.25,
    "valor_total": 37.5,
    "fecha_entrada": "2024-01-15T10:30:00",
    "fecha_vencimiento": "2025-10-25T00:00:00",
    "dias_hasta_vencimiento": 6,
    "estado_vencimiento": "critico",
    "ubicacion": "Almacén A - Estantería 3",
    "proveedor": "Proveedor SA",
    "observaciones": "Lote prioritario"
  }
}
```

### 🔍 Estados de Vencimiento

- `"vencido"` - Fecha de vencimiento pasada
- `"critico"` - Vence en ≤ 7 días
- `"proximo"` - Vence en ≤ 30 días
- `"normal"` - Vence en > 30 días

### 💻 Uso en Frontend

```javascript
$.get(`/lotes/api/lote/${loteId}`).done(function (data) {
  if (data.success) {
    const lote = data.lote;
    console.log(lote);
  }
});
```

---

## ✅ 2. Priorizar Lote en FIFO

### 📍 Endpoint

```
POST /lotes/api/lote/<lote_id>/priorizar
```

### 🎯 Función

Marca un lote como prioritario modificando su fecha de entrada para que se consuma primero según el sistema FIFO.

### 📥 Request Body

```json
{
  "observaciones": "Lote próximo a vencer - Consumo prioritario"
}
```

### 📊 Respuesta

```json
{
  "success": true,
  "message": "Lote priorizado exitosamente",
  "lote": {
    "id": 1,
    "codigo_lote": "LOTE-2024-001",
    "fecha_entrada_original": "2024-03-15T10:00:00",
    "fecha_entrada_nueva": "2024-01-14T10:00:00",
    "inventario_codigo": "ART-001",
    "inventario_nombre": "Tornillo M8x20"
  }
}
```

### 🔧 Funcionamiento

1. Busca el lote más antiguo del mismo artículo
2. Ajusta la fecha de entrada del lote a **1 día antes** del más antiguo
3. Registra la acción en observaciones y movimientos
4. El lote ahora se consumirá primero en el orden FIFO

### ⚠️ Validaciones

- El lote debe estar activo
- Debe tener stock disponible (cantidad_actual > 0)
- Debe existir al menos un lote del mismo artículo

### 💻 Uso en Frontend

```javascript
function priorizarLote(loteId) {
  // Modal de confirmación
  // Al confirmar:
  $.ajax({
    url: `/lotes/api/lote/${loteId}/priorizar`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      observaciones: "Motivo de priorización",
    }),
    success: function (response) {
      mostrarMensaje(response.message, "success");
      actualizarVencimientos();
    },
  });
}
```

### 🎨 Interfaz de Usuario

- **Botón**: <i class="fas fa-arrow-up"></i> Priorizar
- **Modal**: Confirmación con información del lote y campo de observaciones
- **Ubicación**: Cards de lotes próximos a vencer

---

## ✅ 3. Mover Lote a Nueva Ubicación

### 📍 Endpoint

```
POST /lotes/api/lote/<lote_id>/mover
```

### 🎯 Función

Cambia la ubicación física de un lote en el almacén, registrando el movimiento en la trazabilidad.

### 📥 Request Body

```json
{
  "ubicacion": "Almacén B - Estantería 5 - Nivel 3",
  "observaciones": "Reorganización del almacén"
}
```

### 📊 Respuesta

```json
{
  "success": true,
  "message": "Lote movido exitosamente de 'Almacén A' a 'Almacén B - Estantería 5 - Nivel 3'",
  "lote": {
    "id": 1,
    "codigo_lote": "LOTE-2024-001",
    "ubicacion_original": "Almacén A",
    "ubicacion_nueva": "Almacén B - Estantería 5 - Nivel 3",
    "inventario_codigo": "ART-001",
    "inventario_nombre": "Tornillo M8x20"
  }
}
```

### 🔧 Funcionamiento

1. Actualiza el campo `ubicacion` del lote
2. Registra el cambio en observaciones con timestamp
3. Crea un movimiento de tipo `"movimiento_ubicacion"` para trazabilidad
4. No afecta la cantidad del lote

### ⚠️ Validaciones

- El lote debe estar activo
- La nueva ubicación no puede estar vacía
- La nueva ubicación debe ser diferente a la actual

### 💻 Uso en Frontend

```javascript
function moverLote(loteId) {
  // Modal con formulario
  // Al confirmar:
  $.ajax({
    url: `/lotes/api/lote/${loteId}/mover`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      ubicacion: nuevaUbicacion,
      observaciones: motivoMovimiento,
    }),
    success: function (response) {
      mostrarMensaje(response.message, "success");
      actualizarVencimientos();
    },
  });
}
```

### 🎨 Interfaz de Usuario

- **Botón**: <i class="fas fa-exchange-alt"></i> Mover
- **Modal**: Formulario con campos de ubicación y observaciones
- **Ubicación**: Cards de lotes vencidos y próximos a vencer

---

## ✅ 4. Filtros Avanzados (Bonus)

### 🎯 Función

Panel de filtros colapsable para buscar y filtrar lotes por múltiples criterios.

### 🔍 Filtros Disponibles

#### 📅 Días hasta vencimiento

- Todos
- Ya vencidos
- Próximos 7 días (Crítico)
- Próximos 15 días
- Próximos 30 días (default)
- Próximos 60 días
- Próximos 90 días

#### 📦 Buscar artículo

Búsqueda por código o nombre (texto libre)

#### 💰 Valor mínimo en riesgo

Filtrar lotes con valor total >= cantidad especificada

#### 📍 Ubicación

Búsqueda por ubicación (texto libre)

#### 📊 Ordenar por

- Fecha vencimiento (ascendente/descendente)
- Valor (mayor a menor / menor a mayor)
- Cantidad (mayor a menor)
- Artículo (A-Z)

### 🔧 Funcionamiento

1. Guarda los datos originales de todos los lotes al cargar la página
2. Aplica filtros en tiempo real sin recargar
3. Actualiza contadores de las pestañas
4. Muestra estadística de resultados filtrados
5. Botón "Limpiar Filtros" para resetear

### 💻 Uso

Los filtros se aplican automáticamente con `oninput` y `onchange`. No requiere botón "Aplicar".

### 🎨 Interfaz

- **Ubicación**: Entre estadísticas y pestañas
- **Estado**: Colapsable por defecto
- **Indicador**: Muestra "X de Y lotes"

---

## 📝 Registro de Movimientos

Todas las operaciones (priorizar y mover) quedan registradas en:

### 1️⃣ Tabla `movimiento_lote`

```sql
INSERT INTO movimiento_lote (
    lote_id,
    tipo_movimiento,  -- 'ajuste_prioridad' o 'movimiento_ubicacion'
    cantidad,         -- 0 (sin cambio)
    cantidad_anterior,
    cantidad_nueva,
    documento_referencia,
    observaciones,
    usuario_id,
    fecha
)
```

### 2️⃣ Campo `observaciones` del lote

```
[2025-10-19 14:30] PRIORIZADO: Lote próximo a vencer
[2025-10-19 15:45] MOVIMIENTO: Reorganización del almacén
```

---

## 🧪 Testing

### Pruebas Manuales Recomendadas

#### ✅ Test 1: Obtener lote individual

```bash
curl http://localhost:5000/lotes/api/lote/1
```

#### ✅ Test 2: Priorizar lote

```bash
curl -X POST http://localhost:5000/lotes/api/lote/1/priorizar \
  -H "Content-Type: application/json" \
  -d '{"observaciones": "Test de priorización"}'
```

#### ✅ Test 3: Mover lote

```bash
curl -X POST http://localhost:5000/lotes/api/lote/1/mover \
  -H "Content-Type: application/json" \
  -d '{"ubicacion": "Almacén Test", "observaciones": "Movimiento de prueba"}'
```

#### ✅ Test 4: Filtros en UI

1. Ir a `/lotes/vencimientos`
2. Expandir "Filtros Avanzados"
3. Seleccionar "Próximos 7 días"
4. Buscar artículo por nombre
5. Verificar que se filtran correctamente

---

## 🔐 Seguridad

### Autenticación

Todos los endpoints requieren `@login_required`

### Validaciones

- ✅ Lote debe existir (404 si no existe)
- ✅ Lote debe estar activo
- ✅ Datos de entrada validados
- ✅ Transacciones con rollback en caso de error

### Logging

```python
logger.error(f"Error al priorizar lote {lote_id}: {str(e)}")
```

---

## 📊 Base de Datos

### Nuevos Tipos de Movimiento

```python
tipo_movimiento = "ajuste_prioridad"    # Priorización
tipo_movimiento = "movimiento_ubicacion" # Cambio de ubicación
```

### Campos Utilizados

- `LoteInventario.fecha_entrada` - Modificado en priorización
- `LoteInventario.ubicacion` - Modificado en movimiento
- `LoteInventario.observaciones` - Historial de cambios

---

## 🎨 UI/UX Mejorada

### Modales Implementados

1. **Modal de Priorización** - Fondo amarillo (warning)
2. **Modal de Movimiento** - Fondo azul (info)
3. **Modal de Consumo** - Ya existente (rojo/danger)

### Iconografía

- 🔼 `fa-arrow-up` - Priorizar
- 🔄 `fa-exchange-alt` - Mover
- ➖ `fa-minus` - Consumir
- 👁️ `fa-eye` - Ver detalles

### Notificaciones

Toast notifications con auto-hide (5 segundos) para feedback inmediato

---

## 🚀 Próximas Funcionalidades Sugeridas

1. **📄 Exportar a Excel** - Reporte de lotes vencidos/próximos
2. **🔔 Notificaciones Push** - Alertas automáticas de vencimientos
3. **📧 Envío de Reportes** - Informes periódicos por email
4. **📈 Dashboard de Vencimientos** - Gráficos y estadísticas avanzadas
5. **🏷️ Etiquetas QR** - Generar etiquetas para lotes
6. **📱 Vista Móvil** - Optimización responsive mejorada

---

## 📚 Archivos Modificados

### Backend

- `app/blueprints/lotes.py` (+220 líneas)
  - `api_lote_individual()` (línea ~348)
  - `api_priorizar_lote()` (línea ~478)
  - `api_mover_lote()` (línea ~572)

### Frontend

- `app/templates/lotes/vencimientos.html` (+350 líneas)
  - Panel de filtros avanzados (línea ~257)
  - Funciones JavaScript de priorización (línea ~900)
  - Funciones JavaScript de movimiento (línea ~770)
  - Funciones de filtrado (línea ~1010)

---

## 👥 Autor

**Sistema GMAO - Módulo FIFO**  
Fecha: 19 de octubre de 2025  
Versión: 1.0.0

---

## 📞 Soporte

Para preguntas o issues:

1. Revisar logs en `logs/`
2. Verificar consola del navegador (F12)
3. Comprobar estado de base de datos
4. Validar permisos de usuario

---

**¡Funcionalidades implementadas y listas para usar!** ✨
