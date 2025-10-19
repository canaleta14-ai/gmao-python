# Sistema FIFO (First In, First Out)

## 📋 Índice

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Modelos de Datos](#modelos-de-datos)
4. [API REST](#api-rest)
5. [Servicio FIFO](#servicio-fifo)
6. [Flujos de Trabajo](#flujos-de-trabajo)
7. [Integración con Órdenes de Trabajo](#integración-con-órdenes-de-trabajo)
8. [Interfaz de Usuario](#interfaz-de-usuario)
9. [Ejemplos de Uso](#ejemplos-de-uso)
10. [Validaciones y Reglas de Negocio](#validaciones-y-reglas-de-negocio)

---

## Introducción

El **Sistema FIFO** (First In, First Out) es un módulo de gestión de inventario que implementa el método de valoración de inventarios donde **los primeros artículos en entrar son los primeros en salir**. Este sistema es esencial para:

- **Gestión de lotes con fecha de caducidad**
- **Control de trazabilidad** (seguimiento completo de cada lote)
- **Optimización de inventarios** (evitar obsolescencia)
- **Cumplimiento normativo** (auditorías, regulaciones sanitarias)

### 🔑 Concepto Fundamental: ¿Qué es un Lote?

Un **lote** es un grupo de unidades de un artículo que:

- Entraron al inventario en la misma fecha
- Tienen el mismo precio de compra
- Pueden tener la misma fecha de vencimiento (opcional)
- Se consumen como una unidad en orden FIFO

**Ejemplo práctico:**

```
Artículo: Filtro de aire industrial

┌─────────────────────────────────────────────────────┐
│ LOTE-2024-001                                       │
│ • Entrada: 15/01/2024                               │
│ • Cantidad: 50 unidades                             │
│ • Precio: €15.00/ud                                 │
│ • Vencimiento: 15/01/2025                           │
│ • Estado: 10 unidades (consumidas primero en FIFO)  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ LOTE-2024-002                                       │
│ • Entrada: 20/02/2024                               │
│ • Cantidad: 30 unidades                             │
│ • Precio: €16.50/ud                                 │
│ • Vencimiento: 20/02/2025                           │
│ • Estado: 30 unidades disponibles                   │
└─────────────────────────────────────────────────────┘

Stock total del artículo = 40 unidades (10 + 30)
```

### ⚠️ IMPORTANTE: Migración de Artículos Existentes

Si ya tienes artículos en el inventario **sin lotes**, necesitas ejecutar la migración:

```bash
# Verificar situación actual
python scripts/verificar_lotes.py

# Migrar artículos existentes a lotes
python scripts/migrar_stock_a_lotes.py
```

Este script creará **un lote inicial** por cada artículo con stock existente.

### Características Principales

- ✅ Gestión automática de consumo FIFO
- ✅ Control de lotes con fecha de vencimiento
- ✅ Reservas de stock para órdenes de trabajo
- ✅ Trazabilidad completa de movimientos
- ✅ Alertas de vencimiento
- ✅ Validaciones de integridad
- ✅ Migración automática de stock existente

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE PRESENTACIÓN                   │
│  Templates HTML + JavaScript (AJAX) + Bootstrap            │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      CAPA DE RUTAS (API)                    │
│            app/blueprints/lotes.py (lotes_bp)              │
│  Endpoints: /api/consumir, /api/reservar, /api/liberar    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   CAPA DE LÓGICA DE NEGOCIO                 │
│          app/services/servicio_fifo.py (ServicioFIFO)      │
│  Métodos: consumir_fifo(), reservar_stock(), liberar()     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      CAPA DE PERSISTENCIA                   │
│       app/models/lote_inventario.py (SQLAlchemy ORM)       │
│  Modelos: LoteInventario, MovimientoLote                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Modelos de Datos

### LoteInventario

Representa un lote individual de inventario con control FIFO.

**Archivo:** `app/models/lote_inventario.py`

```python
class LoteInventario(db.Model):
    __tablename__ = 'lotes_inventario'

    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    inventario_id = db.Column(db.Integer, db.ForeignKey('inventario.id'), nullable=False)
    numero_lote = db.Column(db.String(100), nullable=False)
    cantidad_inicial = db.Column(db.Numeric(12, 4), nullable=False)
    cantidad_actual = db.Column(db.Numeric(12, 4), nullable=False)
    cantidad_reservada = db.Column(db.Numeric(12, 4), default=0)
    cantidad_disponible = db.Column(db.Numeric(12, 4))  # Calculada
    fecha_entrada = db.Column(db.DateTime, nullable=False)
    fecha_vencimiento = db.Column(db.Date)
    precio_unitario = db.Column(db.Numeric(12, 4))

    # Relaciones
    inventario = db.relationship('Inventario', backref='lotes')
    movimientos = db.relationship('MovimientoLote', back_populates='lote')
```

**Campos Clave:**

- `cantidad_actual`: Stock físico real en el lote
- `cantidad_reservada`: Cantidad comprometida para órdenes de trabajo
- `cantidad_disponible`: `cantidad_actual - cantidad_reservada` (disponible para nuevas reservas)
- `fecha_entrada`: Fecha de recepción del lote (determina orden FIFO)
- `fecha_vencimiento`: Fecha de caducidad (opcional)

**Métodos Principales:**

#### `consumir(cantidad, motivo, usuario_id, orden_trabajo_id)`

Consume stock del lote y registra movimiento de salida.

```python
# Validaciones:
# - ValueError si cantidad <= 0
# - ValueError si cantidad > cantidad_actual
# - Verifica que cantidad_actual no sea negativa después del consumo

lote.consumir(
    cantidad=10.5,
    motivo="Mantenimiento preventivo",
    usuario_id=1,
    orden_trabajo_id=42
)
```

#### `reservar(cantidad, orden_trabajo_id)`

Reserva stock para una orden de trabajo específica.

```python
# Validaciones:
# - ValueError si cantidad <= 0
# - ValueError si cantidad > cantidad_disponible

lote.reservar(cantidad=50, orden_trabajo_id=100)
```

#### `liberar_reserva(cantidad, orden_trabajo_id)`

Libera una reserva previa (si la orden se cancela).

```python
# Validaciones:
# - ValueError si cantidad <= 0
# - ValueError si cantidad > cantidad_reservada
# - Verifica que cantidad_reservada no sea negativa

lote.liberar_reserva(cantidad=50, orden_trabajo_id=100)
```

#### `obtener_lotes_fifo(inventario_id, incluir_vencidos=False)`

Método estático que retorna lotes ordenados por fecha de entrada (FIFO).

```python
# Por defecto excluye lotes vencidos
lotes = LoteInventario.obtener_lotes_fifo(inventario_id=5)

# Incluir lotes vencidos
todos_lotes = LoteInventario.obtener_lotes_fifo(
    inventario_id=5,
    incluir_vencidos=True
)
```

### MovimientoLote

Registra cada operación sobre un lote (entradas, salidas, reservas, liberaciones).

**Archivo:** `app/models/lote_inventario.py`

```python
class MovimientoLote(db.Model):
    __tablename__ = 'movimientos_lote'

    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes_inventario.id'))
    tipo_movimiento = db.Column(db.String(20))  # 'entrada', 'salida', 'reserva', 'liberacion'
    cantidad = db.Column(db.Numeric(12, 4), nullable=False)
    cantidad_antes = db.Column(db.Numeric(12, 4))
    cantidad_despues = db.Column(db.Numeric(12, 4))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    orden_trabajo_id = db.Column(db.Integer, db.ForeignKey('ordenes_trabajo.id'))

    # Relaciones
    lote = db.relationship('LoteInventario', back_populates='movimientos')
    usuario = db.relationship('Usuario', backref='movimientos_lote')
    orden_trabajo = db.relationship('OrdenTrabajo', backref='movimientos_lote')
```

**Tipos de Movimiento:**

- `entrada`: Recepción de nuevo lote
- `salida`: Consumo de stock
- `reserva`: Reserva para orden de trabajo
- `liberacion`: Liberación de reserva

---

## API REST

### Base URL

```
http://localhost:5000/lotes
```

### Endpoints Disponibles

#### 1. **Listar Todos los Lotes**

```http
GET /lotes/
```

**Respuesta (HTML):** Página con tabla de lotes

---

#### 2. **Obtener Información de Stock por Artículo**

```http
GET /lotes/api/lotes/<inventario_id>
```

**Parámetros:**

- `inventario_id` (path): ID del artículo de inventario

**Respuesta 200 OK:**

```json
{
  "success": true,
  "stock": {
    "inventario_id": 5,
    "nombre_articulo": "Filtro de aire",
    "stock_total": 150.0,
    "stock_disponible": 120.0,
    "stock_reservado": 30.0,
    "lotes": [
      {
        "id": 1,
        "numero_lote": "LOTE-2024-001",
        "cantidad_actual": 50.0,
        "cantidad_disponible": 40.0,
        "fecha_entrada": "2024-01-15T10:30:00",
        "fecha_vencimiento": "2025-01-15",
        "dias_hasta_vencimiento": 120
      }
    ]
  }
}
```

**Respuesta 404 Not Found:**

```json
{
  "success": false,
  "error": "No se encontraron lotes para este artículo"
}
```

---

#### 3. **Consumir Stock (FIFO Automático)**

```http
POST /lotes/api/consumir
```

**Headers:**

```
Content-Type: application/json
X-CSRFToken: <token>
```

**Body:**

```json
{
  "inventario_id": 5,
  "cantidad": 35.5,
  "motivo": "Mantenimiento correctivo bomba 3",
  "orden_trabajo_id": 142
}
```

**Validaciones:**

- `inventario_id` requerido
- `cantidad` requerido, debe ser > 0
- `motivo` opcional
- `orden_trabajo_id` opcional

**Respuesta 200 OK:**

```json
{
  "success": true,
  "message": "Stock consumido exitosamente",
  "data": {
    "cantidad_solicitada": 35.5,
    "cantidad_consumida": 35.5,
    "stock_restante": 114.5,
    "lotes_consumidos": [
      {
        "lote_id": 1,
        "numero_lote": "LOTE-2024-001",
        "cantidad_consumida": 20.0,
        "cantidad_restante": 30.0
      },
      {
        "lote_id": 2,
        "numero_lote": "LOTE-2024-002",
        "cantidad_consumida": 15.5,
        "cantidad_restante": 84.5
      }
    ]
  }
}
```

**Respuesta 400 Bad Request:**

```json
{
  "success": false,
  "error": "El campo 'inventario_id' es requerido"
}
```

**Respuesta 409 Conflict (Stock Insuficiente):**

```json
{
  "success": false,
  "error": "Stock insuficiente. Solicitado: 100.00, Disponible: 50.00, Faltante: 50.00",
  "data": {
    "solicitado": 100.0,
    "disponible": 50.0,
    "faltante": 50.0
  }
}
```

---

#### 4. **Reservar Stock para Orden de Trabajo**

```http
POST /lotes/api/reservar
```

**Headers:**

```
Content-Type: application/json
X-CSRFToken: <token>
```

**Body:**

```json
{
  "inventario_id": 5,
  "cantidad": 25.0,
  "orden_trabajo_id": 150
}
```

**Validaciones:**

- `orden_trabajo_id` requerido
- `cantidad` requerido, debe ser > 0

**Respuesta 200 OK:**

```json
{
  "success": true,
  "message": "Stock reservado exitosamente",
  "data": {
    "cantidad_reservada": 25.0,
    "orden_trabajo_id": 150,
    "lotes_reservados": [
      {
        "lote_id": 3,
        "numero_lote": "LOTE-2024-003",
        "cantidad_reservada": 25.0,
        "cantidad_disponible": 75.0
      }
    ]
  }
}
```

---

#### 5. **Liberar Reserva de Stock**

```http
POST /lotes/api/liberar
```

**Headers:**

```
Content-Type: application/json
X-CSRFToken: <token>
```

**Body:**

```json
{
  "inventario_id": 5,
  "cantidad": 25.0,
  "orden_trabajo_id": 150
}
```

**Respuesta 200 OK:**

```json
{
  "success": true,
  "message": "Reservas liberadas exitosamente",
  "data": {
    "cantidad_liberada": 25.0,
    "lotes_liberados": [
      {
        "lote_id": 3,
        "numero_lote": "LOTE-2024-003",
        "cantidad_liberada": 25.0
      }
    ]
  }
}
```

---

#### 6. **Trazabilidad Completa de un Lote**

```http
GET /lotes/trazabilidad/<lote_id>
```

**Respuesta (HTML):** Página con histórico completo de movimientos del lote

---

#### 7. **Lotes Próximos a Vencer**

```http
GET /lotes/vencimientos?dias=30
```

**Parámetros:**

- `dias` (query, opcional): Días de anticipación (default: 30)

**Respuesta (HTML):** Página con alertas de vencimiento

---

## Servicio FIFO

### ServicioFIFO

**Archivo:** `app/services/servicio_fifo.py`

Clase que implementa la lógica de negocio del sistema FIFO.

#### Método: `consumir_fifo(inventario_id, cantidad, motivo, usuario_id, orden_trabajo_id)`

Consume stock siguiendo el orden FIFO (primero los lotes más antiguos).

**Algoritmo:**

1. Obtener lotes disponibles ordenados por `fecha_entrada` ASC (FIFO)
2. Excluir lotes vencidos automáticamente
3. Para cada lote:
   - Si `cantidad_actual >= cantidad_restante`: consumir todo de este lote y continuar
   - Si `cantidad_actual < cantidad_restante`: consumir todo el lote y pasar al siguiente
4. Registrar movimientos de salida en cada lote consumido
5. Retornar resultado con lotes afectados

**Ejemplo:**

```python
from app.services.servicio_fifo import ServicioFIFO

servicio = ServicioFIFO()

resultado = servicio.consumir_fifo(
    inventario_id=5,
    cantidad=75.0,
    motivo="Reparación urgente",
    usuario_id=1,
    orden_trabajo_id=200
)

# resultado = {
#   'consumido': 75.0,
#   'faltante': 0.0,
#   'lotes': [
#     {'lote_id': 1, 'consumido': 50.0},
#     {'lote_id': 2, 'consumido': 25.0}
#   ]
# }
```

#### Método: `crear_lote_entrada(inventario_id, numero_lote, cantidad, precio_unitario, fecha_vencimiento)`

Crea un nuevo lote de entrada en el inventario.

**Validaciones:**

- Inventario debe existir
- Cantidad debe ser > 0
- Número de lote debe ser único

#### Método: `reservar_stock(inventario_id, cantidad, orden_trabajo_id)`

Reserva stock para una orden de trabajo específica.

**Características:**

- Sigue orden FIFO para reservas
- No consume stock, solo lo reserva
- Actualiza `cantidad_reservada` y `cantidad_disponible`

#### Método: `liberar_reservas(inventario_id, orden_trabajo_id, cantidad)`

Libera reservas de stock para una orden de trabajo.

**Casos de uso:**

- Orden de trabajo cancelada
- Orden completada con menos stock del reservado
- Corrección de reservas erróneas

#### Método: `obtener_stock_disponible(inventario_id)`

Retorna información agregada del stock de un artículo.

**Respuesta:**

```python
{
  'inventario_id': 5,
  'nombre': 'Filtro de aire',
  'stock_total': 150.0,
  'stock_disponible': 120.0,
  'stock_reservado': 30.0,
  'lotes': [...]
}
```

---

## Flujos de Trabajo

### 🔧 Generación de Lotes: ¿Cuándo y Cómo?

#### Escenario 1: Sistema Nuevo (Sin Stock Previo)

**Situación:** Empiezas con el sistema GMAO desde cero.

**Solución:** Los lotes se crean automáticamente al recibir mercancía:

1. Vas a **Inventario** → **Crear nuevo artículo**
2. El artículo se crea con `stock_actual = 0`
3. Cuando recibes mercancía:
   - Vas a **Lotes** → **Crear Lote**
   - Seleccionas el artículo
   - Ingresas cantidad, precio, fecha de vencimiento
   - El sistema crea el lote y actualiza el stock

#### Escenario 2: Migración de Sistema Anterior

**Situación:** Ya tienes artículos con stock pero sin lotes.

**Problema detectado:**

```bash
$ python scripts/verificar_lotes.py

============================================================
📊 ANÁLISIS DE INVENTARIO Y LOTES
============================================================

✅ Artículos totales en inventario: 901
✅ Artículos con stock > 0: 506
📦 Lotes FIFO creados: 0

⚠️  PROBLEMA DETECTADO:
   - Hay artículos con stock pero NO hay lotes creados
   - El sistema FIFO requiere que el stock esté organizado en lotes
```

**Solución: Script de Migración Automática**

```bash
# Paso 1: Verificar situación actual
python scripts/verificar_lotes.py

# Paso 2: Ejecutar migración (crea lotes iniciales)
python scripts/migrar_stock_a_lotes.py
```

**¿Qué hace el script de migración?**

1. **Identifica** artículos con `stock_actual > 0` pero sin lotes
2. **Crea un lote inicial** para cada uno:
   ```
   Código: LOTE-INICIAL-{ID}-{FECHA}
   Cantidad: {stock_actual del artículo}
   Fecha entrada: Fecha actual
   Precio: {precio_unitario del artículo}
   Documento: "MIGRACIÓN INICIAL"
   Observaciones: "Lote creado automáticamente..."
   ```
3. **Registra** movimiento de entrada
4. **Commit** cada 50 artículos (evita transacciones largas)

**Ejemplo de ejecución:**

```bash
$ python scripts/migrar_stock_a_lotes.py

============================================================
🔄 MIGRACIÓN DE STOCK EXISTENTE A SISTEMA FIFO
============================================================

📊 Analizando inventario...

✅ Encontrados 506 artículos con stock > 0
📦 Artículos sin lotes: 506

⚠️  Se crearán 506 lotes iniciales

📋 Ejemplos de artículos a migrar:
   1. [ART-00001] TERMO ELECTRICO VERTICAL - Stock: 2.00
   2. [ART-00002] CINTA TEFLON PTFE - Stock: 1.00
   3. [ART-00003] CALDERIN 25 AMF-PLUS - Stock: 1.00
   ...

¿Desea continuar con la migración? (si/no): si

🔄 Iniciando migración...
----------------------------------------------------------------------
✅ [1/506] ART-00001: Lote creado: LOTE-INICIAL-11-20241018
✅ [2/506] ART-00002: Lote creado: LOTE-INICIAL-12-20241018
   💾 Guardando lote 50...
✅ [50/506] ART-00050: Lote creado: LOTE-INICIAL-60-20241018
...

============================================================
📊 RESUMEN DE LA MIGRACIÓN
============================================================

✅ Lotes creados exitosamente: 506
❌ Fallos: 0

📦 Total de lotes en el sistema: 506

✅ Migración completada

💡 Próximos pasos:
   1. Verificar los lotes creados en /lotes/
   2. Ajustar fechas de vencimiento si es necesario
   3. Comenzar a usar el sistema FIFO para nuevas entradas
```

#### Escenario 3: Operación Normal (Después de Configuración)

**Flujo de trabajo diario:**

1. **Recepción de mercancía:**

   - Proveedor entrega pedido
   - Recibes 100 unidades de "Filtro X"
   - Precio: €20.00/ud
   - Vencimiento: 1 año

2. **Creación del lote:**

   - Navegas a `/lotes/crear_lote`
   - Formulario:
     ```
     Artículo: Filtro X
     Código lote: FILTROS-2024-OCT-001
     Cantidad: 100
     Precio unitario: 20.00
     Fecha vencimiento: 18/10/2025
     Documento origen: OC-12345
     ```
   - Click en "Crear Lote"

3. **Sistema actualiza:**

   - Crea `LoteInventario` con cantidad_inicial = 100
   - Actualiza `Inventario.stock_actual` += 100
   - Registra `MovimientoLote` tipo "entrada"

4. **Consumo automático FIFO:**
   - Cuando se consume material, el sistema usa **automáticamente** los lotes más antiguos primero
   - No necesitas seleccionar el lote manualmente

### Flujo 1: Entrada de Nuevo Lote

```
┌─────────────┐
│  Usuario    │ Recibe mercancía
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  Formulario "Crear Lote"        │
│  - Seleccionar artículo         │
│  - Número de lote               │
│  - Cantidad                     │
│  - Precio unitario              │
│  - Fecha de vencimiento         │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  POST /lotes/crear              │
│  Validaciones JavaScript        │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  ServicioFIFO.crear_lote()      │
│  - Validar datos                │
│  - Crear LoteInventario         │
│  - Registrar MovimientoLote     │
│    (tipo: 'entrada')            │
│  - Actualizar stock Inventario  │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│  Lote       │ Listo para consumo
│  Creado     │
└─────────────┘
```

### Flujo 2: Consumo FIFO en Orden de Trabajo

```
┌─────────────┐
│  Técnico    │ Ejecuta mantenimiento
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  Formulario "Consumir Material" │
│  - Artículo: Filtro (ID: 5)     │
│  - Cantidad: 3 unidades         │
│  - Orden: #142                  │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  POST /lotes/api/consumir       │
│  {                              │
│    inventario_id: 5,            │
│    cantidad: 3,                 │
│    orden_trabajo_id: 142        │
│  }                              │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  ServicioFIFO.consumir_fifo()   │
│  1. Obtener lotes FIFO          │
│     (más antiguos primero)      │
│  2. Consumir de lotes:          │
│     - Lote A (2024-01): 2 unid  │
│     - Lote B (2024-02): 1 unid  │
│  3. Registrar movimientos       │
│  4. Actualizar cantidades       │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│  Stock      │ Actualizado
│  Consumido  │
└─────────────┘
```

### Flujo 3: Reserva de Stock

```
┌─────────────┐
│  Planificador │ Crea orden de trabajo
└──────┬────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Formulario "Nueva Orden"       │
│  - Incluye materiales           │
│  - Cantidad estimada            │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  POST /lotes/api/reservar       │
│  {                              │
│    inventario_id: 5,            │
│    cantidad: 10,                │
│    orden_trabajo_id: 200        │
│  }                              │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  ServicioFIFO.reservar_stock()  │
│  1. Verificar disponibilidad    │
│  2. Reservar en lotes FIFO      │
│  3. Actualizar cantidad_reservada│
│  4. Registrar movimiento        │
│    (tipo: 'reserva')            │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│  Stock      │ Reservado (no disponible
│  Reservado  │ para otras órdenes)
└─────────────┘
       │
       │ [Cuando se ejecuta la orden]
       ▼
┌─────────────────────────────────┐
│  POST /lotes/api/consumir       │
│  - Consume desde reserva        │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│  Reserva    │ Convertida en consumo
│  → Consumo  │
└─────────────┘
```

---

## Integración con Órdenes de Trabajo

### Ciclo de Vida Material en Orden

```
┌────────────────────────────────────────────────────────┐
│                  ORDEN DE TRABAJO                      │
│  ID: 142 | Tipo: Preventivo | Estado: Programada      │
└────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Material 1   │   │  Material 2   │   │  Material 3   │
│  Filtro 10W30 │   │  Aceite       │   │  Empaque      │
│  Cant: 3      │   │  Cant: 5L     │   │  Cant: 2      │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        │ [Al crear orden]  │                   │
        ▼                   ▼                   ▼
┌───────────────────────────────────────────────────────┐
│            RESERVAR STOCK (opcional)                  │
│  POST /lotes/api/reservar para cada material         │
│  - Stock queda "bloqueado" para esta orden           │
│  - cantidad_disponible disminuye                     │
│  - cantidad_reservada aumenta                        │
└───────────────────┬───────────────────────────────────┘
                    │
        │ [Al ejecutar orden]
        ▼
┌───────────────────────────────────────────────────────┐
│              CONSUMIR STOCK                           │
│  POST /lotes/api/consumir para cada material         │
│  - Si había reserva: usa esos lotes primero          │
│  - Si no: consume según FIFO normal                  │
│  - Registra movimientos con orden_trabajo_id         │
└───────────────────┬───────────────────────────────────┘
                    │
                    ▼
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│  Orden        │       │  Orden        │
│  Completada   │       │  Cancelada    │
└───────────────┘       └───────┬───────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  LIBERAR RESERVA      │
                    │  POST /lotes/api/     │
                    │       liberar         │
                    └───────────────────────┘
```

### Ejemplo Práctico

**Orden de Trabajo #142:** Mantenimiento preventivo bomba centrífuga

**Materiales Requeridos:**

- Filtro de aceite 10W30 (ID: 5) → 3 unidades
- Grasa sintética (ID: 12) → 0.5 kg
- Empaque bomba (ID: 28) → 1 unidad

**Paso 1: Crear Orden (Estado: Programada)**

```javascript
// En el formulario de nueva orden
const materialesRequeridos = [
  { inventario_id: 5, cantidad: 3 },
  { inventario_id: 12, cantidad: 0.5 },
  { inventario_id: 28, cantidad: 1 },
];

// Reservar stock al crear la orden
for (const material of materialesRequeridos) {
  await fetch("/lotes/api/reservar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      inventario_id: material.inventario_id,
      cantidad: material.cantidad,
      orden_trabajo_id: 142,
    }),
  });
}
```

**Resultado:**

- Stock reservado ✅
- Otros técnicos no pueden usar ese stock
- Inventario muestra: "Disponible: X | Reservado: Y"

**Paso 2: Ejecutar Orden (Estado: En Progreso)**

```javascript
// Cuando el técnico usa los materiales
for (const material of materialesUsados) {
  await fetch("/lotes/api/consumir", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      inventario_id: material.inventario_id,
      cantidad: material.cantidad_real, // Puede ser < reservado
      motivo: "Mantenimiento preventivo bomba 3",
      orden_trabajo_id: 142,
    }),
  });
}
```

**Resultado:**

- Stock consumido desde la reserva
- Movimientos registrados con trazabilidad completa
- Si se usó menos de lo reservado, liberar el excedente

---

## Interfaz de Usuario

### Páginas Principales

#### 1. **Índice de Lotes** (`/lotes/`)

**Archivo:** `app/templates/lotes/index.html`

**Características:**

- Tabla con todos los lotes activos
- Filtros por artículo, estado (activo/vencido)
- Indicadores visuales:
  - 🔴 Lote vencido
  - 🟡 Próximo a vencer (< 30 días)
  - 🟢 Lote en buen estado
- Badges de stock disponible/reservado
- Acciones: Ver detalle, Consumir, Trazabilidad

#### 2. **Crear Lote** (`/lotes/crear`)

**Archivo:** `app/templates/lotes/crear_lote.html`

**Formulario:**

```html
<form id="formCrearLote">
  <select name="inventario_id" required>
    <!-- Artículos disponibles -->
  </select>

  <input type="text" name="numero_lote" placeholder="LOTE-2024-001" required />
  <input type="number" name="cantidad" step="0.01" min="0.01" required />
  <input type="number" name="precio_unitario" step="0.01" min="0" />
  <input type="date" name="fecha_vencimiento" />

  <button type="submit">Crear Lote</button>
</form>
```

**Validaciones JavaScript:**

```javascript
function validarFormulario() {
  const articulo = document.getElementById("inventario_id").value;
  const cantidad = parseFloat(document.getElementById("cantidad").value);
  const precio = parseFloat(document.getElementById("precio_unitario").value);
  const fechaVencimiento = document.getElementById("fecha_vencimiento").value;

  if (!articulo) {
    mostrarError("Debe seleccionar un artículo");
    return false;
  }

  if (cantidad <= 0) {
    mostrarError("La cantidad debe ser mayor a 0");
    return false;
  }

  if (precio < 0) {
    mostrarError("El precio no puede ser negativo");
    return false;
  }

  if (fechaVencimiento) {
    const hoy = new Date().toISOString().split("T")[0];
    if (fechaVencimiento <= hoy) {
      mostrarError("La fecha de vencimiento debe ser futura");
      return false;
    }
  }

  return true;
}
```

#### 3. **Detalle de Inventario** (`/lotes/inventario/<id>`)

**Archivo:** `app/templates/lotes/detalle_inventario.html`

**Muestra:**

- Información del artículo
- Stock total/disponible/reservado
- Lista de lotes con cantidad actual
- Gráfico de distribución por lote
- Próximos vencimientos

#### 4. **Trazabilidad** (`/lotes/trazabilidad/<lote_id>`)

**Archivo:** `app/templates/lotes/trazabilidad.html`

**Timeline de Movimientos:**

```
📦 01/01/2024 10:30 - ENTRADA
   └─ Cantidad: 100 unidades
   └─ Usuario: Juan Pérez
   └─ Lote: LOTE-2024-001

📤 05/01/2024 14:20 - SALIDA
   └─ Cantidad: 25 unidades
   └─ Motivo: Mantenimiento correctivo
   └─ Orden: #142
   └─ Usuario: María García
   └─ Stock restante: 75 unidades

🔒 10/01/2024 09:15 - RESERVA
   └─ Cantidad: 30 unidades
   └─ Orden: #150
   └─ Usuario: Carlos López

🔓 12/01/2024 16:45 - LIBERACIÓN
   └─ Cantidad: 10 unidades
   └─ Motivo: Orden cancelada
   └─ Orden: #150
```

#### 5. **Alertas de Vencimiento** (`/lotes/vencimientos`)

**Archivo:** `app/templates/lotes/vencimientos.html`

**Tabla de Lotes Próximos a Vencer:**

| Artículo      | Lote          | Cantidad    | Vencimiento | Días      | Acciones           |
| ------------- | ------------- | ----------- | ----------- | --------- | ------------------ |
| Filtro 10W30  | LOTE-2024-001 | 45 unidades | 15/11/2024  | 🔴 **5**  | Consumir / Ajustar |
| Aceite SAE 40 | LOTE-2024-003 | 20 L        | 30/11/2024  | 🟡 **20** | Ver detalle        |

---

## Ejemplos de Uso

### Ejemplo 1: Crear Lote de Entrada

**Escenario:** Llega pedido de 100 filtros de aire con vencimiento a 1 año.

```bash
curl -X POST http://localhost:5000/lotes/crear \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{
    "inventario_id": 5,
    "numero_lote": "FILTROS-2024-OCT-001",
    "cantidad": 100,
    "precio_unitario": 15.50,
    "fecha_vencimiento": "2025-10-18"
  }'
```

**Respuesta:**

```json
{
  "success": true,
  "message": "Lote creado exitosamente",
  "lote_id": 42
}
```

### Ejemplo 2: Consumir Material en Mantenimiento

**Escenario:** Técnico realiza mantenimiento y usa 3 filtros de aire.

```bash
curl -X POST http://localhost:5000/lotes/api/consumir \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{
    "inventario_id": 5,
    "cantidad": 3,
    "motivo": "Mantenimiento preventivo bomba centrífuga 3",
    "orden_trabajo_id": 142
  }'
```

**Respuesta:**

```json
{
  "success": true,
  "message": "Stock consumido exitosamente",
  "data": {
    "cantidad_consumida": 3,
    "lotes_consumidos": [
      {
        "lote_id": 40,
        "numero_lote": "FILTROS-2024-SEP-001",
        "cantidad_consumida": 3,
        "cantidad_restante": 7,
        "fecha_entrada": "2024-09-15"
      }
    ]
  }
}
```

**Lógica FIFO:**

- Sistema identifica lote más antiguo (FILTROS-2024-SEP-001)
- Consume las 3 unidades de ese lote
- Si ese lote tuviera solo 2 unidades, consumiría 2 de ese lote y 1 del siguiente

### Ejemplo 3: Reservar Stock para Orden Futura

**Escenario:** Se programa mantenimiento para la próxima semana, se reservan materiales.

```bash
curl -X POST http://localhost:5000/lotes/api/reservar \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{
    "inventario_id": 5,
    "cantidad": 10,
    "orden_trabajo_id": 200
  }'
```

**Respuesta:**

```json
{
  "success": true,
  "message": "Stock reservado exitosamente",
  "data": {
    "cantidad_reservada": 10,
    "lotes_reservados": [
      {
        "lote_id": 42,
        "numero_lote": "FILTROS-2024-OCT-001",
        "cantidad_reservada": 10,
        "cantidad_disponible": 90
      }
    ]
  }
}
```

**Estado después de la reserva:**

- Lote 42:
  - `cantidad_actual`: 100 (stock físico)
  - `cantidad_reservada`: 10 (comprometido para orden #200)
  - `cantidad_disponible`: 90 (disponible para otras órdenes)

### Ejemplo 4: Consultar Stock Disponible

```bash
curl -X GET http://localhost:5000/lotes/api/lotes/5
```

**Respuesta:**

```json
{
  "success": true,
  "stock": {
    "inventario_id": 5,
    "nombre_articulo": "Filtro de aire industrial",
    "codigo": "FILT-AIR-001",
    "stock_total": 147,
    "stock_disponible": 127,
    "stock_reservado": 20,
    "lotes": [
      {
        "id": 40,
        "numero_lote": "FILTROS-2024-SEP-001",
        "cantidad_actual": 7,
        "cantidad_disponible": 7,
        "fecha_entrada": "2024-09-15",
        "fecha_vencimiento": "2025-09-15",
        "dias_hasta_vencimiento": 332
      },
      {
        "id": 42,
        "numero_lote": "FILTROS-2024-OCT-001",
        "cantidad_actual": 100,
        "cantidad_disponible": 90,
        "cantidad_reservada": 10,
        "fecha_entrada": "2024-10-18",
        "fecha_vencimiento": "2025-10-18",
        "dias_hasta_vencimiento": 365
      },
      {
        "id": 43,
        "numero_lote": "FILTROS-2024-OCT-002",
        "cantidad_actual": 40,
        "cantidad_disponible": 30,
        "cantidad_reservada": 10,
        "fecha_entrada": "2024-10-19",
        "fecha_vencimiento": "2025-10-19",
        "dias_hasta_vencimiento": 366
      }
    ]
  }
}
```

---

## Validaciones y Reglas de Negocio

### Validaciones a Nivel de Modelo

#### LoteInventario

✅ **Cantidad Positiva:**

```python
if cantidad <= 0:
    raise ValueError("La cantidad debe ser mayor a 0")
```

✅ **Stock Suficiente (Consumo):**

```python
if cantidad > self.cantidad_actual:
    raise ValueError(f"Stock insuficiente. Disponible: {self.cantidad_actual}")
```

✅ **Stock Disponible (Reserva):**

```python
if cantidad > self.cantidad_disponible:
    raise ValueError(f"Stock no disponible. Solo hay {self.cantidad_disponible}")
```

✅ **Integridad de Cantidades:**

```python
# Después de consumir
if self.cantidad_actual < 0:
    raise ValueError("La cantidad actual no puede ser negativa")

# Después de liberar reserva
if self.cantidad_reservada < 0:
    raise ValueError("La cantidad reservada no puede ser negativa")
```

### Validaciones a Nivel de Servicio

#### ServicioFIFO

✅ **Artículo Existe:**

```python
inventario = Inventario.query.get(inventario_id)
if not inventario:
    raise ValueError(f"Artículo de inventario {inventario_id} no encontrado")
```

✅ **Excluir Lotes Vencidos:**

```python
# En obtener_lotes_fifo() por defecto
lotes = LoteInventario.obtener_lotes_fifo(inventario_id, incluir_vencidos=False)
```

✅ **Stock Agregado Insuficiente:**

```python
stock_disponible = sum(lote.cantidad_disponible for lote in lotes)
if cantidad > stock_disponible:
    faltante = cantidad - stock_disponible
    logger.warning(f"Stock insuficiente. Faltante: {faltante}")
    # Retorna info parcial
```

### Validaciones a Nivel de API

#### Endpoints (lotes.py)

✅ **Campos Requeridos:**

```python
# POST /api/consumir
if not request.json.get('inventario_id'):
    return jsonify({'success': False, 'error': 'Campo requerido'}), 400

if not request.json.get('cantidad'):
    return jsonify({'success': False, 'error': 'Campo requerido'}), 400
```

✅ **Tipos de Datos:**

```python
try:
    cantidad = float(request.json.get('cantidad'))
except (ValueError, TypeError):
    return jsonify({'success': False, 'error': 'Cantidad inválida'}), 400
```

✅ **Rollback en Errores:**

```python
try:
    resultado = servicio.consumir_fifo(...)
    db.session.commit()
except ValueError as e:
    db.session.rollback()
    return jsonify({'success': False, 'error': str(e)}), 400
```

### Validaciones JavaScript (Frontend)

#### crear_lote.html

```javascript
function validarFormulario() {
  // Artículo seleccionado
  const articulo = document.getElementById("inventario_id").value;
  if (!articulo) {
    mostrarError("Debe seleccionar un artículo");
    return false;
  }

  // Cantidad mayor a 0
  const cantidad = parseFloat(document.getElementById("cantidad").value);
  if (isNaN(cantidad) || cantidad <= 0) {
    mostrarError("La cantidad debe ser mayor a 0");
    return false;
  }

  // Precio no negativo
  const precio = parseFloat(document.getElementById("precio_unitario").value);
  if (precio < 0) {
    mostrarError("El precio no puede ser negativo");
    return false;
  }

  // Fecha vencimiento futura (si se proporciona)
  const fechaVencimiento = document.getElementById("fecha_vencimiento").value;
  if (fechaVencimiento) {
    const hoy = new Date().toISOString().split("T")[0];
    if (fechaVencimiento <= hoy) {
      mostrarError("La fecha de vencimiento debe ser futura");
      return false;
    }
  }

  return true;
}
```

### Reglas de Negocio

#### 1. **Orden FIFO Estricto**

Los lotes **siempre** se consumen por orden de `fecha_entrada` (más antiguo primero):

```python
lotes = LoteInventario.query.filter_by(inventario_id=inventario_id) \
                             .order_by(LoteInventario.fecha_entrada.asc()) \
                             .all()
```

#### 2. **Exclusión Automática de Lotes Vencidos**

Por defecto, los lotes vencidos **no** se incluyen en consumos automáticos:

```python
if not incluir_vencidos and lote.fecha_vencimiento:
    if lote.fecha_vencimiento < date.today():
        continue  # Saltar lote vencido
```

#### 3. **Prioridad de Reservas**

Las reservas **no bloquean el stock físico**, solo reducen la disponibilidad:

- `cantidad_actual`: Stock físico real
- `cantidad_reservada`: Stock comprometido
- `cantidad_disponible = cantidad_actual - cantidad_reservada`

#### 4. **Trazabilidad Completa**

Cada operación **debe** registrar un `MovimientoLote`:

```python
movimiento = MovimientoLote(
    lote_id=lote.id,
    tipo_movimiento='salida',  # entrada, salida, reserva, liberacion
    cantidad=cantidad_consumida,
    cantidad_antes=cantidad_antes,
    cantidad_despues=lote.cantidad_actual,
    motivo=motivo,
    usuario_id=usuario_id,
    orden_trabajo_id=orden_trabajo_id
)
db.session.add(movimiento)
```

#### 5. **Atomicidad de Transacciones**

Todas las operaciones multi-lote son atómicas (todo o nada):

```python
try:
    for lote in lotes:
        lote.consumir(...)
    db.session.commit()
except Exception as e:
    db.session.rollback()
    raise
```

---

## Conclusión

El Sistema FIFO proporciona una gestión robusta y auditada del inventario con las siguientes ventajas:

✅ **Automatización:** Consumo FIFO automático sin intervención manual  
✅ **Trazabilidad:** Histórico completo de cada movimiento  
✅ **Prevención:** Alertas de vencimiento y validaciones de stock  
✅ **Integridad:** Validaciones multi-capa (modelo, servicio, API, frontend)  
✅ **Integración:** Vinculación directa con órdenes de trabajo  
✅ **Auditoría:** Registro de usuario y timestamp en cada operación

Para más información, consultar:

- [Documentación API Inventario](API_INVENTARIO.md)
- [Guía de Migraciones](MIGRACIONES.md)
- [Tests Unitarios](../tests/test_services/test_servicio_fifo.py)
