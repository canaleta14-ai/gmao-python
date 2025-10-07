import os
import sys

# Ensure project root on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

def main():
    # Simulate pytest environment for in-memory DB and CSRF disabled
    os.environ["PYTEST_CURRENT_TEST"] = "debug_order_post"
    app = create_app()
    with app.test_client() as client:
        # Prepare admin user in DB
        with app.app_context():
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

        # Ensure login
        login = client.post(
            "/login", json={"username": "admin", "password": "admin123"}
        )
        print("login status:", login.status_code)
        payload = {
            "tipo": "Correctivo",
            "prioridad": "Media",
            "descripcion": "Orden de prueba cobertura",
        }
        resp = client.post("/ordenes/", json=payload)
        print("create status:", resp.status_code)
        try:
            print("create body:", resp.get_json())
        except Exception as e:
            print("create body error:", e, resp.data[:200])

if __name__ == "__main__":
    main()