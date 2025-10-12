"""
Sistema de Alertas Inteligente - Servicio de Notificaciones
Servicio para enviar notificaciones por diferentes canales
"""

import smtplib
import json
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from flask import current_app
from app.models.alertas import AlertaHistorial, NotificacionLog
from app.extensions import db

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio de notificaciones multi-canal"""

    def __init__(self):
        self.logger = logger

    def enviar_email_alerta(self, alerta: AlertaHistorial, destinatario: str) -> bool:
        """Envía email de nueva alerta"""
        try:
            asunto = f"🚨 Nueva Alerta: {alerta.configuracion.nombre}"
            cuerpo_html = self.generar_template_alerta_html(alerta)

            return self.enviar_email(destinatario, asunto, cuerpo_html)

        except Exception as e:
            self.logger.error(f"Error enviando email de alerta: {str(e)}")
            return False

    def enviar_email_resolucion(
        self, alerta: AlertaHistorial, destinatario: str
    ) -> bool:
        """Envía email de resolución de alerta"""
        try:
            asunto = f"✅ Alerta Resuelta: {alerta.configuracion.nombre}"
            cuerpo_html = self.generar_template_resolucion_html(alerta)

            return self.enviar_email(destinatario, asunto, cuerpo_html)

        except Exception as e:
            self.logger.error(f"Error enviando email de resolución: {str(e)}")
            return False

    def enviar_email_escalamiento(
        self, alerta: AlertaHistorial, destinatario: str
    ) -> bool:
        """Envía email de escalamiento de alerta"""
        try:
            asunto = f"⚠️ Escalamiento Nivel {alerta.nivel_escalamiento}: {alerta.configuracion.nombre}"
            cuerpo_html = self.generar_template_escalamiento_html(alerta)

            return self.enviar_email(destinatario, asunto, cuerpo_html)

        except Exception as e:
            self.logger.error(f"Error enviando email de escalamiento: {str(e)}")
            return False

    def enviar_email(self, destinatario: str, asunto: str, cuerpo_html: str) -> bool:
        """Método base para enviar emails"""
        try:
            # Configuración SMTP desde variables de entorno
            smtp_server = current_app.config.get("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = current_app.config.get("SMTP_PORT", 587)
            smtp_username = current_app.config.get("SMTP_USERNAME", "")
            smtp_password = current_app.config.get("SMTP_PASSWORD", "")
            smtp_use_tls = current_app.config.get("SMTP_USE_TLS", True)

            if not smtp_username or not smtp_password:
                self.logger.warning("Configuración SMTP incompleta, email no enviado")
                return False

            # Crear mensaje
            mensaje = MIMEMultipart("alternative")
            mensaje["Subject"] = asunto
            mensaje["From"] = smtp_username
            mensaje["To"] = destinatario

            # Adjuntar cuerpo HTML
            parte_html = MIMEText(cuerpo_html, "html", "utf-8")
            mensaje.attach(parte_html)

            # Enviar email
            with smtplib.SMTP(smtp_server, smtp_port) as servidor:
                if smtp_use_tls:
                    servidor.starttls()
                servidor.login(smtp_username, smtp_password)
                servidor.send_message(mensaje)

            self.logger.info(f"Email enviado exitosamente a {destinatario}")
            return True

        except Exception as e:
            self.logger.error(f"Error enviando email: {str(e)}")
            return False

    def generar_template_alerta_html(self, alerta: AlertaHistorial) -> str:
        """Genera template HTML para nueva alerta"""

        # Obtener datos adicionales
        datos_json = ""
        if alerta.datos_json:
            try:
                datos = json.loads(alerta.datos_json)
                datos_json = self.formatear_datos_tabla(datos)
            except:
                datos_json = alerta.datos_json

        # Color según prioridad
        color_prioridad = {
            "critica": "#dc3545",  # Rojo
            "alta": "#fd7e14",  # Naranja
            "media": "#ffc107",  # Amarillo
            "baja": "#28a745",  # Verde
        }.get(alerta.prioridad, "#6c757d")

        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nueva Alerta - GMAO</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #343a40;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background-color: {color_prioridad};
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 30px;
                }}
                .alert-info {{
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .alert-details {{
                    margin: 20px 0;
                }}
                .alert-details table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .alert-details th, .alert-details td {{
                    padding: 8px 12px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }}
                .alert-details th {{
                    background-color: #f8f9fa;
                    font-weight: 600;
                }}
                .priority-badge {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    color: white;
                    background-color: {color_prioridad};
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                    color: #6c757d;
                }}
                .action-button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 10px 5px;
                }}
                .data-table {{
                    width: 100%;
                    margin-top: 15px;
                    border-collapse: collapse;
                    font-size: 14px;
                }}
                .data-table th {{
                    background-color: #e9ecef;
                    padding: 8px;
                    border: 1px solid #dee2e6;
                }}
                .data-table td {{
                    padding: 8px;
                    border: 1px solid #dee2e6;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Nueva Alerta Activada</h1>
                </div>
                
                <div class="content">
                    <div class="alert-info">
                        <h2>{alerta.configuracion.nombre}</h2>
                        <p><strong>Mensaje:</strong> {alerta.mensaje}</p>
                        <p><strong>Prioridad:</strong> <span class="priority-badge">{alerta.prioridad.upper()}</span></p>
                    </div>
                    
                    <div class="alert-details">
                        <h3>Detalles de la Alerta</h3>
                        <table>
                            <tr>
                                <th>ID de Alerta</th>
                                <td>{alerta.id}</td>
                            </tr>
                            <tr>
                                <th>Tipo</th>
                                <td>{alerta.configuracion.tipo_alerta.title()}</td>
                            </tr>
                            <tr>
                                <th>Fecha de Activación</th>
                                <td>{alerta.fecha_activacion.strftime('%d/%m/%Y %H:%M:%S') if alerta.fecha_activacion else 'N/A'}</td>
                            </tr>
                            <tr>
                                <th>Estado</th>
                                <td>{alerta.estado.title()}</td>
                            </tr>
                        </table>
                    </div>
                    
                    {f'<div class="alert-details"><h3>Datos Detectados</h3>{datos_json}</div>' if datos_json else ''}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://mantenimiento-470311.ew.r.appspot.com/dashboard/" class="action-button">
                            Ver en Dashboard
                        </a>
                        <a href="https://mantenimiento-470311.ew.r.appspot.com/alertas/" class="action-button">
                            Gestionar Alertas
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Este es un mensaje automático del Sistema GMAO</p>
                    <p>Fecha de envío: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return template

    def generar_template_resolucion_html(self, alerta: AlertaHistorial) -> str:
        """Genera template HTML para resolución de alerta"""

        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alerta Resuelta - GMAO</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #343a40;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background-color: #28a745;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 30px;
                }}
                .alert-info {{
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Alerta Resuelta</h1>
                </div>
                
                <div class="content">
                    <div class="alert-info">
                        <h2>{alerta.configuracion.nombre}</h2>
                        <p><strong>La alerta ha sido resuelta exitosamente</strong></p>
                        <p><strong>Fecha de resolución:</strong> {alerta.fecha_resolucion.strftime('%d/%m/%Y %H:%M:%S') if alerta.fecha_resolucion else 'N/A'}</p>
                        {f'<p><strong>Notas:</strong> {alerta.notas_resolucion}</p>' if alerta.notas_resolucion else ''}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Este es un mensaje automático del Sistema GMAO</p>
                    <p>Fecha de envío: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return template

    def generar_template_escalamiento_html(self, alerta: AlertaHistorial) -> str:
        """Genera template HTML para escalamiento de alerta"""

        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Escalamiento de Alerta - GMAO</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #343a40;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background-color: #fd7e14;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 30px;
                }}
                .alert-info {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                    color: #6c757d;
                }}
                .urgent {{
                    color: #dc3545;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Escalamiento de Alerta</h1>
                </div>
                
                <div class="content">
                    <div class="alert-info">
                        <h2>{alerta.configuracion.nombre}</h2>
                        <p class="urgent">ATENCIÓN: Esta alerta ha sido escalada al nivel {alerta.nivel_escalamiento}</p>
                        <p><strong>Mensaje:</strong> {alerta.mensaje}</p>
                        <p><strong>Tiempo activa:</strong> {alerta._calcular_tiempo_activa()} minutos</p>
                        <p><strong>Requiere atención inmediata</strong></p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Este es un mensaje automático del Sistema GMAO</p>
                    <p>Fecha de envío: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return template

    def formatear_datos_tabla(self, datos: List[Dict]) -> str:
        """Formatea datos JSON como tabla HTML"""
        if not datos:
            return ""

        if not isinstance(datos, list):
            return str(datos)

        # Obtener las columnas del primer registro
        columnas = list(datos[0].keys())

        html = '<table class="data-table">'

        # Encabezados
        html += "<tr>"
        for columna in columnas:
            html += f'<th>{columna.replace("_", " ").title()}</th>'
        html += "</tr>"

        # Datos (máximo 10 filas para el email)
        for i, fila in enumerate(datos[:10]):
            html += "<tr>"
            for columna in columnas:
                valor = fila.get(columna, "")
                html += f"<td>{valor}</td>"
            html += "</tr>"

        if len(datos) > 10:
            html += f'<tr><td colspan="{len(columnas)}" style="text-align: center; font-style: italic;">... y {len(datos) - 10} registros más</td></tr>'

        html += "</table>"

        return html

    def enviar_notificacion_dashboard(self, alerta: AlertaHistorial, usuario_id: str):
        """Envía notificación al dashboard (placeholder)"""
        # Esta función se implementaría con WebSockets o similar
        # Por ahora, solo registramos en log
        self.logger.info(
            f"Notificación dashboard para usuario {usuario_id}: {alerta.mensaje}"
        )
        return True

    def enviar_reporte_diario(self, destinatarios: List[str]) -> bool:
        """Envía reporte diario de alertas"""
        try:
            from app.models.alertas import AlertaHistorial
            from datetime import date, timedelta

            # Obtener alertas del día
            hoy = date.today()
            ayer = hoy - timedelta(days=1)

            alertas_hoy = AlertaHistorial.query.filter(
                AlertaHistorial.fecha_activacion >= hoy
            ).all()

            alertas_ayer = AlertaHistorial.query.filter(
                AlertaHistorial.fecha_activacion >= ayer,
                AlertaHistorial.fecha_activacion < hoy,
            ).all()

            # Generar reporte
            asunto = f"📊 Reporte Diario de Alertas - {hoy.strftime('%d/%m/%Y')}"
            cuerpo_html = self.generar_template_reporte_diario(
                alertas_hoy, alertas_ayer
            )

            # Enviar a todos los destinatarios
            for destinatario in destinatarios:
                self.enviar_email(destinatario, asunto, cuerpo_html)

            return True

        except Exception as e:
            self.logger.error(f"Error enviando reporte diario: {str(e)}")
            return False

    def generar_template_reporte_diario(self, alertas_hoy, alertas_ayer) -> str:
        """Genera template HTML para reporte diario"""
        # Simplificado por ahora
        return f"""
        <html>
        <body>
            <h1>📊 Reporte Diario de Alertas</h1>
            <h2>Resumen de Hoy</h2>
            <p>Total de alertas: {len(alertas_hoy)}</p>
            <h2>Comparación con Ayer</h2>
            <p>Alertas de ayer: {len(alertas_ayer)}</p>
        </body>
        </html>
        """


# Instancia global del servicio de notificaciones
notification_service = NotificationService()
