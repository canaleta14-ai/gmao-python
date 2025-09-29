from app.factory import create_app
from app.models.usuario import Usuario

app = create_app()
with app.app_context():
    users = Usuario.query.all()
    print(f"Total de usuarios en la base de datos: {len(users)}")
    if users:
        for user in users:
            print(
                f"ID: {user.id}, Usuario: {user.username}, Email: {user.email}, Rol: {user.rol}, Activo: {user.activo}"
            )
    else:
        print("No hay usuarios en la base de datos.")
        print("Creando usuario admin por defecto...")

        # Crear usuario admin
        from werkzeug.security import generate_password_hash

        admin = Usuario(
            username="admin",
            email="admin@gmao.com",
            password=generate_password_hash("admin123"),
            nombre="Administrador",
            rol="Administrador",
            activo=True,
        )
        from app.extensions import db

        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado: admin / admin123")
