from app.models.activo import Activo
from app.extensions import db
from flask import jsonify
import csv
from io import StringIO


def listar_activos(filtros=None):
    query = Activo.query

    # Aplicar filtros de búsqueda si se proporcionan
    if filtros:
        if "nombre" in filtros and filtros["nombre"]:
            query = query.filter(Activo.nombre.ilike(f"%{filtros['nombre']}%"))

        if "codigo" in filtros and filtros["codigo"]:
            query = query.filter(Activo.codigo.ilike(f"%{filtros['codigo']}%"))

        if "ubicacion" in filtros and filtros["ubicacion"]:
            query = query.filter(Activo.ubicacion.ilike(f"%{filtros['ubicacion']}%"))

        if "fabricante" in filtros and filtros["fabricante"]:
            query = query.filter(Activo.fabricante.ilike(f"%{filtros['fabricante']}%"))

        if "departamento" in filtros and filtros["departamento"]:
            query = query.filter(Activo.departamento == filtros["departamento"])

        if "tipo" in filtros and filtros["tipo"]:
            query = query.filter(Activo.tipo.ilike(f"%{filtros['tipo']}%"))

        if "q" in filtros and filtros["q"]:
            # Búsqueda general en múltiples campos
            search_term = f"%{filtros['q']}%"
            query = query.filter(
                db.or_(
                    Activo.nombre.ilike(search_term),
                    Activo.codigo.ilike(search_term),
                    Activo.ubicacion.ilike(search_term),
                    Activo.fabricante.ilike(search_term),
                )
            )

    # Limitar resultados si se especifica
    if filtros and "limit" in filtros:
        try:
            limit = int(filtros["limit"])
            query = query.limit(limit)
        except (ValueError, TypeError):
            pass

    activos = query.all()
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


def listar_activos_paginado(
    page=1, per_page=10, q=None, departamento=None, estado=None
):
    """Listar activos con paginación y filtros"""
    query = Activo.query

    # Filtro por departamento
    if departamento:
        query = query.filter_by(departamento=departamento)

    # Filtro por estado
    if estado:
        query = query.filter_by(estado=estado)

    # Filtro de búsqueda general
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            db.or_(
                Activo.nombre.ilike(search_term),
                Activo.codigo.ilike(search_term),
                Activo.ubicacion.ilike(search_term),
                Activo.fabricante.ilike(search_term),
                Activo.tipo.ilike(search_term),
                Activo.proveedor.ilike(search_term),
                Activo.modelo.ilike(search_term),
                Activo.numero_serie.ilike(search_term),
            )
        )

    # Ordenamiento por código
    query = query.order_by(Activo.codigo.asc())

    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    departamentos = Activo.get_departamentos()
    activos_data = [
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
        for a in pagination.items
    ]

    return {
        "items": activos_data,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


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
