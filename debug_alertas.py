#!/usr/bin/env python3
"""
Script simple para probar la carga de alertas en el navegador
"""
print(
    """
🔧 INSTRUCCIONES PARA DEBUGGEAR ALERTAS:

1. 📂 Abre el navegador en: http://127.0.0.1:5000
2. 🔑 Haz login con: admin / admin123  
3. 📊 Ve al Dashboard (si no estás ya)
4. 🛠️ Abre las herramientas de desarrollo (F12)
5. 📄 Ve a la pestaña "Console"
6. 🔍 Busca estos mensajes:

   ✅ MENSAJES ESPERADOS:
   - "🔍 Cargando alertas de mantenimiento..."
   - "📡 Respuesta recibida: 200 OK"
   - "📊 Datos de alertas: {success: true, ...}"
   - "✅ Cargando 2 alertas"
   - "🎨 Renderizando alertas: 2"
   - "✅ Alertas renderizadas exitosamente"

   ❌ MENSAJES DE ERROR:
   - "❌ Error cargando alertas de mantenimiento: ..."
   - "⚠️ Contenedor maintenanceAlerts no encontrado"
   - Cualquier error 401, 403, 500, etc.

7. 🔄 Si no ves los mensajes, recarga la página (F5)
8. 📋 Reporta qué mensajes ves exactamente

NOTAS:
- Las alertas deberían cargarse automáticamente
- Si ves "Cargando alertas..." por más de 5 segundos, hay un problema
- El reintento automático debería funcionar si hay errores
"""
)

# También vamos a verificar que el server esté ejecutándose
import requests

try:
    response = requests.get("http://127.0.0.1:5000", timeout=2)
    if response.status_code == 200:
        print("✅ Servidor Flask está ejecutándose correctamente en puerto 5000")
    else:
        print(f"⚠️ Servidor responde pero con código: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Servidor Flask no está ejecutándose!")
    print("   Ejecuta: python run.py")
except Exception as e:
    print(f"⚠️ Error verificando servidor: {e}")

print("\n" + "=" * 50)
print("Ahora abre el navegador y sigue las instrucciones de arriba ☝️")
