import os
import smtplib
import pytest


class FakeSMTP:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = False
        self.sent = False
        self.msg = None

    def ehlo(self):
        return True

    def starttls(self):
        self.started_tls = True
        return True

    def login(self, username, password):
        self.logged_in = bool(username and password)
        if not self.logged_in:
            raise smtplib.SMTPAuthenticationError(535, b"invalid")
        return True

    def send_message(self, msg):
        self.sent = True
        self.msg = msg
        return {}

    def quit(self):
        return True


def test_enviar_email_missing_config_raises(monkeypatch, app):
    # Limpiar credenciales para forzar error
    monkeypatch.delenv("MAIL_USERNAME", raising=False)
    monkeypatch.delenv("MAIL_PASSWORD", raising=False)

    from app.utils.email_utils import enviar_email

    with app.app_context():
        with pytest.raises(ValueError):
            enviar_email("dest@example.com", "Prueba", "<b>Hola</b>")


def test_enviar_email_success_with_fake_smtp(monkeypatch, app):
    # Configurar la aplicación Flask directamente
    app.config.update(
        {
            "MAIL_SERVER": "smtp.example.com",
            "MAIL_PORT": 587,
            "MAIL_USE_TLS": True,
            "MAIL_USERNAME": "user@example.com",
            "MAIL_PASSWORD": "secret",
        }
    )

    # Reemplazar smtplib.SMTP por stub
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)

    from app.utils.email_utils import enviar_email

    with app.app_context():
        ok = enviar_email("dest@example.com", "Asunto", "<b>Hola</b>")
        assert ok is True


def test_contenido_texto_fallback(monkeypatch, app):
    # Configurar la aplicación Flask directamente
    app.config.update(
        {
            "MAIL_SERVER": "smtp.example.com",
            "MAIL_PORT": 587,
            "MAIL_USE_TLS": True,
            "MAIL_USERNAME": "user@example.com",
            "MAIL_PASSWORD": "secret",
        }
    )

    # Reemplazar smtplib.SMTP por stub que captura el mensaje
    fake = FakeSMTP("smtp.example.com", 587)

    def make_fake(host, port, timeout=None):
        return fake

    monkeypatch.setattr(smtplib, "SMTP", make_fake)

    from app.utils.email_utils import enviar_email

    html = "<html><body><h1>Hola</h1><p>Mundo</p></body></html>"
    with app.app_context():
        ok = enviar_email("dest@example.com", "Asunto", html, contenido_texto=None)
        assert ok is True

    # Verificar que se generó parte de texto plano sin etiquetas
    assert fake.msg is not None
    parts = fake.msg.get_payload()
    # Parte 0: text/plain, Parte 1: text/html
    plain = parts[0].get_payload()
    assert "Hola" in plain and "Mundo" in plain
    assert "<" not in plain and ">" not in plain
