import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

from app.factory import create_app

app = create_app()

if __name__ == "__main__":
    # Configuración de debug desde variables de entorno
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))

    app.run(debug=debug, host=host, port=port)
