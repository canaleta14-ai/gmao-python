from flask import Blueprint, jsonify, current_app
from app.utils.email_utils import enviar_email
import logging

# Crear blueprint para test de email
test_email_bp = Blueprint("test_email", __name__)


@test_email_bp.route("/api/test-email-debug", methods=["GET"])
def test_email_debug():
    """
    Endpoint para probar el envío de emails directamente
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info("=== INICIANDO TEST DE EMAIL DIRECTO ===")

        # Intentar enviar un email de prueba
        destinatario = "j_hidalgo@gmail.com"
        asunto = "Test Email Debug - GMAO System"
        contenido_html = """
        <html>
        <body>
            <h2>Test de Email Debug</h2>
            <p>Este es un email de prueba para verificar la configuración de SMTP.</p>
            <p>Si recibes este email, la configuración está funcionando correctamente.</p>
            <p>Timestamp: ${timestamp}</p>
        </body>
        </html>
        """.replace(
            "${timestamp}", str(datetime.now())
        )

        logger.info(f"Enviando email de prueba a: {destinatario}")

        result = enviar_email(destinatario, asunto, contenido_html)

        logger.info(f"Resultado del envío: {result}")

        return jsonify(
            {
                "success": True,
                "message": "Email enviado exitosamente",
                "destinatario": destinatario,
                "timestamp": str(datetime.now()),
            }
        )

    except Exception as e:
        logger.error(f"Error en test de email: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Error enviando email de prueba",
                }
            ),
            500,
        )


# Registrar el blueprint
def register_test_email_blueprint(app):
    app.register_blueprint(test_email_bp)
