# Guía Rápida: Gestión de Repuestos en Órdenes de Trabajo

## 📋 Resumen Ejecutivo

El sistema GMAO **YA TIENE** la funcionalidad completa para descontar repuestos directamente desde las órdenes de trabajo y mantener un control exacto del inventario.

## 🎯 Funcionalidad Principal

### ¿Qué puedes hacer?

✅ **Agregar repuestos** a cualquier orden de trabajo  
✅ **Ver stock disponible** en tiempo real  
✅ **Descontar automáticamente** al completar la orden  
✅ **Descontar manualmente** cuando lo necesites  
✅ **Rastrear completamente** quién, cuándo y cuánto  

---

## 🚀 Guía de Uso - Paso a Paso

### Paso 1: Abrir una Orden de Trabajo

1. Ir a **Órdenes de Trabajo**
2. Hacer clic en una orden existente o crear una nueva
3. En el modal de detalles, buscar la sección **"Recambios y Repuestos"**

### Paso 2: Agregar Repuestos

1. Hacer clic en botón **"+ Agregar Recambio"**
2. En el modal que se abre:
   - **Artículo/Repuesto:** Escribir código o descripción
   - Sistema mostrará sugerencias con autocompletado
   - Seleccionar el artículo deseado
   - Ver **stock actual** del artículo
3. **Cantidad Solicitada:** Ingresar cantidad que se necesita
4. **Cantidad Utilizada:** (Opcional) Se puede especificar después
5. **Observaciones:** (Opcional) Notas adicionales
6. Clic en **"Agregar"**

### Paso 3: Ver Repuestos Asignados

La orden ahora muestra una tabla con:

```
┌─────────────┬──────────────────┬────────────┬────────────┬──────────┐
│ Artículo    │ Descripción      │ Solicitado │ Utilizado  │ Estado   │
├─────────────┼──────────────────┼────────────┼────────────┼──────────┤
│ REP-001     │ Filtro de aire   │ 2          │ 2          │ ✅ OK    │
│ REP-015     │ Rodamiento       │ 4          │ -          │ ⏳ Pend. │
└─────────────┴──────────────────┴────────────┴────────────┴──────────┘
```

### Paso 4A: Descuento Automático (Recomendado)

1. Completar el trabajo de mantenimiento
2. Cambiar estado de la orden a **"Completada"**
3. ✨ **El sistema automáticamente:**
   - Descuenta todos los repuestos pendientes
   - Actualiza el inventario
   - Crea movimientos de inventario
   - Registra fecha y usuario

**¡Listo! Sin pasos adicionales.**

### Paso 4B: Descuento Manual (Alternativa)

1. Completar el trabajo
2. En la sección de repuestos, clic en **"Descontar del Stock"**
3. Confirmar en el modal
4. Sistema procesa cada repuesto:
   - ✅ Descuenta los que tienen stock
   - ❌ Muestra error si falta stock
   - Continúa con los demás

---

## 💡 Casos de Uso Comunes

### Caso 1: Mantenimiento Preventivo Rutinario

**Situación:** Cambio de filtros programado

**Pasos:**
1. Abrir orden de mantenimiento preventivo
2. Agregar repuestos:
   - Filtro de aire (1 unidad)
   - Filtro de aceite (1 unidad)
3. Realizar el trabajo
4. Completar orden → Descuento automático ✨

**Resultado:** Inventario actualizado, trabajo completado

---

### Caso 2: Reparación con Cantidad Variable

**Situación:** No se sabe exactamente cuánto se va a usar

**Pasos:**
1. Agregar repuesto con cantidad estimada: Grasa (5 kg)
2. Durante el trabajo: Solo se usan 3 kg
3. Antes de descontar: Actualizar cantidad utilizada a 3 kg
4. Descontar → Solo se descuentan 3 kg

**Resultado:** Stock refleja consumo real

---

### Caso 3: Stock Insuficiente

**Situación:** Se necesita un repuesto que no hay en stock

**Pasos:**
1. Intentar agregar repuesto
2. Sistema muestra: "Stock actual: 0 unidades"
3. Opciones:
   - Comprar repuesto primero
   - O agregar de todos modos y descuento fallará con mensaje claro

**Resultado:** Sistema previene descuadres

---

## 🔍 Dónde Ver la Información

### En la Orden de Trabajo:
- Lista completa de repuestos
- Estado de cada uno (descontado/pendiente)
- Costo total de repuestos

### En Inventario:
- Movimientos tipo "salida - orden_trabajo"
- Documento referencia: "OT-{número}"
- Observaciones con detalles

### En Reportes:
- Consumo de repuestos por período
- Costo de mantenimiento por activo
- Órdenes con repuestos pendientes

---

## ⚙️ Configuración del Sistema

### Modo Actual: HÍBRIDO

El sistema está configurado para:
- ✅ Descuento automático al completar orden
- ✅ Botón manual disponible por si se necesita

### Ventajas del Modo Híbrido:
- **Técnicos olvadizos:** El descuento automático asegura que se registre
- **Casos especiales:** El botón manual permite flexibilidad
- **Mejor de ambos mundos**

---

## 📊 Información Técnica para Administradores

### Validaciones Activas:

1. ✅ Stock suficiente para descontar
2. ✅ No descontar dos veces el mismo repuesto
3. ✅ No eliminar repuestos ya descontados
4. ✅ Orden debe existir y ser válida

### Auditoría Registrada:

Cada descuento genera:
- **Movimiento de inventario** con todos los detalles
- **Timestamp** exacto
- **Usuario** que realizó la acción
- **Precio** en el momento del descuento
- **Cantidad** antes y después

### Base de Datos:

```
orden_recambio
├─ id
├─ orden_trabajo_id
├─ inventario_id
├─ cantidad_solicitada
├─ cantidad_utilizada
├─ descontado (BOOLEAN)
├─ fecha_descuento
└─ usuario_id
```

---

## ❓ Preguntas Frecuentes

### ¿Puedo descontar un repuesto dos veces?
❌ **No.** El sistema tiene un flag `descontado` que lo previene.

### ¿Qué pasa si no hay stock?
⚠️ El sistema muestra error específico y no descuenta ese repuesto, pero continúa con los demás.

### ¿Puedo eliminar un repuesto ya descontado?
❌ **No.** Para mantener integridad de datos. Se debe hacer ajuste de inventario.

### ¿Se puede desactivar el descuento automático?
✅ **Sí.** Comentar línea 360 en `static/js/ordenes.js`

### ¿Los repuestos tienen costo?
✅ **Sí.** Se captura el precio promedio del inventario al momento de agregar el repuesto.

### ¿Puedo ver el historial?
✅ **Sí.** En Inventario → Movimientos, filtrar por tipo "orden_trabajo"

---

## 🎓 Tips y Mejores Prácticas

### 1. Agregar Repuestos Antes de Empezar
- Facilita planificación
- Asegura disponibilidad
- Mejor control

### 2. Actualizar Cantidad Utilizada
- Especialmente si difiere de la solicitada
- Stock más preciso
- Costeo más exacto

### 3. Usar Observaciones
- Documentar razón del uso
- Notas técnicas importantes
- Facilita auditorías

### 4. Revisar Antes de Completar
- Verificar que todos los repuestos estén agregados
- Confirmar cantidades
- Descuento automático será preciso

### 5. Monitorear Stock Mínimo
- Configurar alertas en inventario
- Reponer antes de quedarse sin stock
- Evitar interrupciones

---

## 📞 Soporte

### Archivos de Documentación:
- **`SISTEMA_REPUESTOS_ORDENES.md`** - Documentación técnica completa
- **`GUIA_RAPIDA_REPUESTOS.md`** - Esta guía (usuario final)

### Archivos de Código:
- **Frontend:** `static/js/ordenes.js` (líneas 1750-1920)
- **Backend:** `app/controllers/orden_recambios_controller.py`
- **Modelo:** `app/models/orden_recambio.py`
- **API:** `app/routes/recambios.py`

### Consultas SQL de Diagnóstico:

```sql
-- Ver repuestos pendientes de descontar
SELECT * FROM orden_recambio WHERE descontado = FALSE;

-- Movimientos de hoy
SELECT * FROM movimiento_inventario 
WHERE DATE(fecha) = CURRENT_DATE 
AND subtipo = 'orden_trabajo';
```

---

## ✅ Resumen Final

### El Sistema YA ESTÁ COMPLETO

No necesitas:
- ❌ Desarrollar nuevas funcionalidades
- ❌ Instalar módulos adicionales
- ❌ Configuraciones complejas

Solo necesitas:
- ✅ Empezar a usar las órdenes de trabajo
- ✅ Agregar repuestos según se usen
- ✅ Completar las órdenes
- ✅ El sistema hará el resto

### Control Exacto del Inventario

Con este sistema tienes:
- 📊 **Trazabilidad completa:** Quién, qué, cuándo, cuánto
- 💰 **Costeo preciso:** Precio capturado al momento
- 🔒 **Auditoría robusta:** Todo registrado
- ⚡ **Automático:** Sin pasos manuales extra
- 🎯 **Exacto:** Sin descuadres ni errores

---

**¡El sistema está listo para usar!** 🚀

Fecha: 1 de octubre de 2025  
Versión: 1.0  
Estado: ✅ Operacional
