from app import create_app
from app.models.orden_trabajo import OrdenTrabajo
from app.extensions import db
from datetime import datetime

app = create_app()
with app.app_context():
    # Buscar la orden específica
    orden_semanal = OrdenTrabajo.query.filter(
        OrdenTrabajo.numero_orden == "OT-SEMANAL-L"
    ).first()

    if orden_semanal:
        print(f"✅ Orden encontrada: {orden_semanal.numero_orden}")
        print(f"📝 Descripción: {orden_semanal.descripcion}")
        print(f"📅 Fecha actual: {orden_semanal.fecha_programada}")
        print(f"📆 Día actual: {orden_semanal.fecha_programada.strftime('%A')}")

        # La fecha correcta debe ser lunes 29/09/2025
        fecha_correcta = datetime(2025, 9, 29)
        print(f"\n🎯 Fecha correcta (lunes): {fecha_correcta.strftime('%Y-%m-%d %A')}")

        if orden_semanal.fecha_programada.date() != fecha_correcta.date():
            print("🔧 Corrigiendo fecha...")
            orden_semanal.fecha_programada = fecha_correcta
            db.session.commit()
            print("✅ Fecha corregida exitosamente")
            print(
                f"📅 Nueva fecha: {orden_semanal.fecha_programada.strftime('%Y-%m-%d %A')}"
            )
        else:
            print("✅ La fecha ya es correcta")
    else:
        print("❌ No se encontró la orden OT-SEMANAL-L")

        # Buscar cualquier orden semanal
        orden_semanal = OrdenTrabajo.query.filter(
            OrdenTrabajo.descripcion.contains("semanal")
        ).first()

        if orden_semanal:
            print(f"\n✅ Encontrada orden semanal: {orden_semanal.numero_orden}")
            print(f"📅 Fecha actual: {orden_semanal.fecha_programada}")
            print(f"📆 Día: {orden_semanal.fecha_programada.strftime('%A')}")

            # Si es para lunes pero está mal programada
            if "lunes" in orden_semanal.descripcion.lower():
                fecha_correcta = datetime(2025, 9, 29)  # Próximo lunes
                if orden_semanal.fecha_programada.date() != fecha_correcta.date():
                    print("🔧 Corrigiendo fecha para lunes...")
                    orden_semanal.fecha_programada = fecha_correcta
                    db.session.commit()
                    print("✅ Fecha corregida")
        else:
            print("❌ No se encontraron órdenes semanales")
