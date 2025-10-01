# 🎨 Demostración Visual: Sistema de Checkboxes

**Guía Visual Paso a Paso del Sistema de Selección Masiva**

---

## 📺 Vista Inicial (Sin Selección)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🖥️  Gestión de Activos                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Listado de Activos    [0 activos]                          │
│                                                                 │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║ [ ]  Código  Departamento  Activo  Tipo  Estado  ...     ║ │
│  ╠═══════════════════════════════════════════════════════════╣ │
│  ║ [ ]  001A01  Producción    Motor   Máq.  Operativo  ...  ║ │
│  ║ [ ]  001A02  Producción    Bomba   Máq.  Operativo  ...  ║ │
│  ║ [ ]  002A01  Calidad       Sensor  Ins.  Operativo  ...  ║ │
│  ║ [ ]  003A01  Mantenimiento Grúa    Veh.  En Mant.   ...  ║ │
│  ║ [ ]  003A02  Mantenimiento Carro   Veh.  Operativo  ...  ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────────┘
```

**Estado:**
- ❌ Sin selección
- ❌ Contador oculto
- ❌ Barra de acciones oculta

---

## 📺 Vista con 1 Elemento Seleccionado

```
┌─────────────────────────────────────────────────────────────────┐
│ 🖥️  Gestión de Activos                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Listado de Activos    [5 activos]  🔵 1 seleccionado       │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 🟢 Operativo  🟡 Manten.  🔵 Prioridad  📥 Export  🗑️ Elim │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║ [-]  Código  Departamento  Activo  Tipo  Estado  ...     ║ │
│  ╠═══════════════════════════════════════════════════════════╣ │
│  ║ [✓]  001A01  Producción    Motor   Máq.  Operativo  ...  ║ │ ← Seleccionado (fondo azul)
│  ║ [ ]  001A02  Producción    Bomba   Máq.  Operativo  ...  ║ │
│  ║ [ ]  002A01  Calidad       Sensor  Ins.  Operativo  ...  ║ │
│  ║ [ ]  003A01  Mantenimiento Grúa    Veh.  En Mant.   ...  ║ │
│  ║ [ ]  003A02  Mantenimiento Carro   Veh.  Operativo  ...  ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────────┘
```

**Estado:**
- ✅ 1 elemento seleccionado
- ✅ Contador visible: "🔵 1 seleccionado"
- ✅ Barra de acciones visible
- ✅ Checkbox encabezado: estado intermedio "[-]"
- ✅ Fila seleccionada: fondo azul claro

---

## 📺 Vista con Todos Seleccionados

```
┌─────────────────────────────────────────────────────────────────┐
│ 🖥️  Gestión de Activos                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Listado de Activos    [5 activos]  🔵 5 seleccionados      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 🟢 Operativo  🟡 Manten.  🔵 Prioridad  📥 Export  🗑️ Elim │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║ [✓]  Código  Departamento  Activo  Tipo  Estado  ...     ║ │ ← Todos marcados
│  ╠═══════════════════════════════════════════════════════════╣ │
│  ║ [✓]  001A01  Producción    Motor   Máq.  Operativo  ...  ║ │ ← Fondo azul
│  ║ [✓]  001A02  Producción    Bomba   Máq.  Operativo  ...  ║ │ ← Fondo azul
│  ║ [✓]  002A01  Calidad       Sensor  Ins.  Operativo  ...  ║ │ ← Fondo azul
│  ║ [✓]  003A01  Mantenimiento Grúa    Veh.  En Mant.   ...  ║ │ ← Fondo azul
│  ║ [✓]  003A02  Mantenimiento Carro   Veh.  Operativo  ...  ║ │ ← Fondo azul
│  ╚═══════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────────┘
```

**Estado:**
- ✅ 5 elementos seleccionados
- ✅ Contador: "🔵 5 seleccionados"
- ✅ Barra de acciones visible
- ✅ Checkbox encabezado: marcado "[✓]"
- ✅ Todas las filas: fondo azul claro

---

## 📺 Modal de Confirmación (Cambiar Estado)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│       ┌─────────────────────────────────────────┐              │
│       │ ⚠️  ¿Cambiar estado a "Operativo"?      │              │
│       ├─────────────────────────────────────────┤              │
│       │                                         │              │
│       │ Se cambiará el estado de 3 activo(s)   │              │
│       │ a "Operativo".                          │              │
│       │                                         │              │
│       │ [Cancelar]            [✓ Confirmar]     │              │
│       └─────────────────────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Flujo:**
1. Usuario selecciona 3 activos
2. Click en botón "🟢 Operativo"
3. Aparece modal de confirmación
4. Click en "Confirmar"
5. Se ejecuta acción masiva
6. Mensaje de éxito
7. Tabla actualizada

---

## 📺 Modal de Cambiar Prioridad

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│       ┌─────────────────────────────────────────┐              │
│       │ 🏁 Cambiar Prioridad                    │              │
│       ├─────────────────────────────────────────┤              │
│       │                                         │              │
│       │ Seleccione la nueva prioridad para     │              │
│       │ 3 activo(s):                            │              │
│       │                                         │              │
│       │ ┌─────────────────────────────────────┐ │              │
│       │ │ [ ] Baja                            │ │              │
│       │ │ [ ] Media                           │ │              │
│       │ │ [✓] Alta          ← Seleccionada    │ │              │
│       │ │ [ ] Crítica                         │ │              │
│       │ └─────────────────────────────────────┘ │              │
│       │                                         │              │
│       │ [Cancelar]            [✓ Cambiar]       │              │
│       └─────────────────────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Flujo:**
1. Usuario selecciona activos
2. Click en botón "🔵 Prioridad"
3. Aparece modal con selector
4. Usuario selecciona "Alta"
5. Click en "Cambiar"
6. Se ejecuta acción masiva
7. Tabla actualizada con nueva prioridad

---

## 📺 Mensaje de Éxito

```
┌─────────────────────────────────────────────────────────────────┐
│ 🖥️  Gestión de Activos                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ ✅ 3 activo(s) actualizado(s) exitosamente               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  📊 Listado de Activos    [5 activos]                          │
│                                                                 │
│  ╔═══════════════════════════════════════════════════════════╗ │
│  ║ [ ]  Código  Departamento  Activo  Tipo  Estado  ...     ║ │
│  ╠═══════════════════════════════════════════════════════════╣ │
│  ║ [ ]  001A01  Producción    Motor   Máq.  ✅ Operativo ... ║ │ ← Actualizado
│  ║ [ ]  001A02  Producción    Bomba   Máq.  ✅ Operativo ... ║ │ ← Actualizado
│  ║ [ ]  002A01  Calidad       Sensor  Ins.  ✅ Operativo ... ║ │ ← Actualizado
│  ║ [ ]  003A01  Mantenimiento Grúa    Veh.  En Mant.   ...  ║ │
│  ║ [ ]  003A02  Mantenimiento Carro   Veh.  Operativo  ...  ║ │
│  ╚═══════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────────┘
```

**Resultado:**
- ✅ Mensaje de éxito (verde)
- ✅ Tabla actualizada
- ✅ Selección limpiada
- ✅ Contador oculto
- ✅ Barra de acciones oculta

---

## 🎬 Animaciones

### Aparecer Barra de Acciones
```
Estado 1 (Sin selección):
┌──────────────────────────────────────────┐
│ 📊 Listado de Activos    [5 activos]    │
└──────────────────────────────────────────┘

       ↓ Click en checkbox (0.3s animación)

Estado 2 (Con selección):
┌──────────────────────────────────────────┐
│ 📊 Listado de Activos    🔵 1 seleccionado│
│ ┌────────────────────────────────────┐   │
│ │ 🟢 Operativo  🟡 Manten.  ...      │   │ ← Aparece con slideDown
│ └────────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

### Seleccionar Fila
```
Antes:                           Después:
────────────────────────         ═══════════════════════
[ ] 001A01  Motor  ...    →→→    [✓] 001A01  Motor  ...
────────────────────────         ═══════════════════════
                                 ↑ Fondo azul #e7f3ff
                                 ↑ Transición 0.2s
```

### Contador Actualizado
```
Selección 0 → 1:
[oculto]  →  🔵 1 seleccionado  (fadeIn 0.3s)

Selección 1 → 2:
🔵 1 seleccionado  →  🔵 2 seleccionados  (actualización instantánea)

Selección 2 → 0:
🔵 2 seleccionados  →  [oculto]  (fadeOut 0.3s)
```

---

## 🎨 Colores y Badges

### Estados de Activos
```
🟢 Operativo          → Verde   (bg-success)
🟡 En Mantenimiento   → Amarillo (bg-warning)
🔴 Fuera de Servicio  → Rojo    (bg-danger)
🔵 En Reparación      → Azul    (bg-info)
⚫ Inactivo           → Gris    (bg-secondary)
```

### Prioridades
```
🟢 Baja     → Verde   (bg-success)
🔵 Media    → Azul    (bg-primary)
🟡 Alta     → Amarillo (bg-warning)
🔴 Crítica  → Rojo    (bg-danger)
```

### Botones de Acción
```
🟢 Operativo         → btn-success
🟡 Mantenimiento     → btn-warning
🔵 Prioridad         → btn-info
📥 Exportar          → btn-primary
🗑️ Eliminar          → btn-danger
```

---

## 📱 Vista Responsive (Móvil)

```
┌─────────────────────┐
│ 🖥️  Gestión Activos │
├─────────────────────┤
│ 📊 Activos          │
│ [5] 🔵 2 selec.     │
│ ┌─────────────────┐ │
│ │🟢🟡🔵📥🗑️       │ │ ← Botones más pequeños
│ └─────────────────┘ │
│                     │
│ ╔═══════════════╗   │
│ ║ [-] Código    ║   │
│ ╠═══════════════╣   │
│ ║ [✓] 001A01    ║   │ ← Columnas ajustadas
│ ║     Motor     ║   │
│ ║     Operativo ║   │
│ ╟───────────────╢   │
│ ║ [ ] 001A02    ║   │
│ ║     Bomba     ║   │
│ ║     Operativo ║   │
│ ╚═══════════════╝   │
└─────────────────────┘
```

**Adaptaciones móvil:**
- Botones más compactos
- Solo iconos (sin texto)
- Columnas apiladas verticalmente
- Scroll horizontal si es necesario

---

## 🔄 Flujo Completo de Uso

```
┌─────────────┐
│   INICIO    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ Usuario ve tabla vacía  │
│ Sin checkboxes marcados │
└──────────┬──────────────┘
           │
           ▼
    ┌──────────────┐
    │ Seleccionar? │
    └──┬───────┬───┘
       │       │
  Individual  Todos
       │       │
       ▼       ▼
┌──────────┐ ┌─────────────┐
│ Click en │ │ Click en    │
│ checkbox │ │ checkbox    │
│ de fila  │ │ encabezado  │
└────┬─────┘ └──────┬──────┘
     │              │
     └──────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Fila marcada  │
    │ Fondo azul    │
    │ Contador ↑    │
    │ Barra aparece │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Elegir acción │
    └───┬───────────┘
        │
   ┌────┴────┬─────────┬──────────┬─────────┐
   │         │         │          │         │
   ▼         ▼         ▼          ▼         ▼
┌──────┐ ┌──────┐ ┌─────────┐ ┌──────┐ ┌──────┐
│Estado│ │Estado│ │Prioridad│ │Export│ │Elimi-│
│Operat│ │Mant. │ │         │ │CSV   │ │nar   │
└──┬───┘ └──┬───┘ └────┬────┘ └──┬───┘ └──┬───┘
   │        │          │         │        │
   │        │          ▼         │        │
   │        │    ┌──────────┐    │        │
   │        │    │Modal con │    │        │
   │        │    │selector  │    │        │
   │        │    └────┬─────┘    │        │
   │        │         │          │        │
   └────────┴─────────┴──────────┴────────┘
            │
            ▼
    ┌───────────────┐
    │ Modal         │
    │ confirmación  │
    └───────┬───────┘
            │
       ┌────┴────┐
       │         │
    Cancelar  Confirmar
       │         │
       │         ▼
       │   ┌──────────────┐
       │   │ Ejecutar     │
       │   │ API calls    │
       │   └──────┬───────┘
       │          │
       │          ▼
       │   ┌──────────────┐
       │   │ Mensaje      │
       │   │ éxito/error  │
       │   └──────┬───────┘
       │          │
       │          ▼
       │   ┌──────────────┐
       │   │ Actualizar   │
       │   │ tabla        │
       │   │ estadísticas │
       │   └──────┬───────┘
       │          │
       └──────────┘
            │
            ▼
    ┌───────────────┐
    │ Limpiar       │
    │ selección     │
    │ Ocultar barra │
    └───────┬───────┘
            │
            ▼
       ┌─────────┐
       │   FIN   │
       └─────────┘
```

---

## 🎯 Casos de Uso Visuales

### Caso 1: Cambiar Estado de Múltiples Activos

```
ANTES:
╔════════════════════════════════╗
║ Activo          │ Estado       ║
╠════════════════════════════════╣
║ Motor Bomba 1   │ 🔴 Fuera    ║ ← Necesita cambiar
║ Motor Bomba 2   │ 🔴 Fuera    ║ ← Necesita cambiar
║ Motor Bomba 3   │ 🔴 Fuera    ║ ← Necesita cambiar
║ Sensor Temp     │ 🟢 Operativo ║
║ Grúa Principal  │ 🟡 Manten.   ║
╚════════════════════════════════╝

ACCIÓN:
1. [✓] Seleccionar Motor Bomba 1, 2, 3
2. Click → 🟢 Operativo
3. Confirmar

DESPUÉS:
╔════════════════════════════════╗
║ Activo          │ Estado       ║
╠════════════════════════════════╣
║ Motor Bomba 1   │ 🟢 Operativo ║ ← Actualizado ✓
║ Motor Bomba 2   │ 🟢 Operativo ║ ← Actualizado ✓
║ Motor Bomba 3   │ 🟢 Operativo ║ ← Actualizado ✓
║ Sensor Temp     │ 🟢 Operativo ║
║ Grúa Principal  │ 🟡 Manten.   ║
╚════════════════════════════════╝

Ahorro: 9 clicks → 5 clicks (44% menos)
```

### Caso 2: Exportar Activos Específicos

```
NECESIDAD:
Exportar solo activos de departamento "Producción"
para reporte de auditoria

PASOS:
1. Filtrar por departamento: Producción
   ╔════════════════════════════════╗
   ║ [✓] 001A01  Motor Bomba      ║
   ║ [✓] 001A02  Compresor        ║
   ║ [✓] 001A03  Caldera          ║
   ║ [✓] 001A04  Sistema Cooling  ║
   ╚════════════════════════════════╝

2. Click en checkbox encabezado → Seleccionar todos

3. Click → 📥 Exportar

4. Archivo descargado:
   📄 activos_seleccionados_2025-10-01.csv
   
   Código,Nombre,Departamento,Tipo,Estado,...
   001A01,Motor Bomba,Producción,Máquina,Operativo,...
   001A02,Compresor,Producción,Máquina,Operativo,...
   001A03,Caldera,Producción,Máquina,En Mant.,...
   001A04,Sistema Cooling,Producción,Equipo,Operativo,...

Tiempo total: ~15 segundos
vs Copiar/pegar manual: ~10 minutos
```

---

## 🎪 Estados del Checkbox Principal

### Estado 1: Ninguno Seleccionado
```
┌────────┐
│ [ ]    │  ← Vacío
└────────┘
```

### Estado 2: Algunos Seleccionados (Intermedio)
```
┌────────┐
│ [-]    │  ← Línea horizontal
└────────┘
```

### Estado 3: Todos Seleccionados
```
┌────────┐
│ [✓]    │  ← Check completo
└────────┘
```

---

## 📊 Métricas Visuales

### Contador Dinámico
```
0 seleccionados:  [OCULTO]

1 seleccionado:   🔵 1 seleccionado    ← Singular

2 seleccionados:  🔵 2 seleccionados   ← Plural

10 seleccionados: 🔵 10 seleccionados

100 seleccionados: 🔵 100 seleccionados
```

### Barra de Progreso (Durante Acción)
```
Ejecutando acción masiva:

┌─────────────────────────────────────┐
│ ⏳ Procesando 15 activos...         │
│ ████████████████░░░░░░░ 60%        │
│ 9 de 15 completados                │
└─────────────────────────────────────┘
```

---

## 🎉 Conclusión Visual

Este sistema proporciona una interfaz **intuitiva, moderna y eficiente** para gestionar múltiples elementos simultáneamente.

**Características clave:**
- ✅ Feedback visual inmediato
- ✅ Animaciones suaves
- ✅ Confirmaciones claras
- ✅ Mensajes informativos
- ✅ Responsive en todos los dispositivos

---

**Para ver en acción:** http://localhost:5000/activos

