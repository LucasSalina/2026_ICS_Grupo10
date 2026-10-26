"""Envía los correos de confirmación de inscripción a los visitantes."""

import base64
import json
import smtplib
import urllib.request
from email.message import EmailMessage
from email.utils import make_msgid

from django.conf import settings
from django.template.loader import render_to_string

URL_API_BREVO = "https://api.brevo.com/v3/smtp/email"
ESPERA_MAXIMA_BREVO_SEGUNDOS = 10
ASUNTO_CONFIRMACION = "Tu inscripción en EcoHarmony Park está confirmada"


def _enviar_por_brevo(destinatario: str, qr: bytes, resumen: str) -> None:
    """Entrega el correo de confirmación a la API de Brevo."""
    datos: dict[str, object] = {
        "sender": {"name": "EcoHarmony Park", "email": settings.CORREO_REMITENTE},
        "to": [{"email": destinatario}],
        "subject": ASUNTO_CONFIRMACION,
        "htmlContent": render_to_string(
            "core/correo_confirmacion.html", {"resumen": resumen}
        ),
        "attachment": [{"name": "qr.png", "content": base64.b64encode(qr).decode()}],
    }
    solicitud = urllib.request.Request(
        URL_API_BREVO,
        data=json.dumps(datos).encode(),
        headers={
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(solicitud, timeout=ESPERA_MAXIMA_BREVO_SEGUNDOS):
        pass


def enviar_mail_confirmacion_registro_a_actividad(
    destinatario: str, qr: bytes, resumen: str = ""
) -> None:
    """Envía el resumen de la inscripción con su código QR incrustado."""
    if settings.BREVO_API_KEY:
        _enviar_por_brevo(destinatario, qr, resumen)
        return
    cid_qr = make_msgid(domain="ecoharmony.park")
    msg = EmailMessage()
    msg["Subject"] = ASUNTO_CONFIRMACION
    msg["From"] = "EcoHarmony Park <noreply@example.com>"
    msg["To"] = destinatario
    msg.set_content(
        render_to_string(
            "core/correo_confirmacion.html",
            {"resumen": resumen, "cid_qr": cid_qr[1:-1]},
        ),
        subtype="html",
    )

    # El cid permite que el HTML muestre el QR inline en lugar de adjunto.
    msg.add_related(qr, maintype="image", subtype="png", cid=cid_qr)

    with smtplib.SMTP(settings.CORREO_SMTP_HOST, settings.CORREO_SMTP_PUERTO) as server:
        server.send_message(msg)
