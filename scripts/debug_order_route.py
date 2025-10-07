import os
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

os.environ["DB_TYPE"] = "sqlite"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

from app.factory import create_app
from app.extensions import db
from app.models.usuario import Usuario


def ensure_admin(app):
    with app.app_context():
        db.create_all()
        admin = Usuario.query.filter_by(username="admin").first()
        if not admin:
            admin = Usuario(
                username="admin",
                email="admin@example.com",
                nombre="Administrador",
                rol="Administrador",
                activo=True,
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()


def main():
    app = create_app()
    # Match testing config similar to tests/conftest
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_ENGINE_OPTIONS": {"connect_args": {"check_same_thread": False}},
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "x" * 64,
            "FLASK_ENV": "development",
        }
    )

    ensure_admin(app)

    with app.test_client() as client:
        # Login
        rlogin = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/json"},
        )
        print("Login:", rlogin.status_code, rlogin.get_json())

        # Minimal order payload
        payload = {
            "tipo": "Correctivo",
            "prioridad": "Media",
            "descripcion": "Orden de prueba cobertura",
        }
        rcreate = client.post("/ordenes/", json=payload)
        print("Create:", rcreate.status_code, rcreate.get_json())

        # If created, try to update estado and then delete
        if rcreate.status_code in (200, 201):
            oid = (rcreate.get_json() or {}).get("id")
            rstate = client.put(f"/ordenes/api/{oid}/estado", json={"estado": "En Proceso"})
            print("Estado:", rstate.status_code, rstate.get_json())
            rdel = client.delete(f"/ordenes/api/{oid}")
            print("Delete:", rdel.status_code, rdel.get_json())


if __name__ == "__main__":
    main()