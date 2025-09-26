from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import event
import re


class Categoria(db.Model):
    """Modelo para categorías dinámicas de inventario"""

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    prefijo = db.Column(
        db.String(10), unique=True, nullable=False
    )  # Para códigos automáticos
    descripcion = db.Column(db.String(200))
    color = db.Column(db.String(7), default="#6c757d")  # Color hex para UI
    activa = db.Column(db.Boolean, default=True)

    # Numeración automática
    ultimo_numero = db.Column(db.Integer, default=0)  # Último número usado para códigos

    # Campos contables
    cuenta_contable_defecto = db.Column(db.String(20), default="622000000")

    # Metadatos
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_actualizacion = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @staticmethod
    def generar_prefijo_desde_nombre(nombre):
        """Genera un prefijo de 3 letras desde el nombre de la categoría"""
        # Limpiar el nombre y tomar las primeras letras
        nombre_limpio = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]", "", nombre.upper())
        palabras = nombre_limpio.split()

        if len(palabras) >= 2:
            # Si hay múltiples palabras, tomar primera letra de cada una
            prefijo = "".join([palabra[0] for palabra in palabras[:3]])
        else:
            # Si hay una sola palabra, tomar las primeras 3 letras
            prefijo = nombre_limpio[:3]

        # Asegurar que sea de 3 caracteres
        while len(prefijo) < 3:
            prefijo += "X"

        return prefijo[:3]

    # Relaciones
    articulos = db.relationship(
        "Inventario",
        back_populates="categoria_obj",
        lazy=True,
        foreign_keys="Inventario.categoria_id",
    )

    def __repr__(self):
        return f"<Categoria {self.nombre} ({self.prefijo})>"

    def generar_proximo_codigo(self):
        """Genera el próximo código para esta categoría"""
        año = datetime.now().year
        self.ultimo_numero += 1
        codigo = f"{self.prefijo}-{año}-{self.ultimo_numero:03d}"
        db.session.commit()
        return codigo

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "prefijo": self.prefijo,
            "descripcion": self.descripcion,
            "color": self.color,
            "activa": self.activa,
            "ultimo_numero": self.ultimo_numero,
            "fecha_creacion": (
                self.fecha_creacion.isoformat() if self.fecha_creacion else None
            ),
        }


# Evento para generar prefijo automáticamente antes de insertar
@event.listens_for(Categoria, "before_insert")
def generar_prefijo_automatico(mapper, connection, target):
    """Genera automáticamente el prefijo si no se proporciona"""
    if not target.prefijo:
        prefijo_base = Categoria.generar_prefijo_desde_nombre(target.nombre)

        # Verificar si el prefijo ya existe y ajustarlo si es necesario
        contador = 1
        prefijo_final = prefijo_base

        # Usar una consulta SQL directa ya que estamos en before_insert
        result = connection.execute(
            db.text("SELECT COUNT(*) FROM categoria WHERE prefijo = :prefijo"),
            {"prefijo": prefijo_final},
        )
        count = result.scalar()

        while count > 0:
            prefijo_final = f"{prefijo_base[:-1]}{contador}"
            result = connection.execute(
                db.text("SELECT COUNT(*) FROM categoria WHERE prefijo = :prefijo"),
                {"prefijo": prefijo_final},
            )
            count = result.scalar()
            contador += 1

        target.prefijo = prefijo_final
