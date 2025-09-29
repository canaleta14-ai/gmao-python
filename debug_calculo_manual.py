from datetime import datetime, timedelta

# Datos de prueba
fecha_base = datetime(2025, 9, 28)  # Domingo
dia_actual = fecha_base.weekday()  # 6 = domingo
primer_dia = 0  # lunes

print(f"Fecha base: {fecha_base.strftime('%Y-%m-%d %A')}")
print(f"Día actual (weekday): {dia_actual}")
print(f"Día objetivo: {primer_dia} (lunes)")

# Mi cálculo actual (MAL)
dias_hasta_lunes_siguiente = 7 - dia_actual
dias_total = dias_hasta_lunes_siguiente + primer_dia
resultado_mal = fecha_base + timedelta(days=dias_total)

print(f"\n🔴 MI CÁLCULO ACTUAL (MAL):")
print(f"días_hasta_lunes_siguiente = 7 - {dia_actual} = {dias_hasta_lunes_siguiente}")
print(f"días_total = {dias_hasta_lunes_siguiente} + {primer_dia} = {dias_total}")
print(f"Resultado: {resultado_mal.strftime('%Y-%m-%d %A')}")

# Cálculo correcto
# Domingo (6) -> Lunes (0): simplemente 1 día
dias_hasta_correcto = (primer_dia - dia_actual) % 7
if dias_hasta_correcto == 0:  # Si es el mismo día, ir a próxima semana
    dias_hasta_correcto = 7
resultado_correcto = fecha_base + timedelta(days=dias_hasta_correcto)

print(f"\n✅ CÁLCULO CORRECTO:")
print(f"días_hasta = ({primer_dia} - {dia_actual}) % 7 = {dias_hasta_correcto}")
print(f"Resultado: {resultado_correcto.strftime('%Y-%m-%d %A')}")

# Otro enfoque más simple
dias_simples = 1  # De domingo a lunes es simplemente 1 día
resultado_simple = fecha_base + timedelta(days=dias_simples)
print(f"\n✅ CÁLCULO SIMPLE:")
print(f"domingo + 1 día = {resultado_simple.strftime('%Y-%m-%d %A')}")
