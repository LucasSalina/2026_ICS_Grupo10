"""Comprueba la generación de códigos QR."""

from core.qr import GeneradorQr


def test_generacion_qr_es_imagen() -> None:
    """Genera el QR como una imagen PNG en bytes."""
    resultado = GeneradorQr().generar("test")

    # Todo archivo PNG comienza con esta firma.
    assert isinstance(resultado, bytes)
    assert resultado.startswith(b"\x89PNG")
