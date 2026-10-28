"""Comprueba el formato del correo de confirmación."""

from unittest.mock import MagicMock, patch

from core.email import enviar_mail_confirmacion_registro_a_actividad


@patch("core.email.smtplib.SMTP")
def test_enviar_mail_envia_imagen_inline(mock_smtp: MagicMock) -> None:
    """Envía un mensaje multiparte con el QR incluido en el cuerpo."""
    # SMTP se usa como context manager: el servidor es lo que devuelve __enter__.
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    enviar_mail_confirmacion_registro_a_actividad("test@ejemplo.com", b"qr_falso")

    mock_server.send_message.assert_called_once()
    mensaje_enviado = mock_server.send_message.call_args[0][0]
    assert mensaje_enviado.is_multipart()
