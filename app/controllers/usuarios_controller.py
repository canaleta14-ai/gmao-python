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
    user = Usuario(
        username=data["username"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        nombre=data.get("nombre"),
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
    paginacion = query.order_by(Usuario.id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return paginacion.items, paginacion.total


def editar_usuario(id, data):
    user = Usuario.query.get_or_404(id)
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
