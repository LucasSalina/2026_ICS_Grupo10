"""Comprueba el envío del correo de confirmación mediante la API de Brevo."""

import base64
import json
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_django.fixtures import Settings

from core.email import enviar_mail_confirmacion_registro_a_actividad


@pytest.fixture
def clave_brevo(settings: Settings) -> None:
    """Configura una clave de Brevo para que el correo salga por su API."""
    settings.BREVO_API_KEY = "clave-de-prueba"


def datos_enviados_a_brevo(api_brevo: MagicMock) -> Any:
    """Devuelve el contenido JSON de la solicitud enviada a Brevo."""
    return json.loads(api_brevo.call_args[0][0].data)


@pytest.mark.usefixtures("clave_brevo")
def test_con_clave_de_brevo_envia_el_correo_por_su_api(
    api_brevo: MagicMock, servidor_smtp: MagicMock
) -> None:
    """Entrega el correo a la API de Brevo en lugar del servidor SMTP."""
    enviar_mail_confirmacion_registro_a_actividad("ana@ejemplo.com", b"qr_falso")

    api_brevo.assert_called_once()
    solicitud = api_brevo.call_args[0][0]
    assert solicitud.full_url == "https://api.brevo.com/v3/smtp/email"
    assert solicitud.get_method() == "POST"
    assert solicitud.get_header("Api-key") == "clave-de-prueba"
    servidor_smtp.send_message.assert_not_called()


@pytest.mark.usefixtures("clave_brevo")
def test_brevo_dirige_el_correo_al_destinatario(api_brevo: MagicMock) -> None:
    """Indica a Brevo la dirección del visitante que se inscribió."""
    enviar_mail_confirmacion_registro_a_actividad("ana@ejemplo.com", b"qr_falso")

    assert datos_enviados_a_brevo(api_brevo)["to"] == [{"email": "ana@ejemplo.com"}]


@pytest.mark.usefixtures("clave_brevo")
def test_brevo_recibe_los_datos_como_json(api_brevo: MagicMock) -> None:
    """Declara el formato JSON que exige la API de Brevo."""
    enviar_mail_confirmacion_registro_a_actividad("ana@ejemplo.com", b"qr_falso")

    solicitud = api_brevo.call_args[0][0]
    assert solicitud.get_header("Content-type") == "application/json"


@pytest.mark.usefixtures("clave_brevo")
def test_brevo_envia_desde_el_remitente_configurado(
    api_brevo: MagicMock, settings: Settings
) -> None:
    """Usa como remitente la dirección verificada en Brevo."""
    settings.CORREO_REMITENTE = "parque@ejemplo.com"

    enviar_mail_confirmacion_registro_a_actividad("ana@ejemplo.com", b"qr_falso")

    assert datos_enviados_a_brevo(api_brevo)["sender"] == {
        "name": "EcoHarmony Park",
        "email": "parque@ejemplo.com",
    }


@pytest.mark.usefixtures("clave_brevo")
def test_brevo_envia_el_asunto_de_la_confirmacion(api_brevo: MagicMock) -> None:
    """Titula el correo como confirmación de la inscripción."""
    enviar_mail_confirmacion_registro_a_actividad("ana@ejemplo.com", b"qr_falso")

    assert (
        datos_enviados_a_brevo(api_brevo)["subject"]
        == "Tu inscripción en EcoHarmony Park está confirmada"
    )


@pytest.mark.usefixtures("clave_brevo")
def test_brevo_incluye_el_resumen_en_el_cuerpo(api_brevo: MagicMock) -> None:
    """Agrega al cuerpo HTML el resumen de la inscripción."""
    enviar_mail_confirmacion_registro_a_actividad(
        "ana@ejemplo.com", b"qr_falso", resumen="Tirolesa · 20/10/2026 · 10:00"
    )

    assert (
        "Tirolesa · 20/10/2026 · 10:00"
        in datos_enviados_a_brevo(api_brevo)["htmlContent"]
    )


@pytest.mark.usefixtures("clave_brevo")
def test_brevo_adjunta_el_qr_de_la_inscripcion(api_brevo: MagicMock) -> None:
    """Adjunta el QR en PNG, porque Brevo no admite imágenes incrustadas."""
    enviar_mail_confirmacion_registro_a_actividad("ana@ejemplo.com", b"qr_falso")

    assert datos_enviados_a_brevo(api_brevo)["attachment"] == [
        {"name": "qr.png", "content": base64.b64encode(b"qr_falso").decode()}
    ]
