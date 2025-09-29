from app import create_app
from app.models.orden_trabajo import OrdenTrabajo
from datetime import datetime

app = create_app()
with app.app_context():
    # Buscar la orden específica
    orden_semanal = OrdenTrabajo.query.filter(
        OrdenTrabajo.numero_orden == "OT-SEMANAL-L"
    ).first()

    if orden_semanal:
        print(f"Orden encontrada: {orden_semanal.numero_orden}")
        print(f"Descripción: {orden_semanal.descripcion}")
        print(f"Fecha programada: {orden_semanal.fecha_programada}")
        print(f"Día: {orden_semanal.fecha_programada.strftime('%A')}")
        print(f"Estado: {orden_semanal.estado}")

        # El problema: está programada para martes 30/09/2025 pero debería ser lunes 29/09/2025
        fecha_correcta = datetime(2025, 9, 29)  # Lunes
        print(f"\nFecha correcta (lunes): {fecha_correcta.strftime('%Y-%m-%d %A')}")

        # Corregir la fecha
        print(
            f"\n¿Corregir la fecha? (de {orden_semanal.fecha_programada.strftime('%A')} a {fecha_correcta.strftime('%A')})"
        )
        respuesta = input("S/N: ")

        if respuesta.upper() == "S":
            from app.extensions import db

            orden_semanal.fecha_programada = fecha_correcta
            db.session.commit()
            print("✅ Fecha corregida exitosamente")
        else:
            print("❌ No se realizaron cambios")
    else:
        print("No se encontró la orden OT-SEMANAL-L")

        # Buscar por descripción
        orden_alt = OrdenTrabajo.query.filter(
            OrdenTrabajo.descripcion.contains("semanal")
        ).first()

        if orden_alt:
            print(f"\nEncontrada orden alternativa: {orden_alt.numero_orden}")
            print(f"Fecha: {orden_alt.fecha_programada}")
            print(f"Día: {orden_alt.fecha_programada.strftime('%A')}")
        else:
            print("No se encontraron órdenes semanales")
