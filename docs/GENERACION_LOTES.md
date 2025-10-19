# 📦 GENERACIÓN DE LOTES - GUÍA RÁPIDA

## ¿Por qué los artículos no tienen lotes?

### Situación Actual

```
┌─────────────────────────────────────────────┐
│         BASE DE DATOS ACTUAL                │
├─────────────────────────────────────────────┤
│                                             │
│  📊 Tabla: inventario                       │
│  ├─ 901 artículos totales                   │
│  ├─ 506 artículos con stock > 0             │
│  └─ Creados SIN sistema de lotes           │
│                                             │
│  📦 Tabla: lotes_inventario                 │
│  └─ 0 lotes (VACÍA)                         │
│                                             │
└─────────────────────────────────────────────┘
```

**Problema:** El sistema FIFO se implementó **después** de tener artículos en inventario.

---

## Solución: 2 Formas de Generar Lotes

### 🔴 Método 1: Migración Automática (RECOMENDADO)

**Cuándo usar:** Ya tienes artículos con stock que necesitas convertir a lotes.

```bash
# Paso 1: Verificar situación
python scripts/verificar_lotes.py

# Paso 2: Ejecutar migración
python scripts/migrar_stock_a_lotes.py
```

**Resultado:**

```
Antes:                          Después:
┌─────────────────┐            ┌─────────────────┐
│ Artículo #11    │            │ Artículo #11    │
│ Código: ART-001 │            │ Código: ART-001 │
│ Stock: 2.00     │  ────────> │ Stock: 2.00     │
│ ❌ Sin lotes    │            │                 │
└─────────────────┘            │ ✅ Con lote:    │
                               │   LOTE-INICIAL  │
                               │   Cantidad: 2.00│
                               └─────────────────┘
```

**¿Qué crea el script?**

Para cada artículo con stock > 0:

- ✅ Un lote inicial con todo el stock actual
- ✅ Código: `LOTE-INICIAL-{ID}-{FECHA}`
- ✅ Precio del artículo
- ✅ Sin fecha de vencimiento (puedes editarla después)
- ✅ Observaciones: "Lote creado automáticamente..."

---

### 🟢 Método 2: Crear Lotes Manualmente

**Cuándo usar:**

- Nuevos artículos sin stock previo
- Recepción de mercancía nueva
- Operación normal del sistema

#### A. Desde la Interfaz Web

**Paso a paso:**

1. **Navega a Lotes**

   ```
   http://localhost:5000/lotes/
   ```

2. **Click en "Crear Nuevo Lote"**

   ```
   http://localhost:5000/lotes/crear_lote
   ```

3. **Completa el formulario:**

   ```
   ┌──────────────────────────────────────────┐
   │  Crear Nuevo Lote                        │
   ├──────────────────────────────────────────┤
   │                                          │
   │  Artículo: [Seleccionar...]             │
   │            ↓                             │
   │            Filtro de aire (ART-00001)   │
   │                                          │
   │  Código Lote: FILTROS-2024-OCT-001      │
   │                                          │
   │  Cantidad: 100                           │
   │                                          │
   │  Precio Unitario: 15.50                  │
   │                                          │
   │  Fecha Vencimiento: 2025-10-18          │
   │                                          │
   │  Documento Origen: OC-12345             │
   │                                          │
   │  [ Crear Lote ]                          │
   └──────────────────────────────────────────┘
   ```

4. **Sistema crea automáticamente:**
   - ✅ Lote en `lotes_inventario`
   - ✅ Movimiento de entrada en `movimientos_lote`
   - ✅ Actualiza `stock_actual` del artículo

#### B. Desde Python (Script o API)

```python
from app.services.servicio_fifo import ServicioFIFO
from datetime import datetime, timezone, timedelta

# Crear lote
lote = ServicioFIFO.crear_lote_entrada(
    inventario_id=11,
    cantidad=100.0,
    precio_unitario=15.50,
    codigo_lote="FILTROS-2024-OCT-001",
    fecha_vencimiento=datetime.now(timezone.utc) + timedelta(days=365),
    documento_origen="OC-12345",
    usuario_id="admin",
    observaciones="Recepción de pedido proveedor XYZ"
)

db.session.commit()
```

#### C. Desde la API REST

```bash
curl -X POST http://localhost:5000/lotes/crear_lote \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-CSRFToken: <token>" \
  -d "inventario_id=11" \
  -d "cantidad=100" \
  -d "precio_unitario=15.50" \
  -d "codigo_lote=FILTROS-2024-OCT-001" \
  -d "fecha_vencimiento=2025-10-18"
```

---

## 🔍 Comparación de Métodos

| Aspecto           | Migración Automática        | Crear Manualmente           |
| ----------------- | --------------------------- | --------------------------- |
| **Cuándo**        | Una vez (migración inicial) | Cada recepción de mercancía |
| **Para qué**      | Stock existente sin lotes   | Nueva mercancía             |
| **Cantidad**      | 506 artículos (en tu caso)  | 1 artículo a la vez         |
| **Tiempo**        | ~2 minutos                  | ~30 segundos por lote       |
| **Código lote**   | Auto: `LOTE-INICIAL-{ID}`   | Manual: `FILTROS-2024-001`  |
| **Fecha entrada** | Fecha actual                | Fecha actual                |
| **Vencimiento**   | Sin fecha (NULL)            | La que especifiques         |
| **Reversible**    | No (pero puedes editar)     | Sí (antes de consumir)      |

---

## 📋 Checklist de Configuración FIFO

### Primera Vez (Configuración Inicial)

- [ ] 1. Verificar artículos sin lotes:

  ```bash
  python scripts/verificar_lotes.py
  ```

- [ ] 2. Ejecutar migración si hay artículos con stock:

  ```bash
  python scripts/migrar_stock_a_lotes.py
  ```

- [ ] 3. Verificar resultado:

  ```bash
  python scripts/verificar_lotes.py
  # Debe mostrar: "✅ Sistema FIFO configurado correctamente"
  ```

- [ ] 4. Revisar lotes creados en la interfaz:

  ```
  http://localhost:5000/lotes/
  ```

- [ ] 5. Ajustar fechas de vencimiento si es necesario:
  - Editar lotes uno por uno
  - Agregar fecha de vencimiento a artículos críticos

### Operación Diaria

- [ ] 1. Al recibir mercancía nueva:

  - Ir a `/lotes/crear_lote`
  - Crear lote con datos del albarán

- [ ] 2. Al consumir material:

  - El sistema consume automáticamente desde lotes más antiguos
  - No necesitas seleccionar el lote manualmente

- [ ] 3. Revisar alertas de vencimiento:
  ```
  http://localhost:5000/lotes/vencimientos
  ```

---

## ❓ FAQ - Preguntas Frecuentes

### ¿Por qué el script de migración crea lotes sin fecha de vencimiento?

**Respuesta:** Porque no sabemos cuándo entró ese stock original. Puedes editar los lotes después y agregar fechas de vencimiento estimadas.

### ¿Puedo ejecutar la migración varias veces?

**Respuesta:** Sí, el script verifica si ya hay lotes y no crea duplicados. Es seguro ejecutarlo múltiples veces.

### ¿Qué pasa con artículos que se agreguen después de la migración?

**Respuesta:** Debes crear lotes manualmente cada vez que recibas mercancía nueva (método 2).

### ¿Puedo mezclar ambos métodos?

**Respuesta:** Sí. Primero ejecutas la migración para stock existente, luego creas lotes manualmente para nueva mercancía.

### ¿El sistema actualiza automáticamente el stock del artículo?

**Respuesta:** Sí. Al crear un lote, se actualiza `inventario.stock_actual`. Al consumir, se descuenta del lote y del artículo.

### ¿Qué pasa si tengo un artículo con stock 0?

**Respuesta:** La migración lo ignora (no crea lote). Cuando recibas mercancía, creas el primer lote manualmente.

---

## 🎯 Ejemplo Completo: De Cero a FIFO

### Estado Inicial

```sql
-- Artículo sin lotes
SELECT * FROM inventario WHERE id = 11;
-- id: 11
-- codigo: ART-00001
-- nombre: Filtro de aire
-- stock_actual: 2.00
-- precio_unitario: 15.00

SELECT * FROM lotes_inventario WHERE inventario_id = 11;
-- (vacío)
```

### Opción A: Migración Automática

```bash
$ python scripts/migrar_stock_a_lotes.py
# ... ejecuta migración ...
✅ Lote creado: LOTE-INICIAL-11-20241018
```

```sql
SELECT * FROM lotes_inventario WHERE inventario_id = 11;
-- id: 1
-- inventario_id: 11
-- codigo_lote: LOTE-INICIAL-11-20241018
-- cantidad_inicial: 2.00
-- cantidad_actual: 2.00
-- precio_unitario: 15.00
-- fecha_entrada: 2024-10-18 23:00:00
-- fecha_vencimiento: NULL
-- documento_origen: MIGRACIÓN INICIAL
```

### Opción B: Crear Manualmente

1. Ir a http://localhost:5000/lotes/crear_lote
2. Completar formulario
3. Submit

```sql
SELECT * FROM lotes_inventario WHERE inventario_id = 11;
-- id: 1
-- inventario_id: 11
-- codigo_lote: FILTROS-2024-OCT-001
-- cantidad_inicial: 2.00
-- cantidad_actual: 2.00
-- precio_unitario: 15.00
-- fecha_entrada: 2024-10-18 23:00:00
-- fecha_vencimiento: 2025-10-18
-- documento_origen: Stock inicial
```

### Resultado: ¡Sistema FIFO Activo!

```
Ahora puedes:
✅ Consumir material automáticamente con FIFO
✅ Reservar stock para órdenes de trabajo
✅ Ver trazabilidad completa
✅ Recibir alertas de vencimiento
```

---

## 📞 Soporte

Si tienes problemas con la generación de lotes:

1. Verifica la documentación completa: [docs/FIFO.md](FIFO.md)
2. Revisa los logs del sistema: `logs/app.log`
3. Ejecuta el script de verificación: `python scripts/verificar_lotes.py`
