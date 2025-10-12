import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

# Configurar logger específico para emails
logger = logging.getLogger(__name__)


def enviar_email(destinatario, asunto, contenido_html, contenido_texto=None):
    """
    Envía un email usando la configuración SMTP

    Args:
        destinatario (str): Email del destinatario
        asunto (str): Asunto del email
        contenido_html (str): Contenido HTML del email
        contenido_texto (str, optional): Contenido de texto plano alternativo
    """
    try:
        # Configuración SMTP desde configuración de Flask (que incluye secrets)
        mail_server = current_app.config.get("MAIL_SERVER", "smtp.gmail.com")
        mail_port = current_app.config.get("MAIL_PORT", 587)
        mail_use_tls = current_app.config.get("MAIL_USE_TLS", True)
        mail_username = current_app.config.get("MAIL_USERNAME")
        mail_password = current_app.config.get("MAIL_PASSWORD")

        if not all([mail_username, mail_password]):
            raise ValueError(
                f"Configuración de email incompleta. MAIL_USERNAME: {'SET' if mail_username else 'MISSING'}, MAIL_PASSWORD: {'SET' if mail_password else 'MISSING'}"
            )

        # Crear mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"] = mail_username
        msg["To"] = destinatario

        # Agregar contenido de texto plano (si no se proporciona, crear uno simple)
        if contenido_texto is None:
            # Extraer texto plano del HTML (versión simplificada)
            import re

            contenido_texto = re.sub(r"<[^>]+>", "", contenido_html)
            contenido_texto = re.sub(r"\s+", " ", contenido_texto).strip()

        # Adjuntar partes del mensaje
        part1 = MIMEText(contenido_texto, "plain", "utf-8")
        part2 = MIMEText(contenido_html, "html", "utf-8")

        msg.attach(part1)
        msg.attach(part2)

        # Conectar al servidor SMTP
        logger.info(f"Conectando a {mail_server}:{mail_port}")
        server = smtplib.SMTP(mail_server, mail_port, timeout=30)
        server.ehlo()

        if mail_use_tls:
            logger.info("Iniciando TLS...")
            server.starttls()
            server.ehlo()

        # Autenticar
        logger.info(f"Autenticando como {mail_username}")
        server.login(mail_username, mail_password)

        # Enviar email
        logger.info(f"Enviando email a {destinatario}")
        # Convertir a bytes con codificación UTF-8
        server.send_message(msg)

        # Cerrar conexión
        server.quit()

        logger.info(f"Email enviado exitosamente a {destinatario}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Error de autenticación SMTP: {e}"
        logger.error(error_msg)
        logger.error(
            "Para Gmail: Asegúrate de usar una contraseña de aplicación si tienes 2FA habilitado"
        )
        logger.error(
            "Crea una contraseña de aplicación en: https://myaccount.google.com/apppasswords"
        )
        raise ValueError(f"{error_msg}. Verifica las credenciales de Gmail.")

    except smtplib.SMTPConnectError as e:
        error_msg = f"Error de conexión SMTP: {e}"
        logger.error(error_msg)
        logger.error(
            "Verifica tu conexión a internet y la configuración del servidor SMTP"
        )
        raise ValueError(f"{error_msg}. Verifica la conexión de red.")

    except smtplib.SMTPException as e:
        error_msg = f"Error SMTP: {e}"
        logger.error(error_msg)
        if "535" in str(e):
            logger.error(
                "Error 535: Credenciales incorrectas. Para Gmail, usa contraseña de aplicación."
            )
        elif "534" in str(e):
            logger.error(
                "Error 534: Autenticación adicional requerida. Habilita aplicaciones menos seguras o usa contraseña de aplicación."
            )
        raise ValueError(f"{error_msg}. Revisa la configuración de Gmail.")

    except Exception as e:
        error_msg = f"Error enviando email a {destinatario}: {e}"
        logger.error(error_msg)
        raise


def enviar_email_solicitud(solicitud):
    """
    Función específica para enviar emails relacionados con solicitudes
    (Mantiene compatibilidad con código existente)
    """
    # Esta función puede ser usada para lógica específica de solicitudes
    # Por ahora delega a la función general
    pass


def enviar_email_confirmacion(solicitud):
    """
    Envía email de confirmación al solicitante
    """
    try:
        asunto = (
            f"Confirmación de Solicitud #{solicitud.numero_solicitud} - GMAO System"
        )

        contenido_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }}
                .header {{ background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; text-align: center; color: #6c757d; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>GMAO System</h1>
                    <p>Solicitud de Servicio Recibida</p>
                </div>
                <div class="content">
                    <h2>¡Gracias por su solicitud!</h2>
                    <p>Estimado/a <strong>{solicitud.nombre_solicitante}</strong>,</p>
                    <p>Hemos recibido su solicitud de servicio y le confirmamos que ha sido registrada exitosamente en nuestro sistema.</p>

                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3>Detalles de la Solicitud:</h3>
                        <p><strong>Número de Solicitud:</strong> {solicitud.numero_solicitud}</p>
                        <p><strong>Fecha:</strong> {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
                        <p><strong>Tipo de Servicio:</strong> {solicitud.tipo_servicio_display}</p>
                        <p><strong>Prioridad:</strong> {solicitud.prioridad_display}</p>
                        <p><strong>Estado:</strong> {solicitud.estado_display}</p>
                    </div>

                    <p><strong>¿Qué sucede ahora?</strong></p>
                    <ol>
                        <li>Su solicitud será revisada por nuestro equipo técnico</li>
                        <li>Recibirá actualizaciones por email sobre el progreso</li>
                        <li>Puede consultar el estado en cualquier momento usando el siguiente enlace:</li>
                    </ol>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config['SERVER_URL']}/solicitudes/seguimiento/{solicitud.numero_solicitud}"
                           class="button">Seguir Solicitud</a>
                    </div>

                    <p>Si tiene alguna pregunta, no dude en contactarnos.</p>
                    <p>Atentamente,<br>Equipo de GMAO System</p>
                </div>
                <div class="footer">
                    <p>Este es un mensaje automático, por favor no responda a este email.</p>
                    <p>© 2024 GMAO System - Sistema de Gestión de Mantenimiento</p>
                </div>
            </div>
        </body>
        </html>
        """

        enviar_email(solicitud.email_solicitante, asunto, contenido_html)
        logger.info(f"Email de confirmación enviado a {solicitud.email_solicitante}")

    except Exception as e:
        logger.error(f"Error enviando email de confirmación: {e}")
        raise


def enviar_email_notificacion_admin(solicitud):
    """
    Envía notificación por email a los administradores sobre nueva solicitud
    """
    try:
        # Obtener emails de administradores desde la base de datos
        from app.models.usuario import Usuario

        admins = Usuario.query.filter_by(rol="Administrador", activo=True).all()
        admin_emails = [admin.email for admin in admins if admin.email]

        # Si no hay administradores en BD, usar email de variable de entorno
        if not admin_emails:
            admin_email_env = current_app.config.get("ADMIN_EMAILS")
            if admin_email_env:
                admin_emails = [admin_email_env]
                logger.info(
                    f"Usando email de administrador desde configuración: {admin_email_env}"
                )
            else:
                logger.warning(
                    "No se encontraron administradores con email válido y ADMIN_EMAILS no está configurado"
                )
                return

        asunto = f"Nueva Solicitud de Servicio #{solicitud.numero_solicitud}"

        contenido_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #dc3545;">Nueva Solicitud de Servicio Recibida</h2>

            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3>Detalles de la Solicitud</h3>
                <p><strong>Número:</strong> {solicitud.numero_solicitud}</p>
                <p><strong>Fecha:</strong> {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Solicitante:</strong> {solicitud.nombre_solicitante}</p>
                <p><strong>Email:</strong> {solicitud.email_solicitante}</p>
                {f'<p><strong>Teléfono:</strong> {solicitud.telefono_solicitante}</p>' if solicitud.telefono_solicitante else ''}
                {f'<p><strong>Empresa:</strong> {solicitud.empresa_solicitante}</p>' if solicitud.empresa_solicitante else ''}
                <p><strong>Tipo:</strong> {solicitud.tipo_servicio_display}</p>
                <p><strong>Prioridad:</strong> {solicitud.prioridad_display}</p>
                <p><strong>Título:</strong> {solicitud.titulo}</p>
                <p><strong>Descripción:</strong> {solicitud.descripcion}</p>
                {f'<p><strong>Ubicación:</strong> {solicitud.ubicacion}</p>' if solicitud.ubicacion else ''}
                {f'<p><strong>Activo Afectado:</strong> {solicitud.activo_afectado}</p>' if solicitud.activo_afectado else ''}
            </div>

            <p><a href="{current_app.config['SERVER_URL']}/admin/solicitudes/{solicitud.id}"
                  style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Ver en Sistema GMAO
            </a></p>

            <p>Esta es una notificación automática del sistema GMAO.</p>
        </div>
        """

        # Enviar a todos los administradores
        for email in admin_emails:
            try:
                enviar_email(email, asunto, contenido_html)
                logger.info(f"Notificación enviada a administrador: {email}")
            except Exception as e:
                logger.error(f"Error enviando notificación a {email}: {e}")

    except Exception as e:
        logger.error(f"Error enviando notificación a administradores: {e}")
        raise
