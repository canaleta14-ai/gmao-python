from app import create_app
from app.controllers.planes_controller import generar_ordenes_automaticas

app = create_app()

with app.app_context():
    resultado = generar_ordenes_automaticas()
    print("Resultado:")
    print(f'Success: {resultado["success"]}')
    print(f'Message: {resultado["message"]}')
    print(f'Órdenes generadas: {resultado.get("ordenes_generadas", 0)}')
    print(f'Planes procesados: {resultado.get("planes_procesados", 0)}')

    if "detalles" in resultado:
        print("\nDetalles:")
        for detalle in resultado["detalles"]:
            print(f"  - {detalle}")
