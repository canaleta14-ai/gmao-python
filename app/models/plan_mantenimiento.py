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

    # Campos esperados por rutas/tests
    tipo_mantenimiento = db.Column(db.String(50))
    tareas = db.Column(db.Text)
    duracion_estimada = db.Column(db.Float)

    # Campos para configuración de frecuencia específica
    tipo_frecuencia = db.Column(db.String(20))  # 'diaria', 'semanal', 'mensual', etc.

    # Configuración semanal
    intervalo_semanas = db.Column(db.Integer)
    dias_semana = db.Column(
        db.String(200)
    )  # JSON string de días seleccionados (aumentado de 50 a 200)

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

    # Control de generación automática
    generacion_automatica = db.Column(
        db.Boolean, default=True
    )  # Si genera órdenes automáticamente

    activo_id = db.Column(db.Integer, db.ForeignKey("activo.id"))
    responsable_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))

    def __init__(self, *args, **kwargs):
        # Generar código por defecto si no se proporciona
        codigo_plan = kwargs.pop("codigo_plan", None)
        # Permitir que tests/rutas pasen 'activo' como boolean para mapear a estado
        activo_flag = kwargs.pop("activo", None)

        super().__init__(*args, **kwargs)

        if codigo_plan:
            self.codigo_plan = codigo_plan
        else:
            self.codigo_plan = self._generar_codigo_plan()

        if activo_flag is not None:
            try:
                self.estado = "Activo" if bool(activo_flag) else "Inactivo"
            except Exception:
                # En caso de tipos no booleanos, dejar estado por defecto
                pass

    @staticmethod
    def _generar_codigo_plan():
        # Genera un código único y legible para el plan
        from datetime import datetime
        import random

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        rand = random.randint(1000, 9999)
        return f"PLAN-{timestamp}-{rand}"
