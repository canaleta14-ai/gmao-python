# 📅 Sistema de Generación Automática de Órdenes - GMAO

## 🎯 **Funcionalidad Implementada**

### ✅ **Generación Automática a las 6:00 AM**
- **Horario fijo:** Todos los días a las 6:00 AM
- **Propósito:** Generar órdenes de trabajo para mantenimientos preventivos vencidos
- **Alcance:** Procesa todos los planes activos que tienen `próxima_ejecución <= fecha_actual`

### ✅ **Calendario Visual de Órdenes**
- **URL:** `/calendario`
- **Características:**
  - Vista de calendario interactivo con FullCalendar
  - Diferentes colores por estado de órdenes
  - Visualización de planes futuros (color púrpura)
  - Estadísticas del mes en tiempo real
  - Botón para generar órdenes manualmente

## 🚀 **Cómo Usar el Sistema**

### **1. Configuración Automática (Recomendado)**
```bash
# Ejecutar como Administrador
setup_scheduler_windows.bat
```
Esto configurará:
- ✅ Dependencias necesarias
- ✅ Tarea programada en Windows Task Scheduler  
- ✅ Ejecución diaria a las 6:00 AM
- ✅ Logs automáticos en carpeta `/logs`

### **2. Uso Manual**
```bash
# Ejecutar una vez (para pruebas)
python scheduler_simple.py --test

# Ver estado del próximo scheduler
python scheduler_simple.py --status

# Iniciar scheduler continuo
python scheduler_simple.py
```

### **3. Acceso al Calendario**
- **Interfaz Web:** http://localhost:5000/calendario
- **Menú:** Navegación → "Calendario de Órdenes"
- **Funciones:** Ver órdenes, generar manualmente, estadísticas

## 📊 **Calendario de Órdenes - Características**

### **Colores del Calendario:**
- 🟡 **Amarillo:** Órdenes Pendientes
- 🔵 **Azul:** Órdenes En Proceso  
- 🟢 **Verde:** Órdenes Completadas
- 🔴 **Rojo:** Órdenes Canceladas
- 🟣 **Púrpura:** Planes Futuros (se generarán automáticamente)

### **Estadísticas en Tiempo Real:**
- Total de órdenes del mes
- Planes programados
- Contadores por estado
- Navegación por meses/años

### **Acciones Disponibles:**
- **Ver detalles:** Click en cualquier evento
- **Generar órdenes:** Botón "Generar Órdenes Hoy"
- **Actualizar:** Refrescar datos del calendario

## 🔧 **Administración del Sistema**

### **Comandos de Task Scheduler:**
```bash
# Ver estado de la tarea
schtasks /query /tn "GMAO_GenerarOrdenes"

# Ejecutar manualmente
schtasks /run /tn "GMAO_GenerarOrdenes"

# Eliminar tarea (si necesario)
schtasks /delete /tn "GMAO_GenerarOrdenes" /f

# Ver logs
type logs\\scheduler_ordenes.log
```

### **Verificar Funcionamiento:**
```bash
# 1. Probar generación manual
python scheduler_simple.py --test

# 2. Verificar que encuentra planes vencidos
# (Debe mostrar mensaje como "Encontrados X planes vencidos")

# 3. Revisar logs
type logs\\scheduler_ordenes.log

# 4. Verificar en calendario web
# http://localhost:5000/calendario
```

## 📋 **Lógica del Sistema**

### **Proceso de Generación:**
1. **6:00 AM diariamente** → Se ejecuta automáticamente
2. **Buscar planes vencidos** → `proxima_ejecucion <= fecha_actual`
3. **Verificar duplicados** → No crear si ya existe orden pendiente
4. **Crear órdenes nuevas** → Con datos del plan y activo asociado
5. **Actualizar próxima ejecución** → Calcular siguiente fecha según frecuencia
6. **Registrar en logs** → Guardar estadísticas y detalles

### **Criterios de Planes Vencidos:**
- ✅ Estado = "Activo"
- ✅ `proxima_ejecucion` <= fecha/hora actual
- ✅ No existe orden pendiente para el mismo plan+activo

### **Datos de Órdenes Generadas:**
- **Tipo:** "Mantenimiento Preventivo"
- **Estado:** "Pendiente" 
- **Prioridad:** "Media"
- **Descripción:** "Mantenimiento preventivo - Plan: {codigo} - {nombre}"
- **Fecha programada:** Fecha actual
- **Activo:** Asociado al plan
- **Instrucciones:** Copiadas del plan

## 🔍 **Solución de Problemas**

### **Si no se generan órdenes:**
1. Verificar que existen planes con `proxima_ejecucion` vencida
2. Comprobar que los planes están en estado "Activo"
3. Revisar logs: `logs\\scheduler_ordenes.log`
4. Ejecutar prueba manual: `python scheduler_simple.py --test`

### **Si el calendario no muestra datos:**
1. Verificar que el servidor Flask está ejecutándose
2. Abrir navegador en `http://localhost:5000/calendario`
3. Revisar consola del navegador (F12) para errores JavaScript
4. Comprobar que existen órdenes en la base de datos

### **Si Task Scheduler no funciona:**
1. Ejecutar `setup_scheduler_windows.bat` como Administrador
2. Verificar en Panel de Control → Herramientas Administrativas → Programador de tareas
3. Buscar tarea "GMAO_GenerarOrdenes"
4. Revisar historial de ejecución

## ✅ **Estado Actual Confirmado**

### **Funcionalidades Operativas:**
- ✅ Función `generar_ordenes_automaticas()` funcionando
- ✅ Endpoint `/planes/api/generar-ordenes` disponible  
- ✅ Scheduler simple con threading funcionando
- ✅ Calendario web con FullCalendar funcionando
- ✅ Task Scheduler de Windows configurado
- ✅ Sistema de logs implementado

### **Próximas Ejecuciones:**
- **Mañana (29/09/2025) a las 6:00 AM** → Primera ejecución automática
- **Cada día a las 6:00 AM** → Generación continua

### **Resultado de Pruebas:**
```
✅ Plan PM-2025-0001: próxima ejecución actualizada a 2025-09-29 06:00:00
🎉 Generación completada: 1 órdenes creadas
📋 Orden generada: OT-000005 (Mantenimiento preventivo - Plan: PM-2025-0001 - Horno)
```

## 🎯 **Resumen para el Usuario**

**¡Ya no necesitas preocuparte por generar órdenes manualmente!**

1. **Automático:** Cada día a las 6:00 AM se generan las órdenes necesarias
2. **Visual:** Usa el calendario para ver todas las órdenes programadas  
3. **Manual:** Puedes generar órdenes adicionales cuando lo necesites
4. **Monitoreo:** Los logs te muestran qué se ha procesado cada día

**El sistema está listo y funcionando. Mañana a las 6:00 AM verás la primera ejecución automática.**