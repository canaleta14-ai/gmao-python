from app.models.proveedor import Proveedor
from app.extensions import db
from flask import jsonify
import csv
from io import StringIO


def listar_proveedores(filtros=None):
    """Retorna proveedores activos con soporte para filtros de búsqueda"""
    query = Proveedor.query.filter_by(activo=True)

    # Aplicar filtros de búsqueda si se proporcionan
    if filtros:
        if "nombre" in filtros and filtros["nombre"]:
            query = query.filter(Proveedor.nombre.ilike(f"%{filtros['nombre']}%"))

        if "nif" in filtros and filtros["nif"]:
            query = query.filter(Proveedor.nif.ilike(f"%{filtros['nif']}%"))

        if "contacto" in filtros and filtros["contacto"]:
            query = query.filter(Proveedor.contacto.ilike(f"%{filtros['contacto']}%"))

        if "q" in filtros and filtros["q"]:
            # Búsqueda general en múltiples campos
            search_term = f"%{filtros['q']}%"
            query = query.filter(
                db.or_(
                    Proveedor.nombre.ilike(search_term),
                    Proveedor.nif.ilike(search_term),
                    Proveedor.contacto.ilike(search_term),
                    Proveedor.email.ilike(search_term),
                )
            )

    # Limitar resultados si se especifica
    if filtros and "limit" in filtros:
        try:
            limit = int(filtros["limit"])
            query = query.limit(limit)
        except (ValueError, TypeError):
            pass

    proveedores = query.all()
    return [
        {
            "id": p.id,
            "nombre": p.nombre,
            "nif": p.nif,
            "cuenta_contable": p.cuenta_contable,
            "direccion": p.direccion,
            "telefono": p.telefono,
            "email": p.email,
            "contacto": p.contacto,
            "activo": p.activo,
        }
        for p in proveedores
    ]


def crear_proveedor(data):
    """Crea un nuevo proveedor"""
    # Validaciones básicas
    if not data.get("nombre"):
        raise ValueError("El nombre es requerido")

    if not data.get("nif"):
        raise ValueError("El NIF es requerido")

    if not data.get("cuenta_contable"):
        raise ValueError("La cuenta contable es requerida")

    # Verificar que el NIF no esté duplicado
    proveedor_existente = Proveedor.query.filter_by(nif=data["nif"]).first()
    if proveedor_existente:
        raise ValueError("Ya existe un proveedor con este NIF")

    # Crear nuevo proveedor
    nuevo_proveedor = Proveedor(
        nombre=data["nombre"].strip(),
        nif=data["nif"].strip().upper(),
        cuenta_contable=data["cuenta_contable"].strip(),
        direccion=data.get("direccion", "").strip(),
        telefono=data.get("telefono", "").strip(),
        email=data.get("email", "").strip(),
        contacto=data.get("contacto", "").strip(),
        activo=True,
    )

    db.session.add(nuevo_proveedor)
    db.session.commit()

    return nuevo_proveedor


def actualizar_proveedor(id, data):
    """Actualiza un proveedor existente"""
    proveedor = Proveedor.query.get_or_404(id)

    # Validaciones básicas
    if not data.get("nombre"):
        raise ValueError("El nombre es requerido")

    if not data.get("nif"):
        raise ValueError("El NIF es requerido")

    if not data.get("cuenta_contable"):
        raise ValueError("La cuenta contable es requerida")

    # Verificar que el NIF no esté duplicado (excepto para el mismo proveedor)
    proveedor_existente = Proveedor.query.filter(
        Proveedor.nif == data["nif"].strip().upper(), Proveedor.id != id
    ).first()
    if proveedor_existente:
        raise ValueError("Ya existe otro proveedor con este NIF")

    # Actualizar campos
    proveedor.nombre = data["nombre"].strip()
    proveedor.nif = data["nif"].strip().upper()
    proveedor.cuenta_contable = data["cuenta_contable"].strip()
    proveedor.direccion = data.get("direccion", "").strip()
    proveedor.telefono = data.get("telefono", "").strip()
    proveedor.email = data.get("email", "").strip()
    proveedor.contacto = data.get("contacto", "").strip()

    db.session.commit()

    return proveedor


def eliminar_proveedor(id):
    """Marca un proveedor como inactivo (soft delete)"""
    proveedor = Proveedor.query.get_or_404(id)
    proveedor.activo = False
    db.session.commit()
    return True


def obtener_proveedor(id):
    """Obtiene un proveedor específico"""
    proveedor = Proveedor.query.get_or_404(id)
    return {
        "id": proveedor.id,
        "nombre": proveedor.nombre,
        "nif": proveedor.nif,
        "cuenta_contable": proveedor.cuenta_contable,
        "direccion": proveedor.direccion,
        "telefono": proveedor.telefono,
        "email": proveedor.email,
        "contacto": proveedor.contacto,
        "activo": proveedor.activo,
    }


def exportar_proveedores_csv():
    """Genera un archivo CSV con todos los proveedores activos"""
    proveedores = Proveedor.query.filter_by(activo=True).all()

    output = StringIO()
    writer = csv.writer(output)

    # Escribir encabezados
    writer.writerow(
        [
            "ID",
            "Nombre",
            "NIF",
            "Cuenta Contable",
            "Dirección",
            "Teléfono",
            "Email",
            "Contacto",
        ]
    )

    # Escribir datos de proveedores
    for proveedor in proveedores:
        writer.writerow(
            [
                proveedor.id,
                proveedor.nombre,
                proveedor.nif,
                proveedor.cuenta_contable,
                proveedor.direccion or "",
                proveedor.telefono or "",
                proveedor.email or "",
                proveedor.contacto or "",
            ]
        )

    csv_data = output.getvalue()
    output.close()

    return csv_data


def validar_nif(nif):
    """Valida que un NIF no esté duplicado"""
    proveedor_existente = Proveedor.query.filter_by(nif=nif.strip().upper()).first()
    if proveedor_existente:
        return {"valido": False, "mensaje": "El NIF ya existe"}
    return {"valido": True, "mensaje": "NIF disponible"}
