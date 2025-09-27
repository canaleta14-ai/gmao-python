#!/usr/bin/env python3
"""
Script simple para probar la carga de alertas en el navegador
"""
print(
    """
ğŸ”§ INSTRUCCIONES PARA DEBUGGEAR ALERTAS:

1. ğŸ“‚ Abre el navegador en: http://127.0.0.1:5000
2. ğŸ”‘ Haz login con: admin / admin123  
3. ğŸ“Š Ve al Dashboard (si no estÃ¡s ya)
4. ğŸ› ï¸� Abre las herramientas de desarrollo (F12)
5. ğŸ“„ Ve a la pestaÃ±a "Console"
6. ğŸ”� Busca estos mensajes:

   âœ… MENSAJES ESPERADOS:
   - "ğŸ”� Cargando alertas de mantenimiento..."
   - "ğŸ“¡ Respuesta recibida: 200 OK"
   - "ğŸ“Š Datos de alertas: {success: true, ...}"
   - "âœ… Cargando 2 alertas"
   - "ğŸ�¨ Renderizando alertas: 2"
   - "âœ… Alertas renderizadas exitosamente"

   â�Œ MENSAJES DE ERROR:
   - "â�Œ Error cargando alertas de mantenimiento: ..."
   - "âš ï¸� Contenedor maintenanceAlerts no encontrado"
   - Cualquier error 401, 403, 500, etc.

7. ğŸ”„ Si no ves los mensajes, recarga la pÃ¡gina (F5)
8. ğŸ“‹ Reporta quÃ© mensajes ves exactamente

NOTAS:
- Las alertas deberÃ­an cargarse automÃ¡ticamente
- Si ves "Cargando alertas..." por mÃ¡s de 5 segundos, hay un problema
- El reintento automÃ¡tico deberÃ­a funcionar si hay errores
"""
)

# TambiÃ©n vamos a verificar que el server estÃ© ejecutÃ¡ndose
import requests

try:
    response = requests.get("http://127.0.0.1:5000", timeout=2)
    if response.status_code == 200:
        print("âœ… Servidor Flask estÃ¡ ejecutÃ¡ndose correctamente en puerto 5000")
    else:
        print(f"âš ï¸� Servidor responde pero con cÃ³digo: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("â�Œ ERROR: Servidor Flask no estÃ¡ ejecutÃ¡ndose!")
    print("   Ejecuta: python run.py")
except Exception as e:
    print(f"âš ï¸� Error verificando servidor: {e}")

print("\n" + "=" * 50)
print("Ahora abre el navegador y sigue las instrucciones de arriba â˜�ï¸�")
