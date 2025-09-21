from app.models.activo import Activo
from app.extensions import db
from flask import jsonify
import csv
from io import StringIO


def listar_activos():
    activos = Activo.query.all()
    departamentos = Activo.get_departamentos()
    return [
        {
            "id": a.id,
            "codigo": a.codigo,
            "departamento": a.departamento,
            "departamento_nombre": departamentos.get(a.departamento, "Desconocido"),
            "nombre": a.nombre,
            "tipo": a.tipo,
            "ubicacion": a.ubicacion,
            "estado": a.estado,
            "prioridad": a.prioridad,
            "modelo": a.modelo,
            "numero_serie": a.numero_serie,
            "fabricante": a.fabricante,
            "proveedor": a.proveedor,
            "ultimo_mantenimiento": (
                a.ultimo_mantenimiento.strftime("%d/%m/%Y")
                if a.ultimo_mantenimiento
                else None
            ),
        }
        for a in activos
    ]


def crear_activo(data):
    # Validar que se proporcione el departamento
    if "departamento" not in data:
        raise ValueError("El departamento es requerido")

    departamento = data["departamento"]
    departamentos_validos = Activo.get_departamentos()

    if departamento not in departamentos_validos:
        raise ValueError("Departamento no válido")

    # Generar código automáticamente o validar el proporcionado
    if "codigo" in data and data["codigo"]:
        codigo = data["codigo"]
        # Validar formato del código
        if not Activo.validar_codigo(codigo):
            raise ValueError("Formato de código inválido. Use el formato: 123A45678")

        # Verificar que el código sea único
        if Activo.query.filter_by(codigo=codigo).first():
            raise ValueError("El código ya existe")
    else:
        # Generar código automáticamente
        codigo = Activo.generar_codigo(departamento)

    nuevo_activo = Activo(
        codigo=codigo,
        departamento=departamento,
        nombre=data["nombre"],
        tipo=data.get("tipo"),
        ubicacion=data.get("ubicacion"),
        estado=data.get("estado", "Operativo"),
        prioridad=data.get("prioridad", "Media"),
        descripcion=data.get("descripcion"),
        modelo=data.get("modelo"),
        numero_serie=data.get("numero_serie"),
        fabricante=data.get("fabricante"),
        proveedor=data.get("proveedor"),
    )
    db.session.add(nuevo_activo)
    db.session.commit()
    return nuevo_activo


def actualizar_activo(id, data):
    activo = Activo.query.get_or_404(id)

    # Si se actualiza el código, validarlo
    if "codigo" in data and data["codigo"] != activo.codigo:
        nuevo_codigo = data["codigo"]
        if not Activo.validar_codigo(nuevo_codigo):
            raise ValueError("Formato de código inválido")

        # Verificar unicidad
        if Activo.query.filter_by(codigo=nuevo_codigo).filter(Activo.id != id).first():
            raise ValueError("El código ya existe")

        activo.codigo = nuevo_codigo

    # Si se actualiza el departamento
    if "departamento" in data:
        departamentos_validos = Activo.get_departamentos()
        if data["departamento"] not in departamentos_validos:
            raise ValueError("Departamento no válido")
        activo.departamento = data["departamento"]

    activo.nombre = data.get("nombre", activo.nombre)
    activo.tipo = data.get("tipo", activo.tipo)
    activo.ubicacion = data.get("ubicacion", activo.ubicacion)
    activo.estado = data.get("estado", activo.estado)
    activo.prioridad = data.get("prioridad", activo.prioridad)
    activo.descripcion = data.get("descripcion", activo.descripcion)
    activo.modelo = data.get("modelo", activo.modelo)
    activo.numero_serie = data.get("numero_serie", activo.numero_serie)
    activo.fabricante = data.get("fabricante", activo.fabricante)
    activo.proveedor = data.get("proveedor", activo.proveedor)

    db.session.commit()
    return activo


def eliminar_activo(id):
    activo = Activo.query.get_or_404(id)
    db.session.delete(activo)
    db.session.commit()
    return True


def generar_siguiente_codigo(departamento):
    """Genera el siguiente código disponible para un departamento"""
    return Activo.generar_codigo(departamento)


def obtener_departamentos():
    """Retorna la lista de departamentos disponibles"""
    return Activo.get_departamentos()


def exportar_activos_csv():
    """Genera un archivo CSV con todos los activos"""
    activos = Activo.query.all()
    departamentos = Activo.get_departamentos()

    output = StringIO()
    writer = csv.writer(output)

    # Escribir encabezados
    writer.writerow(
        [
            "Código",
            "Departamento",
            "Nombre Departamento",
            "Nombre Activo",
            "Tipo",
            "Ubicación",
            "Estado",
            "Prioridad",
            "Modelo",
            "Número Serie",
            "Fabricante",
            "Proveedor",
            "Último Mantenimiento",
        ]
    )

    # Escribir datos
    for activo in activos:
        writer.writerow(
            [
                activo.codigo,
                activo.departamento,
                departamentos.get(activo.departamento, "Desconocido"),
                activo.nombre,
                activo.tipo or "",
                activo.ubicacion or "",
                activo.estado,
                activo.prioridad or "",
                activo.modelo or "",
                activo.numero_serie or "",
                activo.fabricante or "",
                activo.proveedor or "",
                (
                    activo.ultimo_mantenimiento.strftime("%d/%m/%Y")
                    if activo.ultimo_mantenimiento
                    else ""
                ),
            ]
        )

    csv_data = output.getvalue()
    output.close()

    return csv_data


def validar_codigo_unico(codigo):
    """Valida que el código tenga formato correcto y sea único"""
    from app.models.activo import Activo

    # Validar formato
    if not Activo.validar_codigo(codigo):
        return {
            "valido": False,
            "mensaje": "Formato de código inválido. Use: 123A45678",
        }

    # Validar unicidad
    activo_existente = Activo.query.filter_by(codigo=codigo).first()
    if activo_existente:
        return {"valido": False, "mensaje": "El código ya existe"}

    return {"valido": True, "mensaje": "Código válido"}
