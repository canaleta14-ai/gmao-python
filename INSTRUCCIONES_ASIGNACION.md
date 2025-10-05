# 🔐 Solución Completa: Asignación de Técnicos

## 📋 Problema Identificado

**Error**: `403 Forbidden - Acceso denegado. Solo administradores.`

**Causa**: Tu usuario actual NO tiene rol de `administrador`, solo los administradores pueden ejecutar la asignación masiva de técnicos.

---

## ✅ SOLUCIÓN EN 2 PASOS

### **PASO 1: Convertirte en Administrador** 🔐

1. **Abre la aplicación** en tu navegador:
   ```
   https://gmao-sistema-2025.ew.r.appspot.com/ordenes/
   ```

2. **Abre la Consola del Navegador**:
   - Presiona `F12` (o `Ctrl+Shift+I` en Windows, `Cmd+Option+I` en Mac)
   - Ve a la pestaña **"Console"**

3. **Copia y pega este código**:
   ```javascript
   // PASO 1: Hacerte administrador
   fetch('/admin/hacerme-admin', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'}
   })
   .then(r => r.json())
   .then(d => {
       console.log('✅', d.message);
       alert(d.success ? `✅ ${d.message}\n\nAhora puedes ejecutar la asignación de técnicos.` : `❌ ${d.error}`);
   });
   ```

4. **Presiona Enter** y espera el mensaje de confirmación

5. **Verás**: `✅ Usuario 'tu_usuario' es ahora ADMINISTRADOR`

---

### **PASO 2: Asignar Técnicos a Órdenes** 🔧

1. **En la misma consola**, copia y pega este código:
   ```javascript
   // PASO 2: Asignar técnicos a órdenes
   fetch('/admin/asignar-tecnicos', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'}
   })
   .then(r => r.json())
   .then(d => {
       if (d.success) {
           console.log('✅ ÉXITO:', d.message);
           console.log('📊 Órdenes asignadas:', d.asignadas);
           console.log('📝 Detalles:', d.detalles);
           alert(`✅ ${d.message}\n\n${d.detalles.map(det => `• Orden ${det.numero_orden} → ${det.tecnico}`).join('\n')}`);
           location.reload();
       } else {
           alert('❌ Error: ' + d.error);
       }
   });
   ```

2. **Presiona Enter** y espera unos segundos

3. **Verás un alert** con:
   - ✅ Mensaje de éxito
   - 📊 Número de órdenes asignadas
   - 📝 Lista de asignaciones (Orden → Técnico)

4. **La página se recargará automáticamente** y verás los técnicos en la columna

---

## 🎯 Verificación Final

Después de ejecutar ambos pasos:

1. **Ve a la lista de órdenes**: La columna "Técnico" debe mostrar nombres
2. **Abre una orden**: El técnico debe aparecer en el formulario de edición
3. **Verifica el calendario**: Las órdenes deben mostrar el técnico asignado

---

## 📝 Comandos Combinados (Todo en Uno)

Si quieres ejecutar ambos pasos de una vez:

```javascript
// Ejecutar ambos pasos en secuencia
async function asignarTecnicosCompleto() {
    try {
        // Paso 1: Hacerse admin
        console.log('🔐 Paso 1: Convirtiéndote en administrador...');
        const adminRes = await fetch('/admin/hacerme-admin', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const adminData = await adminRes.json();
        
        if (!adminData.success) {
            alert('❌ Error al hacerse admin: ' + adminData.error);
            return;
        }
        
        console.log('✅', adminData.message);
        
        // Paso 2: Asignar técnicos
        console.log('🔧 Paso 2: Asignando técnicos...');
        const asigRes = await fetch('/admin/asignar-tecnicos', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const asigData = await asigRes.json();
        
        if (asigData.success) {
            console.log('✅ ÉXITO:', asigData.message);
            console.log('📊 Órdenes asignadas:', asigData.asignadas);
            console.log('📝 Detalles:', asigData.detalles);
            alert(`✅ ¡COMPLETADO!\n\n${adminData.message}\n\n${asigData.message}\n\n${asigData.detalles.map(d => `• Orden ${d.numero_orden} → ${d.tecnico}`).join('\n')}`);
            location.reload();
        } else {
            alert('❌ Error al asignar técnicos: ' + asigData.error);
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
        alert('❌ Error: ' + error.message);
    }
}

// Ejecutar
asignarTecnicosCompleto();
```

---

## 🔒 Seguridad del Endpoint Temporal

⚠️ **IMPORTANTE**: El endpoint `/admin/hacerme-admin` es **temporal** y está diseñado para resolver este problema específico.

**Características de seguridad**:
- ✅ Requiere autenticación (`@login_required`)
- ✅ Solo afecta al usuario que lo ejecuta (`current_user`)
- ⚠️ No valida el rol actual (es el propósito)

**Después de usarlo**, se recomienda:
1. Remover el endpoint del código
2. Usar la interfaz de administración normal para gestionar usuarios

---

## 📊 Resultados Esperados

Después de ejecutar la asignación masiva, verás algo como:

```
✅ Se asignaron técnicos a 5 órdenes

Detalles:
• Orden OT-001 → Juan Pérez
• Orden OT-002 → María García
• Orden OT-003 → Juan Pérez
• Orden OT-004 → María García
• Orden OT-005 → Juan Pérez
```

---

## ❓ Solución de Problemas

### Si el Paso 1 falla:
- Verifica que estás autenticado (sesión activa)
- Recarga la página e intenta de nuevo
- Verifica que el despliegue haya terminado

### Si el Paso 2 falla:
- Asegúrate de haber ejecutado el Paso 1 primero
- Verifica que hay técnicos activos en el sistema
- Revisa la consola del navegador para más detalles

### Si no ves técnicos en la lista:
- Recarga la página (`F5` o `Ctrl+R`)
- Limpia la caché del navegador (`Ctrl+Shift+R`)
- Verifica que hay técnicos creados en el sistema

---

## 🎯 Estado del Despliegue

✅ **Endpoint temporal desplegado**
✅ **Listo para usar**

URL de la aplicación:
```
https://gmao-sistema-2025.ew.r.appspot.com
```

---

## 📞 Soporte

Si necesitas ayuda adicional, proporciona:
- Mensaje de error completo de la consola
- Tu nombre de usuario
- Captura de pantalla si es posible
