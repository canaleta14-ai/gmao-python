import requests

try:
    data = {
        "nombre_solicitante": "Juan Pérez",
        "email_solicitante": "juan@example.com",
        "telefono_solicitante": "123456789",
        "empresa_solicitante": "Empresa Test",
        "tipo_servicio": "mantenimiento",
        "prioridad": "normal",
        "titulo": "Prueba de solicitud",
        "descripcion": "Esta es una solicitud de prueba",
        "ubicacion": "Oficina principal",
        "activo_afectado": "Computadora 001",
    }
    response = requests.post(
        "http://localhost:5000/solicitudes/", data=data, timeout=10
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 302:
        print("SUCCESS: Request processed and redirected!")
        print("Redirect location:", response.headers.get("Location", "N/A"))
    elif response.status_code == 200:
        print("Request processed but stayed on same page")
        if "error" in response.text.lower() or "flash" in response.text.lower():
            print("Possible validation errors found")
    else:
        print(f"ERROR: Status {response.status_code}")
        print(response.text[:500])
except Exception as e:
    print(f"ERROR: {e}")
