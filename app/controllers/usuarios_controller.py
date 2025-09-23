from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user


def autenticar_usuario(username, password):
    user = Usuario.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return user
    return None


def crear_usuario(data):
    """Crear un nuevo usuario con validaciones"""
    # Validar datos antes de crear
    errores = validar_datos_usuario(data)
    if errores:
        raise ValueError("; ".join(errores))

    user = Usuario(
        username=data["username"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        nombre=data.get("nombre", ""),
        rol=data.get("rol", "Técnico"),
        activo=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


def listar_usuarios(filtros=None, page=1, per_page=10):
    query = Usuario.query
    if filtros:
        if "username" in filtros:
            query = query.filter(Usuario.username.ilike(f"%{filtros['username']}%"))
        if "email" in filtros:
            query = query.filter(Usuario.email.ilike(f"%{filtros['email']}%"))
        if "rol" in filtros:
            query = query.filter(Usuario.rol == filtros["rol"])
        if "activo" in filtros:
            query = query.filter(Usuario.activo == filtros["activo"])
        if "nombre" in filtros:
            query = query.filter(Usuario.nombre.ilike(f"%{filtros['nombre']}%"))
        if "q" in filtros and filtros["q"]:
            # Búsqueda general en múltiples campos
            search_term = f"%{filtros['q']}%"
            query = query.filter(
                db.or_(
                    Usuario.nombre.ilike(search_term),
                    Usuario.username.ilike(search_term),
                    Usuario.email.ilike(search_term),
                    Usuario.rol.ilike(search_term),
                )
            )

    # Limitar resultados si se especifica
    if filtros and "limit" in filtros:
        try:
            limit = int(filtros["limit"])
            query = query.limit(limit)
            # Si hay límite, no usar paginación
            return query.all(), query.count()
        except (ValueError, TypeError):
            pass

    paginacion = query.order_by(Usuario.id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return paginacion.items, paginacion.total


def editar_usuario(id, data):
    """Editar un usuario existente con validaciones"""
    user = Usuario.query.get_or_404(id)

    # Validar datos antes de editar
    errores = validar_datos_usuario(data, es_edicion=True, usuario_id=id)
    if errores:
        raise ValueError("; ".join(errores))

    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    if data.get("password"):
        user.password = generate_password_hash(data["password"])
    user.nombre = data.get("nombre", user.nombre)
    user.rol = data.get("rol", user.rol)
    db.session.commit()
    return user


def cambiar_rol_usuario(id, rol):
    user = Usuario.query.get_or_404(id)
    user.rol = rol
    db.session.commit()
    return user


def cambiar_estado_usuario(id, activo):
    user = Usuario.query.get_or_404(id)
    user.activo = activo
    db.session.commit()
    return user


def obtener_usuario_por_id(id):
    """Obtener un usuario específico por su ID"""
    user = Usuario.query.get_or_404(id)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nombre": user.nombre,
        "rol": user.rol,
        "activo": user.activo,
        "fecha_creacion": (
            user.fecha_creacion.strftime("%Y-%m-%d") if user.fecha_creacion else None
        ),
    }


def eliminar_usuario(id):
    """Eliminar un usuario de la base de datos"""
    user = Usuario.query.get_or_404(id)
    # Verificar que no sea el único administrador
    if user.rol == "Administrador":
        admin_count = Usuario.query.filter_by(rol="Administrador", activo=True).count()
        if admin_count <= 1:
            raise ValueError(
                "No se puede eliminar el último administrador activo del sistema"
            )

    db.session.delete(user)
    db.session.commit()
    return True


def validar_datos_usuario(data, es_edicion=False, usuario_id=None):
    """Validar datos de usuario antes de crear/editar"""
    errores = []

    # Validar username
    if "username" in data:
        if not data["username"] or len(data["username"]) < 3:
            errores.append("El nombre de usuario debe tener al menos 3 caracteres")
        else:
            # Verificar que el username no esté duplicado
            query = Usuario.query.filter_by(username=data["username"])
            if es_edicion and usuario_id:
                query = query.filter(Usuario.id != usuario_id)
            if query.first():
                errores.append("El nombre de usuario ya está en uso")

    # Validar email
    if "email" in data:
        if not data["email"] or "@" not in data["email"]:
            errores.append("El email no es válido")
        else:
            # Verificar que el email no esté duplicado
            query = Usuario.query.filter_by(email=data["email"])
            if es_edicion and usuario_id:
                query = query.filter(Usuario.id != usuario_id)
            if query.first():
                errores.append("El email ya está en uso")

    # Validar contraseña (solo para nuevos usuarios o si se proporciona)
    if not es_edicion and ("password" not in data or not data["password"]):
        errores.append("La contraseña es obligatoria")
    elif "password" in data and data["password"]:
        if len(data["password"]) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres")

    # Validar rol
    if "rol" in data:
        roles_validos = ["Administrador", "Supervisor", "Técnico"]
        if data["rol"] not in roles_validos:
            errores.append(f"El rol debe ser uno de: {', '.join(roles_validos)}")

    return errores


def obtener_estadisticas_usuarios():
    """Obtener estadísticas generales de usuarios"""
    total = Usuario.query.count()
    activos = Usuario.query.filter_by(activo=True).count()
    inactivos = Usuario.query.filter_by(activo=False).count()

    # Estadísticas por rol
    roles_stats = {}
    for rol in ["Administrador", "Supervisor", "Técnico"]:
        roles_stats[rol] = Usuario.query.filter_by(rol=rol, activo=True).count()

    return {
        "total": total,
        "activos": activos,
        "inactivos": inactivos,
        "roles": roles_stats,
    }
