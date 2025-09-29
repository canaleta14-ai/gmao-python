from app.models.usuario import Usuario
from app.extensions import db
from app.factory import create_app

app = create_app()
with app.app_context():
    user = Usuario.query.filter_by(username="admin").first()
    print(f"Usuario admin existe: {user is not None}")
    if user:
        print(f"ID: {user.id}, Username: {user.username}, Rol: {user.rol}")
        print(f"Password hash: {user.password}")
