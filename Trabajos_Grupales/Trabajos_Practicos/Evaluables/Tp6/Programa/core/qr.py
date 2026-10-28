"""Genera códigos QR en formato PNG."""

import io

import segno


class GeneradorQr:
    """Convierte un texto en la imagen PNG de su código QR."""

    def __init__(self, escala: int = 10, nivel_de_correccion: str = "m") -> None:
        self.escala = escala
        self.nivel_de_correccion = nivel_de_correccion

    def generar(self, texto: str) -> bytes:
        """Devuelve los bytes PNG del código QR que codifica el texto."""
        qr = segno.make(texto, error=self.nivel_de_correccion)
        buffer = io.BytesIO()
        qr.save(buffer, kind="png", scale=self.escala)
        buffer.seek(0)
        return buffer.getvalue()
