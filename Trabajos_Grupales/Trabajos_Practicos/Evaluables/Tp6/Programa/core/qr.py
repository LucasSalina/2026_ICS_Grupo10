"""Genera códigos QR en formato PNG."""

import io

import segno


class GenerarQr:
    """Convierte un texto en la imagen PNG de su código QR."""

    def __init__(self, scale: int = 10, error: str = "m") -> None:
        self.scale = scale
        self.error = error

    def generar(self, data: str) -> bytes:
        """Devuelve los bytes PNG del código QR que codifica el texto."""
        qr = segno.make(data, error=self.error)
        buffer = io.BytesIO()
        qr.save(buffer, kind="png", scale=self.scale)
        buffer.seek(0)
        return buffer.getvalue()
