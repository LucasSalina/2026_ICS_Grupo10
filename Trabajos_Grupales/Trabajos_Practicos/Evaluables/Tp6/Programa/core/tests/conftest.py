"""Configuración compartida por las pruebas de la aplicación."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from pytest_django.fixtures import Settings


@pytest.fixture(autouse=True)
def servidor_smtp() -> Iterator[MagicMock]:
    """Reemplaza el servidor de correo para que ninguna prueba envíe mails reales."""
    with patch("core.email.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        yield mock_server


@pytest.fixture(autouse=True)
def api_brevo(settings: Settings) -> Iterator[MagicMock]:
    """Reemplaza la API de Brevo e ignora la clave que haya en el entorno."""
    settings.BREVO_API_KEY = ""
    with patch("urllib.request.urlopen") as mock_urlopen:
        yield mock_urlopen
