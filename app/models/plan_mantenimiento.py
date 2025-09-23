from app.extensions import db
from datetime import datetime


class PlanMantenimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_plan = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    frecuencia = db.Column(db.String(50))
    frecuencia_dias = db.Column(db.Integer)
    ultima_ejecucion = db.Column(db.DateTime)
    proxima_ejecucion = db.Column(db.DateTime)
    estado = db.Column(db.String(50), default="Activo")
    descripcion = db.Column(db.Text)
    instrucciones = db.Column(db.Text)
    tiempo_estimado = db.Column(db.Float)

    # Campos para configuración de frecuencia específica
    tipo_frecuencia = db.Column(db.String(20))  # 'diaria', 'semanal', 'mensual', etc.

    # Configuración semanal
    intervalo_semanas = db.Column(db.Integer)
    dias_semana = db.Column(db.String(50))  # JSON string de días seleccionados

    # Configuración mensual
    tipo_mensual = db.Column(db.String(20))  # 'dia_mes' o 'dia_semana_mes'
    dia_mes = db.Column(db.Integer)  # Para tipo 'dia_mes'
    semana_mes = db.Column(db.Integer)  # Para tipo 'dia_semana_mes' (1-4)
    dia_semana_mes = db.Column(
        db.String(20)
    )  # Para tipo 'dia_semana_mes' (lunes, martes, etc.)
    intervalo_meses = db.Column(db.Integer)  # Cada X meses

    # Configuración personalizada
    frecuencia_personalizada = db.Column(db.Text)  # JSON para configuraciones complejas

    activo_id = db.Column(db.Integer, db.ForeignKey("activo.id"))
