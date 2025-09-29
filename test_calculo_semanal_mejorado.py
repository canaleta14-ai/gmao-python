from datetime import datetime, timedelta


def calcular_proxima_ejecucion_semanal_mejorada(
    dias_semana, fecha_base=None, intervalo_semanas=1
):
    """
    Versión mejorada y corregida del cálculo de próxima ejecución semanal

    Args:
        dias_semana: Lista de días en español ['lunes', 'martes', etc.]
        fecha_base: Fecha desde la cual calcular (por defecto: ahora)
        intervalo_semanas: Cada cuántas semanas repetir (por defecto: 1)

    Returns:
        datetime: Próxima fecha de ejecución
    """
    if fecha_base is None:
        fecha_base = datetime.now()

    # Mapeo de días en español a números de semana (lunes=0, domingo=6)
    dias_map = {
        "lunes": 0,
        "martes": 1,
        "miercoles": 2,
        "jueves": 3,
        "viernes": 4,
        "sabado": 5,
        "domingo": 6,
    }

    # Convertir días a números
    dias_numericos = []
    for dia in dias_semana:
        if isinstance(dia, str) and dia.lower() in dias_map:
            dias_numericos.append(dias_map[dia.lower()])

    if not dias_numericos:
        # Si no hay días válidos, default a próxima semana
        return fecha_base + timedelta(weeks=intervalo_semanas)

    dias_numericos.sort()  # Ordenar para consistencia
    dia_actual = fecha_base.weekday()  # 0=lunes, 6=domingo

    print(f"🐛 DEBUG: fecha_base={fecha_base.strftime('%Y-%m-%d %A')}")
    print(f"🐛 DEBUG: dia_actual={dia_actual} ({fecha_base.strftime('%A')})")
    print(f"🐛 DEBUG: dias_numericos={dias_numericos}")

    # Buscar el próximo día disponible
    proxima_fecha = None

    # 1. Buscar en la semana actual (solo días futuros)
    for dia_objetivo in dias_numericos:
        if dia_objetivo > dia_actual:
            dias_hasta = dia_objetivo - dia_actual
            proxima_fecha = fecha_base + timedelta(days=dias_hasta)
            print(
                f"🐛 DEBUG: Encontrado en semana actual - día {dia_objetivo}, en {dias_hasta} días"
            )
            break

    # 2. Si no se encontró en semana actual, ir a próxima semana
    if proxima_fecha is None:
        primer_dia = min(dias_numericos)
        # Días hasta el final de esta semana + días desde lunes hasta día objetivo
        dias_hasta_lunes_siguiente = 7 - dia_actual
        dias_desde_lunes = primer_dia
        dias_total = dias_hasta_lunes_siguiente + dias_desde_lunes
        proxima_fecha = fecha_base + timedelta(days=dias_total)
        print(f"🐛 DEBUG: No encontrado en semana actual, yendo a próxima semana")
        print(
            f"🐛 DEBUG: primer_dia={primer_dia}, dias_hasta_lunes={dias_hasta_lunes_siguiente}"
        )
        print(f"🐛 DEBUG: días_total={dias_total}")

    # 3. Aplicar intervalo de semanas si es > 1
    if intervalo_semanas > 1:
        semanas_adicionales = (intervalo_semanas - 1) * 7
        proxima_fecha = proxima_fecha + timedelta(days=semanas_adicionales)
        print(f"🐛 DEBUG: Aplicado intervalo {intervalo_semanas} semanas")

    # 4. Limpiar hora (medianoche)
    proxima_fecha = proxima_fecha.replace(hour=0, minute=0, second=0, microsecond=0)

    print(f"🐛 DEBUG: RESULTADO FINAL: {proxima_fecha.strftime('%Y-%m-%d %A')}")
    return proxima_fecha


def test_calculo_semanal():
    """Probar diferentes escenarios del cálculo semanal"""
    print("🧪 PRUEBAS DE CÁLCULO SEMANAL")
    print("=" * 50)

    # Escenario 1: Hoy es domingo, plan para lunes
    fecha_domingo = datetime(2025, 9, 28)  # Domingo
    resultado1 = calcular_proxima_ejecucion_semanal_mejorada(["lunes"], fecha_domingo)
    print(f"Escenario 1 - Domingo → Lunes: {resultado1.strftime('%Y-%m-%d %A')}")
    print()

    # Escenario 2: Hoy es lunes, plan para martes
    fecha_lunes = datetime(2025, 9, 29)  # Lunes
    resultado2 = calcular_proxima_ejecucion_semanal_mejorada(["martes"], fecha_lunes)
    print(f"Escenario 2 - Lunes → Martes: {resultado2.strftime('%Y-%m-%d %A')}")
    print()

    # Escenario 3: Hoy es viernes, plan para lunes (próxima semana)
    fecha_viernes = datetime(2025, 9, 26)  # Viernes
    resultado3 = calcular_proxima_ejecucion_semanal_mejorada(["lunes"], fecha_viernes)
    print(
        f"Escenario 3 - Viernes → Lunes siguiente: {resultado3.strftime('%Y-%m-%d %A')}"
    )
    print()

    # Escenario 4: Plan para múltiples días
    resultado4 = calcular_proxima_ejecucion_semanal_mejorada(
        ["lunes", "miercoles", "viernes"], fecha_domingo
    )
    print(f"Escenario 4 - Múltiples días: {resultado4.strftime('%Y-%m-%d %A')}")
    print()


if __name__ == "__main__":
    test_calculo_semanal()
