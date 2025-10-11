#!/usr/bin/env python3
"""
Configuración específica para España - GMAO Disfood
"""

import os
import pytz
from datetime import datetime


def configure_spain_settings():
    """Configurar ajustes específicos para España"""

    # Zona horaria española
    os.environ["TZ"] = "Europe/Madrid"

    # Idioma y localización
    os.environ["LANG"] = "es_ES.UTF-8"
    os.environ["LC_ALL"] = "es_ES.UTF-8"

    # Configuración de fechas
    os.environ["DATE_FORMAT"] = "%d/%m/%Y"
    os.environ["DATETIME_FORMAT"] = "%d/%m/%Y %H:%M"

    # Configuración GDPR
    os.environ["GDPR_COMPLIANCE"] = "true"
    os.environ["DATA_RETENTION_YEARS"] = "7"  # Normativa española
    os.environ["PRIVACY_POLICY_URL"] = "/politica-privacidad"
    os.environ["COOKIES_POLICY_URL"] = "/politica-cookies"

    # Configuración de empresa española
    os.environ["COMPANY_COUNTRY"] = "ES"
    os.environ["COMPANY_TIMEZONE"] = "Europe/Madrid"
    os.environ["WORKING_HOURS_START"] = "08:00"
    os.environ["WORKING_HOURS_END"] = "18:00"

    # Días laborables (Lunes=0, Domingo=6)
    os.environ["WORKING_DAYS"] = "0,1,2,3,4"  # Lun-Vie

    # Festivos nacionales españoles (formato MM-DD)
    os.environ["NATIONAL_HOLIDAYS"] = (
        "01-01,01-06,05-01,08-15,10-12,11-01,12-06,12-08,12-25"
    )

    return True


def get_spain_timezone():
    """Obtener zona horaria de España"""
    return pytz.timezone("Europe/Madrid")


def format_spanish_date(date_obj):
    """Formatear fecha en formato español"""
    if not date_obj:
        return ""

    # Convertir a zona horaria española
    spain_tz = get_spain_timezone()
    if date_obj.tzinfo is None:
        date_obj = spain_tz.localize(date_obj)
    else:
        date_obj = date_obj.astimezone(spain_tz)

    return date_obj.strftime("%d/%m/%Y %H:%M")


def get_working_hours():
    """Obtener horario laboral español"""
    return {
        "start": "08:00",
        "end": "18:00",
        "lunch_start": "13:00",
        "lunch_end": "14:00",
        "working_days": [0, 1, 2, 3, 4],  # Lun-Vie
    }


def is_working_day(date_obj):
    """Verificar si es día laborable en España"""
    if not date_obj:
        return False

    # Convertir a zona horaria española
    spain_tz = get_spain_timezone()
    if date_obj.tzinfo is None:
        date_obj = spain_tz.localize(date_obj)
    else:
        date_obj = date_obj.astimezone(spain_tz)

    # Verificar día de la semana (0=Lunes, 6=Domingo)
    if date_obj.weekday() >= 5:  # Sábado o Domingo
        return False

    # Verificar festivos nacionales
    national_holidays = [
        "01-01",  # Año Nuevo
        "01-06",  # Reyes Magos
        "05-01",  # Día del Trabajador
        "08-15",  # Asunción de la Virgen
        "10-12",  # Día de la Hispanidad
        "11-01",  # Todos los Santos
        "12-06",  # Día de la Constitución
        "12-08",  # Inmaculada Concepción
        "12-25",  # Navidad
    ]

    date_str = date_obj.strftime("%m-%d")
    if date_str in national_holidays:
        return False

    return True


def get_next_working_day(date_obj):
    """Obtener el siguiente día laborable"""
    from datetime import timedelta

    current_date = date_obj
    while not is_working_day(current_date):
        current_date += timedelta(days=1)

    return current_date


def get_spanish_locale_settings():
    """Obtener configuración de localización española"""
    return {
        "decimal_separator": ",",
        "thousands_separator": ".",
        "currency_symbol": "€",
        "currency_position": "after",  # "100,50 €"
        "date_format": "dd/mm/yyyy",
        "time_format": "HH:mm",
        "first_day_of_week": 1,  # Lunes
    }


if __name__ == "__main__":
    configure_spain_settings()
    print("✅ Configuración española aplicada")
    print(f"🕐 Zona horaria: {os.environ.get('TZ')}")
    print(f"🌍 Idioma: {os.environ.get('LANG')}")
    print(f"📅 Formato fecha: {os.environ.get('DATE_FORMAT')}")
    print(
        f"🏢 Horario laboral: {os.environ.get('WORKING_HOURS_START')} - {os.environ.get('WORKING_HOURS_END')}"
    )
