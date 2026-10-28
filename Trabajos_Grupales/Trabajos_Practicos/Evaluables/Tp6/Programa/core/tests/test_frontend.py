"""Prueba la integración HTTP del catálogo y sus enlaces de inscripción."""

import base64
import re
import urllib.error
from collections.abc import Iterator
from datetime import date, datetime, time
from unittest.mock import MagicMock, patch

import pytest
from django.test import Client
from django.utils import timezone
from pytest_django.fixtures import Settings

from core.models import Actividad, Horario, Inscripcion
from core.qr import GeneradorQr

URL_FORMULARIO_TIROLESA = "/inscripcion/?actividad=tirolesa&fecha=2026-10-20"


@pytest.fixture
def reloj_controlado() -> Iterator[None]:
    """Fija el reloj una hora antes del turno de las pruebas."""
    with patch(
        "django.utils.timezone.now",
        return_value=datetime(2026, 10, 20, 9, tzinfo=timezone.get_current_timezone()),
    ):
        yield


@pytest.fixture
def horario_tirolesa(reloj_controlado: None) -> Horario:
    """Crea un turno reservable de Tirolesa."""
    tirolesa = Actividad.objects.create(nombre="TIROLESA", cupo_maximo=10)
    return Horario.objects.create(
        actividad=tirolesa, fecha=date(2026, 10, 20), hora=time(10)
    )


def datos_de_inscripcion(horario: Horario) -> dict[str, str]:
    """Arma los campos que envía el formulario para un grupo de dos personas."""
    return {
        "horario": str(horario.pk),
        "cantidad_personas": "2",
        "participante_1_nombre": "Ana Pérez",
        "participante_1_dni": "30111222",
        "participante_1_edad": "35",
        "participante_1_talle": "M",
        "participante_2_nombre": "Juan Pérez",
        "participante_2_dni": "50111222",
        "participante_2_edad": "10",
        "participante_2_talle": "S",
        "correo": "ana@ejemplo.com",
        "acepta_terminos": "on",
    }


def test_catalogo_muestra_actividades_con_enlaces_de_inscripcion(
    client: Client,
) -> None:
    respuesta = client.get("/")
    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert "Jardinería" in contenido
    assert contenido.count('class="button button-dark">Inscribirme') == 4
    assert 'href="/inscripcion/?actividad=safari"' in contenido
    assert 'href="/inscripcion/?actividad=jardineria"' in contenido
    assert "Consultar edad" not in contenido
    assert 'id="id_edad"' not in contenido


def test_catalogo_no_acepta_envios_de_formulario(client: Client) -> None:
    respuesta = client.post("/")
    assert respuesta.status_code == 405


def test_catalogo_no_presenta_la_capacidad_como_disponibilidad(client: Client) -> None:
    """Deja los lugares disponibles para el turno elegido en la inscripción."""
    respuesta = client.get("/")

    assert "personas por turno" not in respuesta.content.decode()


@pytest.mark.django_db
def test_formulario_muestra_fecha_y_horarios(client: Client) -> None:
    respuesta = client.get("/inscripcion/?actividad=safari")
    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert 'id="fecha-visita"' in contenido
    assert "No se admiten reservas con más de 24 horas de anticipación" in contenido
    assert "Los turnos se habilitan hasta 15 minutos antes" in contenido


@pytest.mark.django_db
def test_formulario_no_muestra_precios_de_entradas(client: Client) -> None:
    """Deja los precios y descuentos de entradas a la compra de entradas."""
    respuesta = client.get("/inscripcion/?actividad=safari")

    contenido = respuesta.content.decode()
    assert "Precios de entradas" not in contenido
    assert "$10.000" not in contenido
    assert "50% de descuento" not in contenido


@pytest.mark.django_db
@pytest.mark.parametrize(
    "codigo",
    [
        "safari",
        "tirolesa",
        "palestra",
        "jardineria",
    ],
)
def test_una_pagina_de_inscripcion_preselecciona_actividad_por_query(
    client: Client, codigo: str
) -> None:
    respuesta = client.get(f"/inscripcion/?actividad={codigo}")
    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert contenido.count("<legend>Participante ") == 12
    assert 'id="actividad"' in contenido
    assert contenido.count('type="radio" name="actividad"') == 4
    assert (
        f'name="actividad" value="{codigo}" form="consulta-turnos" required checked>'
        in contenido
    )
    assert "Elegí una fecha para ver los turnos." in contenido
    assert 'id="fecha-visita"' in contenido
    assert 'name="cantidad_personas"' in contenido
    assert "inscripcion.js" in contenido
    assert "código QR" in contenido
    assert "inscripcion.js" in contenido


@pytest.mark.django_db
def test_selector_ofrece_el_ultimo_turno_del_dia(client: Client) -> None:
    """Ofrece el turno de las 17:00, el último que comienza dentro del horario."""
    tirolesa = Actividad.objects.create(nombre="TIROLESA", cupo_maximo=10)
    Horario.objects.create(actividad=tirolesa, fecha=date(2026, 10, 20), hora=time(17))

    with patch(
        "django.utils.timezone.now",
        return_value=datetime(
            2026, 10, 20, 16, 30, tzinfo=timezone.get_current_timezone()
        ),
    ):
        respuesta = client.get(URL_FORMULARIO_TIROLESA)

    turno = re.search(
        r'<label class="choice-chip time-chip">.*?</label>',
        respuesta.content.decode(),
        flags=re.DOTALL,
    )
    assert turno is not None
    assert "17:00" in turno.group()
    assert "10 lugares" in turno.group()


@pytest.mark.django_db
def test_formulario_presenta_los_datos_de_la_actividad_elegida(client: Client) -> None:
    """Muestra el título, los términos y el talle propios de la actividad."""
    respuesta = client.get("/inscripcion/?actividad=tirolesa")

    contenido = respuesta.content.decode()
    assert "Inscripción a Tirolesa." in contenido
    assert "Términos y condiciones de Tirolesa" in contenido
    assert "informar su edad y talla de vestimenta" in contenido
    assert 'name="participante_1_talle"' in contenido


@pytest.mark.django_db
def test_formulario_no_pide_talle_en_actividades_que_no_lo_requieren(
    client: Client,
) -> None:
    """Omite el talle de vestimenta cuando la actividad no lo usa."""
    respuesta = client.get("/inscripcion/?actividad=safari")

    assert 'name="participante_1_talle"' not in respuesta.content.decode()


@pytest.mark.django_db
def test_formulario_presenta_los_terminos_como_vigentes(client: Client) -> None:
    """No anuncia los términos como provisorios ahora que la inscripción funciona."""
    respuesta = client.get("/inscripcion/?actividad=safari")

    contenido = respuesta.content.decode()
    assert "Términos y condiciones de" in contenido
    assert "Condiciones preliminares" not in contenido


@pytest.mark.django_db
def test_formulario_no_pide_datos_que_la_inscripcion_no_guarda(
    client: Client,
) -> None:
    """Omite el nombre de un coordinador, que no forma parte de la inscripción."""
    respuesta = client.get("/inscripcion/?actividad=safari")

    assert 'name="nombre_actividad"' not in respuesta.content.decode()


def test_formulario_inscripcion_rechaza_metodos_no_admitidos(client: Client) -> None:
    respuesta = client.put("/inscripcion/")
    assert respuesta.status_code == 405


def test_inscripcion_ya_no_tiene_ruta_por_actividad(client: Client) -> None:
    respuesta = client.get("/inscripcion/safari/")
    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_formulario_registra_la_inscripcion_enviada(
    client: Client, horario_tirolesa: Horario
) -> None:
    """Guarda la inscripción del grupo y muestra la confirmación."""
    respuesta = client.post(
        URL_FORMULARIO_TIROLESA,
        datos_de_inscripcion(horario_tirolesa),
    )

    assert respuesta.status_code == 200
    assert "Inscripción confirmada" in respuesta.content.decode()
    inscripcion = Inscripcion.objects.get()
    assert inscripcion.horario == horario_tirolesa
    assert inscripcion.correo == "ana@ejemplo.com"
    assert list(
        inscripcion.participantes.order_by("dni").values_list(
            "nombre", "dni", "edad", "talle"
        )
    ) == [
        ("Ana Pérez", "30111222", 35, "M"),
        ("Juan Pérez", "50111222", 10, "S"),
    ]


@pytest.mark.django_db
def test_formulario_muestra_el_error_de_una_inscripcion_rechazada(
    client: Client, horario_tirolesa: Horario
) -> None:
    """Vuelve al formulario con el motivo del rechazo y no guarda nada."""
    datos = datos_de_inscripcion(horario_tirolesa) | {"participante_2_dni": "123"}

    respuesta = client.post(URL_FORMULARIO_TIROLESA, datos)

    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert 'id="registration-form"' in contenido
    assert "El DNI debe tener 7 u 8 dígitos, sin puntos." in contenido
    assert not Inscripcion.objects.exists()


def envio_rechazado(client: Client, horario: Horario) -> str:
    """Envía una inscripción con un DNI inválido y devuelve el formulario."""
    datos = datos_de_inscripcion(horario) | {"participante_2_dni": "123"}
    return client.post(URL_FORMULARIO_TIROLESA, datos).content.decode()


@pytest.mark.django_db
def test_formulario_rechazado_conserva_el_correo_y_la_cantidad(
    client: Client, horario_tirolesa: Horario
) -> None:
    """Evita que el visitante vuelva a escribir sus datos de contacto."""
    contenido = envio_rechazado(client, horario_tirolesa)

    assert 'name="correo" type="email" value="ana@ejemplo.com"' in contenido
    assert 'name="cantidad_personas" type="number" value="2"' in contenido


@pytest.mark.django_db
def test_formulario_rechazado_conserva_los_datos_de_los_participantes(
    client: Client, horario_tirolesa: Horario
) -> None:
    """Muestra nuevamente el nombre, DNI, edad y talle de cada participante."""
    contenido = envio_rechazado(client, horario_tirolesa)

    assert 'name="participante_1_nombre" type="text" value="Ana Pérez"' in contenido
    assert 'name="participante_1_dni" type="text" value="30111222"' in contenido
    assert 'name="participante_1_edad" type="number" value="35"' in contenido
    assert 'name="participante_2_dni" type="text" value="123"' in contenido
    assert '<option value="S" selected>S</option>' in contenido


@pytest.mark.django_db
def test_formulario_rechazado_conserva_el_horario_elegido(
    client: Client, horario_tirolesa: Horario
) -> None:
    """Mantiene seleccionado el turno que había elegido el visitante."""
    contenido = envio_rechazado(client, horario_tirolesa)

    assert (
        f'name="horario" value="{horario_tirolesa.pk}" data-cupos="10" required checked>'
        in contenido
    )


@pytest.mark.django_db
def test_formulario_rechazado_conserva_la_aceptacion_de_los_terminos(
    client: Client, horario_tirolesa: Horario
) -> None:
    """No obliga a volver a aceptar términos que ya fueron aceptados."""
    contenido = envio_rechazado(client, horario_tirolesa)

    assert 'name="acepta_terminos" required checked>' in contenido


@pytest.mark.django_db
@pytest.mark.parametrize(
    "edad",
    [
        pytest.param("", id="vacia"),
        pytest.param("diez", id="en_letras"),
    ],
)
def test_formulario_rechaza_una_edad_no_numerica(
    client: Client, horario_tirolesa: Horario, edad: str
) -> None:
    """Informa que la edad debe ser un número en lugar de fallar."""
    datos = datos_de_inscripcion(horario_tirolesa) | {"participante_1_edad": edad}

    respuesta = client.post(URL_FORMULARIO_TIROLESA, datos)

    assert "La edad debe ser un número entero." in respuesta.content.decode()
    assert not Inscripcion.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "cantidad",
    [
        pytest.param("", id="vacia"),
        pytest.param("dos", id="en_letras"),
    ],
)
def test_formulario_rechaza_una_cantidad_de_participantes_no_numerica(
    client: Client, horario_tirolesa: Horario, cantidad: str
) -> None:
    """Pide indicar la cantidad de participantes en lugar de fallar."""
    datos = datos_de_inscripcion(horario_tirolesa) | {"cantidad_personas": cantidad}

    respuesta = client.post(URL_FORMULARIO_TIROLESA, datos)

    assert "Indicá la cantidad de participantes." in respuesta.content.decode()
    assert not Inscripcion.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("campo", "mensaje"),
    [
        pytest.param(
            "cantidad_personas", "Indicá la cantidad de participantes.", id="cantidad"
        ),
        pytest.param("correo", "Ingresá un correo electrónico válido.", id="correo"),
        pytest.param(
            "participante_2_nombre",
            "Indicá el nombre de cada participante.",
            id="nombre",
        ),
        pytest.param(
            "participante_2_dni",
            "El DNI debe tener 7 u 8 dígitos, sin puntos.",
            id="dni",
        ),
        pytest.param(
            "participante_2_edad", "La edad debe ser un número entero.", id="edad"
        ),
    ],
)
def test_formulario_informa_los_campos_faltantes(
    client: Client, horario_tirolesa: Horario, campo: str, mensaje: str
) -> None:
    """Vuelve al formulario con el motivo cuando el envío omite un campo."""
    datos = datos_de_inscripcion(horario_tirolesa)
    del datos[campo]

    respuesta = client.post(URL_FORMULARIO_TIROLESA, datos)

    assert respuesta.status_code == 200
    assert mensaje in respuesta.content.decode()
    assert not Inscripcion.objects.exists()


@pytest.mark.django_db
def test_formulario_responde_404_ante_un_horario_inexistente(
    client: Client, horario_tirolesa: Horario
) -> None:
    """No registra envíos para turnos que no existen."""
    datos = datos_de_inscripcion(horario_tirolesa) | {
        "horario": str(horario_tirolesa.pk + 1)
    }

    respuesta = client.post(URL_FORMULARIO_TIROLESA, datos)

    assert respuesta.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "horario",
    [
        pytest.param("", id="vacio"),
        pytest.param("diez", id="en_letras"),
    ],
)
def test_formulario_responde_404_ante_un_horario_no_numerico(
    client: Client, horario_tirolesa: Horario, horario: str
) -> None:
    """Trata un identificador de turno mal formado como un turno inexistente."""
    datos = datos_de_inscripcion(horario_tirolesa) | {"horario": horario}

    respuesta = client.post(URL_FORMULARIO_TIROLESA, datos)

    assert respuesta.status_code == 404


@pytest.mark.django_db
def test_formulario_se_envia_por_post(client: Client) -> None:
    """Habilita el envío del formulario con protección CSRF."""
    respuesta = client.get("/inscripcion/?actividad=safari")

    contenido = respuesta.content.decode()
    assert 'id="registration-form" method="post"' in contenido
    assert 'name="csrfmiddlewaretoken"' in contenido
    assert 'type="submit">Finalizar inscripción' in contenido
    assert "todavía no están habilitados" not in contenido


@pytest.mark.django_db
def test_formulario_envia_el_correo_de_confirmacion(
    client: Client, horario_tirolesa: Horario, servidor_smtp: MagicMock
) -> None:
    """Envía al visitante el resumen de la inscripción registrada."""
    client.post(URL_FORMULARIO_TIROLESA, datos_de_inscripcion(horario_tirolesa))

    servidor_smtp.send_message.assert_called_once()
    mensaje_enviado = servidor_smtp.send_message.call_args[0][0]
    cuerpo = mensaje_enviado.get_body(preferencelist=("html",)).get_content()
    assert mensaje_enviado["To"] == "ana@ejemplo.com"
    assert "Tirolesa · 20/10/2026 · 10:00" in cuerpo
    assert "Ana Pérez · DNI 30111222" in cuerpo
    assert "Juan Pérez · DNI 50111222" in cuerpo


@pytest.mark.django_db
def test_correo_de_confirmacion_incluye_el_numero_de_orden(
    client: Client, horario_tirolesa: Horario, servidor_smtp: MagicMock
) -> None:
    """Informa en el correo el mismo número que muestra la confirmación."""
    client.post(URL_FORMULARIO_TIROLESA, datos_de_inscripcion(horario_tirolesa))

    mensaje_enviado = servidor_smtp.send_message.call_args[0][0]
    cuerpo = mensaje_enviado.get_body(preferencelist=("html",)).get_content()
    assert f"Inscripción N.º {Inscripcion.objects.get().pk:06d}" in cuerpo


@pytest.mark.django_db
def test_correo_de_confirmacion_incluye_el_qr_de_la_inscripcion(
    client: Client, horario_tirolesa: Horario, servidor_smtp: MagicMock
) -> None:
    """Adjunta un QR que solo codifica el identificador de la inscripción."""
    client.post(URL_FORMULARIO_TIROLESA, datos_de_inscripcion(horario_tirolesa))

    mensaje_enviado = servidor_smtp.send_message.call_args[0][0]
    imagenes = [
        parte.get_content()
        for parte in mensaje_enviado.walk()
        if parte.get_content_type() == "image/png"
    ]
    qr_esperado = GeneradorQr().generar(
        f"EcoHarmony-Inscripcion-{Inscripcion.objects.get().pk}"
    )
    assert imagenes == [qr_esperado]


@pytest.mark.django_db
def test_formulario_confirma_la_inscripcion_aunque_falle_el_correo(
    client: Client,
    horario_tirolesa: Horario,
    servidor_smtp: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Un error del servidor de correo no cancela la inscripción y queda registrado."""
    servidor_smtp.send_message.side_effect = ConnectionRefusedError

    respuesta = client.post(
        URL_FORMULARIO_TIROLESA, datos_de_inscripcion(horario_tirolesa)
    )

    assert "Inscripción confirmada" in respuesta.content.decode()
    assert Inscripcion.objects.exists()
    assert "No se pudo enviar el correo de confirmación" in caplog.text


@pytest.mark.django_db
def test_confirmacion_muestra_el_qr_de_la_inscripcion(
    client: Client, horario_tirolesa: Horario
) -> None:
    """Presenta en pantalla el mismo QR que se envía por correo."""
    respuesta = client.post(
        URL_FORMULARIO_TIROLESA, datos_de_inscripcion(horario_tirolesa)
    )

    qr_esperado = GeneradorQr().generar(
        f"EcoHarmony-Inscripcion-{Inscripcion.objects.get().pk}"
    )
    imagen = base64.b64encode(qr_esperado).decode()
    assert f'src="data:image/png;base64,{imagen}"' in respuesta.content.decode()


@pytest.mark.django_db
def test_confirmacion_avisa_cuando_no_se_pudo_enviar_el_correo(
    client: Client, horario_tirolesa: Horario, servidor_smtp: MagicMock
) -> None:
    """Pide guardar el pase en pantalla si el correo no salió."""
    servidor_smtp.send_message.side_effect = ConnectionRefusedError

    respuesta = client.post(
        URL_FORMULARIO_TIROLESA, datos_de_inscripcion(horario_tirolesa)
    )

    contenido = respuesta.content.decode()
    assert "No pudimos enviar el correo a ana@ejemplo.com" in contenido
    assert "Enviamos el resumen" not in contenido


@pytest.mark.django_db
def test_formulario_confirma_la_inscripcion_aunque_falle_brevo(
    client: Client,
    horario_tirolesa: Horario,
    api_brevo: MagicMock,
    settings: Settings,
) -> None:
    """Un error de la API de Brevo no cancela la inscripción y se avisa en el pase."""
    settings.BREVO_API_KEY = "clave-de-prueba"
    api_brevo.side_effect = urllib.error.URLError("sin conexión")

    respuesta = client.post(
        URL_FORMULARIO_TIROLESA, datos_de_inscripcion(horario_tirolesa)
    )

    assert Inscripcion.objects.exists()
    assert "No pudimos enviar el correo a ana@ejemplo.com" in respuesta.content.decode()
