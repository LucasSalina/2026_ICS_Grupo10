"""Comprueba la generación de códigos QR."""

from core.qr import GenerarQr


def test_generacion_qr_es_imagen() -> None:
    """Genera el QR como una imagen PNG en bytes."""
    resultado = GenerarQr().generar("test")

    # Todo archivo PNG comienza con esta firma.
    assert isinstance(resultado, bytes)
    assert resultado.startswith(b"\x89PNG")
