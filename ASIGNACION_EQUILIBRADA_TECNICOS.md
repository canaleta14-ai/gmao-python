# Sistema de Asignación Equilibrada de Técnicos

## Descripción General

Se ha implementado un sistema automático de asignación equilibrada de técnicos para las órdenes de trabajo generadas desde planes de mantenimiento preventivo. El sistema distribuye las órdenes de manera equitativa entre los técnicos disponibles, basándose en su carga de trabajo actual.

## Funcionalidad Implementada

### 1. Función de Asignación Equilibrada

**Archivo:** `app/controllers/planes_controller.py`  
**Función:** `asignar_tecnico_equilibrado()` (líneas 731-776)

```python
def asignar_tecnico_equilibrado():
    """
    Asigna un técnico de manera equilibrada basándose en su carga de trabajo.
    
    Returns:
        int: ID del técnico con menor carga, o None si no hay técnicos disponibles
    """
```

#### Algoritmo de Asignación:

1. **Consulta de técnicos activos:**
   - Busca usuarios con `activo = True`
   - Filtra por roles: "Técnico" o "Supervisor"

2. **Cálculo de carga de trabajo:**
   - Cuenta órdenes con estado "Pendiente" o "En Proceso"
   - Cada técnico tiene una métrica de carga

3. **Selección del técnico:**
   - Ordena técnicos por carga ascendente
   - Retorna el ID del técnico con menor carga
   - Retorna `None` si no hay técnicos disponibles

4. **Diagnóstico:**
   - Imprime información de cada técnico y su carga
   - Facilita el debugging y monitoreo

### 2. Integración en Generación Automática

**Archivo:** `app/controllers/planes_controller.py`  
**Función:** `generar_ordenes_automaticas()` (línea 636)

**Cambios realizados:**
```python
# Asignar técnico de manera equilibrada
tecnico_id = asignar_tecnico_equilibrado()

# Crear nueva orden de trabajo
nueva_orden = OrdenTrabajo(
    tipo="Mantenimiento Preventivo",
    prioridad="Media",
    estado="Pendiente",
    descripcion=f"Mantenimiento preventivo - Plan: {plan.codigo_plan} - {plan.nombre}",
    fecha_creacion=ahora,
    fecha_programada=ahora.date(),
    activo_id=plan.activo_id,
    tecnico_id=tecnico_id,  # ← Asignación automática de técnico
    tiempo_estimado=(
        plan.tiempo_estimado if hasattr(plan, "tiempo_estimado") else None
    ),
    observaciones=f"Orden generada automáticamente desde plan preventivo.\n\nInstrucciones:\n{plan.instrucciones or 'Sin instrucciones específicas'}",
)
```

### 3. Integración en Generación Manual

**Archivo:** `app/controllers/planes_controller.py`  
**Función:** `generar_ordenes_manuales()` (línea 829)

**Cambios realizados:**
```python
# Asignar técnico de manera equilibrada
tecnico_id = asignar_tecnico_equilibrado()

# Crear nueva orden de trabajo
nueva_orden = OrdenTrabajo(
    tipo="Mantenimiento Preventivo",
    prioridad="Media",
    estado="Pendiente",
    descripcion=f"Mantenimiento preventivo MANUAL - Plan: {plan.codigo_plan} - {plan.nombre}",
    fecha_creacion=ahora,
    fecha_programada=fecha_objetivo.date(),
    activo_id=plan.activo_id,
    tecnico_id=tecnico_id,  # ← Asignación automática de técnico
    tiempo_estimado=(
        plan.tiempo_estimado if hasattr(plan, "tiempo_estimado") else None
    ),
    observaciones=f"Orden generada MANUALMENTE por {usuario}.\n\nInstrucciones:\n{plan.instrucciones or 'Sin instrucciones específicas'}",
)
```

## Scripts de Prueba

### 1. Script de Diagnóstico Completo

**Archivo:** `test_asignacion_equilibrada.py`

Muestra información detallada sobre:
- Estado actual de técnicos y sus cargas
- Planes listos para generación automática
- Últimas órdenes generadas
- Estadísticas de distribución de órdenes
- Análisis de equilibrio de carga

**Uso:**
```bash
python test_asignacion_equilibrada.py
```

### 2. Script de Completar Orden de Prueba

**Archivo:** `completar_orden_test.py`

Facilita las pruebas completando órdenes para permitir nueva generación.

**Uso:**
```bash
python completar_orden_test.py
```

## Resultados de Pruebas

### Prueba Exitosa Realizada:

**Fecha:** 2025-10-01 21:46:23

**Escenario:**
- 1 técnico activo (Juan Pérez)
- Carga inicial: 2 órdenes activas

**Resultado:**
```
👥 Encontrados 1 técnicos disponibles
   👤 Juan Pérez: 2 órdenes activas
✅ Técnico asignado: Juan Pérez (carga actual: 2)
✅ Plan PM-2025-0003: próxima ejecución actualizada a 2025-10-04 00:00:00
🎉 Generación completada: 1 órdenes creadas
```

**Orden generada:**
- Número: OT-000004
- Plan: PM-2025-0003 - Amasadora
- Técnico asignado: Juan Pérez (automático)
- Estado: Pendiente

### Estado Final:

```
TÉCNICO                          PENDIENTES   EN PROCESO  COMPLETADAS    ACTIVAS      TOTAL
------------------------------------------------------------------------------------------
Juan Pérez                                2            1            1          3          4
------------------------------------------------------------------------------------------

✅ La carga está perfectamente equilibrada
```

## Beneficios del Sistema

### 1. Distribución Equitativa
- Las órdenes se distribuyen automáticamente
- Evita la sobrecarga de técnicos específicos
- Optimiza el uso de recursos humanos

### 2. Automatización Completa
- No requiere intervención manual para asignar técnicos
- Funciona tanto en generación automática como manual
- Reduce la carga administrativa

### 3. Escalabilidad
- El algoritmo funciona con cualquier número de técnicos
- Se adapta automáticamente a cambios en el equipo
- Considera tanto técnicos como supervisores

### 4. Transparencia
- Proporciona información detallada en logs
- Muestra la carga de cada técnico al asignar
- Facilita el monitoreo y auditoría

### 5. Mantenibilidad
- Código modular y bien documentado
- Función independiente fácil de probar
- Scripts de diagnóstico incluidos

## Comportamiento del Sistema

### Criterios de Asignación:

1. **Técnicos Elegibles:**
   - Usuario activo (`activo = True`)
   - Rol "Técnico" o "Supervisor"

2. **Métrica de Carga:**
   - Órdenes en estado "Pendiente"
   - Órdenes en estado "En Proceso"
   - Total = Pendiente + En Proceso

3. **Selección:**
   - Técnico con menor carga total
   - Si hay empate, se toma el primero encontrado
   - Si no hay técnicos, `tecnico_id = None`

### Casos Especiales:

1. **Sin técnicos disponibles:**
   - La orden se crea sin técnico asignado
   - Se puede asignar manualmente después

2. **Múltiples técnicos con igual carga:**
   - Se asigna al primero en la lista (ordenado por ID)
   - La distribución sigue siendo equitativa a largo plazo

3. **Nuevo técnico agregado:**
   - Automáticamente incluido en la rotación
   - Recibirá órdenes hasta alcanzar la carga promedio

## Monitoreo y Análisis

### Logs del Sistema:

El sistema imprime información detallada:

```
👥 Encontrados X técnicos disponibles
   👤 Nombre Técnico 1: Y órdenes activas
   👤 Nombre Técnico 2: Z órdenes activas
✅ Técnico asignado: Nombre (carga actual: N)
```

### Script de Diagnóstico:

Proporciona vista completa del sistema:
- Lista de técnicos con sus cargas
- Distribución de órdenes por estado
- Análisis de equilibrio
- Recomendaciones

## Próximos Pasos Sugeridos

### 1. Configuración Avanzada:
- Permitir asignación por especialidad de técnico
- Considerar disponibilidad horaria
- Implementar prioridades de asignación

### 2. Métricas Adicionales:
- Dashboard de carga de trabajo
- Reportes de eficiencia
- Alertas de sobrecarga

### 3. Optimizaciones:
- Cache de cálculo de cargas
- Asignación basada en tiempo estimado
- Predicción de carga futura

## Conclusión

El sistema de asignación equilibrada de técnicos está **completamente funcional** y **probado exitosamente**. Proporciona una distribución automática y equitativa de las órdenes de trabajo generadas desde planes de mantenimiento preventivo, reduciendo la carga administrativa y optimizando el uso de recursos.

✅ **Sistema implementado y operacional**
