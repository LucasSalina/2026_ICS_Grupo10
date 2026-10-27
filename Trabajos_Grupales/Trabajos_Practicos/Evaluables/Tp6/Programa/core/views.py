"""Catálogo público de actividades del parque."""

import base64
import logging
from datetime import timedelta

from django.http import Http404, HttpRequest, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from core.consulta_horarios import consultar_horarios_por_actividad
from core.email import enviar_mail_confirmacion_registro_a_actividad
from core.inscripciones import (
    ACTIVIDADES_CON_TALLE,
    TALLES_DISPONIBLES,
    DatosParticipante,
    InscripcionSinParticipantesError,
)
from core.models import CUPO_MAXIMO_POR_ACTIVIDAD, Actividad, Horario, Inscripcion
from core.qr import GenerarQr
from core.validacion_edad import EDADES_MINIMAS_POR_ACTIVIDAD, EdadInvalidaError

logger = logging.getLogger(__name__)

DESCRIPCIONES = {
    "SAFARI": (
        "Un encuentro salvaje.",
        "Recorré el parque y descubrí su fauna de cerca.",
        "safari",
    ),
    "TIROLESA": (
        "El bosque, desde arriba.",
        "Cambiá de perspectiva entre las copas de los árboles.",
        "tirolesa",
    ),
    "PALESTRA": (
        "Un poco más alto.",
        "Encontrá tu camino hacia la cima, una presa a la vez.",
        "palestra",
    ),
    "JARDINERIA": (
        "Manos a la tierra.",
        "Acercate al mundo de las plantas y a sus pequeños habitantes.",
        "jardineria",
    ),
}

TERMINOS_POR_ACTIVIDAD = {
    "SAFARI": (
        "El participante deberá respetar en todo momento las indicaciones del personal encargado de la actividad.",
        "El participante deberá permanecer dentro del recorrido habilitado y no podrá abandonar el grupo sin autorización del guía.",
        "Queda prohibido alimentar, tocar, perseguir o molestar a los animales durante el recorrido.",
        "El participante deberá mantener una conducta respetuosa hacia los animales y el entorno natural.",
        "La actividad podrá suspenderse o reprogramarse por condiciones climáticas desfavorables o por motivos de seguridad y bienestar animal.",
        "La inscripción estará sujeta a la disponibilidad de cupos para el horario seleccionado.",
        "El participante deberá presentarse en el sector correspondiente con anticipación al horario reservado.",
        "La aceptación de estos términos y condiciones será obligatoria para completar la inscripción.",
    ),
    "TIROLESA": (
        "El participante deberá respetar en todo momento las indicaciones del personal encargado de la actividad.",
        "El participante deberá cumplir con los requisitos de seguridad establecidos por EcoHarmony Park antes de utilizar la tirolesa.",
        "El participante deberá informar su edad y talla de vestimenta al momento de la inscripción, para verificar que el equipamiento asignado sea adecuado.",
        "La actividad podrá suspenderse o reprogramarse por condiciones climáticas desfavorables o por motivos de seguridad.",
        "El participante deberá utilizar correctamente el arnés, el casco y los demás elementos de seguridad proporcionados por el parque.",
        "La inscripción estará sujeta a la disponibilidad de cupos para el horario seleccionado.",
        "El participante deberá presentarse en el sector correspondiente con anticipación al horario reservado.",
        "La aceptación de estos términos y condiciones será obligatoria para completar la inscripción.",
    ),
    "PALESTRA": (
        "El participante deberá respetar en todo momento las indicaciones del personal encargado de la actividad.",
        "El participante deberá utilizar correctamente los elementos de protección y aseguramiento proporcionados por el parque.",
        "Antes de comenzar, el participante deberá verificar junto al instructor que el equipamiento se encuentre correctamente colocado.",
        "No estará permitido iniciar el ascenso sin la autorización del instructor responsable.",
        "El participante deberá informar su edad y talla de vestimenta al momento de la inscripción, para permitir la asignación de equipamiento adecuado.",
        "La actividad podrá suspenderse o reprogramarse por condiciones climáticas desfavorables, fallas en el equipamiento o motivos de seguridad.",
        "La inscripción estará sujeta a la disponibilidad de cupos para el horario seleccionado.",
        "El participante deberá presentarse en el sector correspondiente con anticipación al horario reservado.",
        "La aceptación de estos términos y condiciones será obligatoria para completar la inscripción.",
    ),
    "JARDINERIA": (
        "El participante deberá respetar en todo momento las indicaciones del personal encargado de la actividad.",
        "El participante deberá utilizar responsablemente las herramientas y los materiales proporcionados durante la actividad.",
        "Queda prohibido arrancar, dañar o retirar plantas del parque sin autorización del personal responsable.",
        "El participante deberá respetar las especies vegetales y seguir las instrucciones para su cuidado y manipulación.",
        "Las herramientas deberán devolverse al personal encargado al finalizar la actividad.",
        "La actividad podrá suspenderse o reprogramarse por condiciones climáticas desfavorables o por motivos operativos.",
        "La inscripción estará sujeta a la disponibilidad de cupos para el horario seleccionado.",
        "El participante deberá presentarse en el sector correspondiente con anticipación al horario reservado.",
        "La aceptación de estos términos y condiciones será obligatoria para completar la inscripción.",
    ),
}


@require_GET
def catalogo(request: HttpRequest) -> HttpResponse:
    """Presenta las actividades disponibles y sus enlaces de inscripción."""
    nombres = dict(Actividad.OPCIONES_ACTIVIDAD)
    actividades = [
        {
            "codigo": codigo,
            "nombre": nombres[codigo],
            "titulo": contenido[0],
            "descripcion": contenido[1],
            "ilustracion": contenido[2],
            "edad_minima": EDADES_MINIMAS_POR_ACTIVIDAD[codigo],
            "requiere_talle": codigo in ACTIVIDADES_CON_TALLE,
        }
        for codigo, contenido in DESCRIPCIONES.items()
    ]
    return render(
        request,
        "core/catalogo.html",
        {
            "actividades": actividades,
        },
    )


def _leer_entero(texto: str, rechazo: ValueError) -> int:
    """Convierte un campo numérico del formulario o informa el rechazo dado."""
    try:
        return int(texto)
    except ValueError:
        raise rechazo from None


def _leer_participantes(datos: QueryDict) -> list[DatosParticipante]:
    """Arma los datos de cada participante enviado en el formulario."""
    cantidad = _leer_entero(
        datos.get("cantidad_personas", ""),
        InscripcionSinParticipantesError("Indicá la cantidad de participantes."),
    )
    return [
        DatosParticipante(
            nombre=datos.get(f"participante_{numero}_nombre", ""),
            dni=datos.get(f"participante_{numero}_dni", ""),
            edad=_leer_entero(
                datos.get(f"participante_{numero}_edad", ""),
                EdadInvalidaError("La edad debe ser un número entero."),
            ),
            talle=datos.get(f"participante_{numero}_talle", ""),
        )
        for numero in range(1, cantidad + 1)
    ]


def _cantidad_inicial(envio: QueryDict) -> int:
    """Indica cuántos bloques de participantes mostrar al abrir el formulario."""
    try:
        cantidad = int(envio.get("cantidad_personas", ""))
    except ValueError:
        return 1
    return min(max(cantidad, 1), max(CUPO_MAXIMO_POR_ACTIVIDAD.values()))


def _valores_de_participantes(envio: QueryDict) -> list[dict[str, object]]:
    """Prepara un bloque por cada lugar posible con los datos ya enviados."""
    cantidad = _cantidad_inicial(envio)
    return [
        {
            "numero": numero,
            "nombre": envio.get(f"participante_{numero}_nombre", ""),
            "dni": envio.get(f"participante_{numero}_dni", ""),
            "edad": envio.get(f"participante_{numero}_edad", ""),
            "talle": envio.get(f"participante_{numero}_talle", ""),
            "visible": numero <= cantidad,
        }
        for numero in range(1, max(CUPO_MAXIMO_POR_ACTIVIDAD.values()) + 1)
    ]


def _registrar_envio(datos: QueryDict) -> Inscripcion:
    """Registra la inscripción con los campos enviados en el formulario."""
    identificador_horario = datos.get("horario", "")
    if not identificador_horario.isdigit():
        raise Http404("El horario elegido no existe.")
    horario = get_object_or_404(Horario, pk=identificador_horario)
    return horario.registrar_inscripcion(
        correo=datos.get("correo", ""),
        participantes=_leer_participantes(datos),
        acepta_terminos="acepta_terminos" in datos,
    )


def _resumen_de_inscripcion(inscripcion: Inscripcion) -> str:
    """Describe el turno y los participantes de la inscripción, uno por línea."""
    horario = inscripcion.horario
    lineas = [
        f"{horario.actividad} · {horario.fecha:%d/%m/%Y} · {horario.hora:%H:%M}",
        *(
            f"{participante.nombre} · DNI {participante.dni}"
            for participante in inscripcion.participantes.order_by("pk")
        ),
    ]
    return "\n".join(lineas)


def _enviar_confirmacion(inscripcion: Inscripcion, qr: bytes) -> bool:
    """Envía al visitante el resumen y el QR, e indica si el correo salió."""
    try:
        enviar_mail_confirmacion_registro_a_actividad(
            inscripcion.correo,
            qr,
            resumen=_resumen_de_inscripcion(inscripcion),
        )
    except OSError:
        logger.exception(
            "No se pudo enviar el correo de confirmación de la inscripción %s.",
            inscripcion.pk,
        )
        return False
    return True


@require_http_methods(["GET", "POST"])
def inscripcion(request: HttpRequest) -> HttpResponse:
    """Muestra el formulario de inscripción y registra los envíos."""
    if request.method == "POST":
        try:
            inscripcion_registrada = _registrar_envio(request.POST)
        except ValueError as rechazo:
            return _mostrar_formulario(request, error=str(rechazo))
        qr = GenerarQr().generate(f"EcoHarmony-Inscripcion-{inscripcion_registrada.pk}")
        correo_enviado = _enviar_confirmacion(inscripcion_registrada, qr)
        return render(
            request,
            "core/confirmacion.html",
            {
                "inscripcion": inscripcion_registrada,
                "qr": base64.b64encode(qr).decode(),
                "correo_enviado": correo_enviado,
                "arte": {"codigo": inscripcion_registrada.horario.actividad.nombre},
            },
        )
    return _mostrar_formulario(request)


def _mostrar_formulario(request: HttpRequest, error: str = "") -> HttpResponse:
    """Renderiza el formulario visual común para todas las actividades."""
    codigo_actividad = request.GET.get("actividad", "").upper()
    actividad_seleccionada = Actividad.objects.filter(nombre=codigo_actividad).first()
    horarios = (
        consultar_horarios_por_actividad(actividad_seleccionada)
        if actividad_seleccionada is not None
        else []
    )
    fechas_disponibles = sorted({horario.fecha for horario in horarios})
    fecha_seleccionada = request.GET.get("fecha")
    if not fecha_seleccionada and len(fechas_disponibles) == 1:
        fecha_seleccionada = fechas_disponibles[0].isoformat()
    horarios_disponibles = [
        horario
        for horario in horarios
        if horario.fecha.isoformat() == fecha_seleccionada
    ]
    sin_turnos = (
        actividad_seleccionada is not None
        and bool(fecha_seleccionada)
        and not horarios_disponibles
    )
    nombres = dict(Actividad.OPCIONES_ACTIVIDAD)
    actividades = [
        {
            "codigo": codigo.lower(),
            "nombre": nombres[codigo],
            "descripcion": contenido[0],
            "edad_minima": EDADES_MINIMAS_POR_ACTIVIDAD[codigo],
            "requiere_talle": codigo in ACTIVIDADES_CON_TALLE,
            "terminos": TERMINOS_POR_ACTIVIDAD[codigo],
            "arte": {"codigo": codigo},
        }
        for codigo, contenido in DESCRIPCIONES.items()
    ]
    actividad_elegida = next(
        (
            opcion
            for opcion in actividades
            if opcion["codigo"] == codigo_actividad.lower()
        ),
        None,
    )
    return render(
        request,
        "core/inscripcion.html",
        {
            "actividades": actividades,
            "actividad_elegida": actividad_elegida,
            "fechas_disponibles": fechas_disponibles,
            "actividad_seleccionada": (
                codigo_actividad.lower() if codigo_actividad in DESCRIPCIONES else ""
            ),
            "fecha_seleccionada": fecha_seleccionada or "",
            "fecha_elegida": next(
                (
                    fecha
                    for fecha in fechas_disponibles
                    if fecha.isoformat() == fecha_seleccionada
                ),
                None,
            ),
            "hoy": timezone.localdate(),
            "manana": timezone.localdate() + timedelta(days=1),
            "horarios_disponibles": horarios_disponibles,
            "sin_turnos": sin_turnos,
            "error": error,
            "envio": request.POST,
            "participantes": _valores_de_participantes(request.POST),
            "cantidad_inicial": _cantidad_inicial(request.POST),
            "talles": TALLES_DISPONIBLES,
        },
    )
