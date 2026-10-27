# Entorno de desarrollo del TP6

Ejecutar los comandos siguientes desde esta carpeta (`Programa`).
El entorno verificado usa **CPython 3.14.8 en macOS ARM64**, la version que fija
la guia de estilo (`../Material_Adicional/2026-ICS_Produccion_TP6_ConradoJuncos.pdf`).
No se ha verificado esta instalacion en otros sistemas operativos.

## Instalacion

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
```

`requirements.txt` contiene Django, Segno, gunicorn, whitenoise y las
dependencias transitivas de ejecucion. `requirements-dev.txt` incluye ese archivo y agrega pytest,
pytest-django, Black, Ruff y mypy con sus dependencias. Para instalar solamente
lo necesario para ejecutar la aplicacion, usar `-r requirements.txt`.
No se necesita instalar paquetes globales ni usar `--break-system-packages`.

Las versiones estan fijadas para el entorno indicado. Al actualizarlas, comprobar
la instalacion en un entorno nuevo, ejecutar las verificaciones y actualizar
tambien las dependencias transitivas. No reemplazar estos archivos con un
`pip freeze` de un entorno que contenga paquetes de otros proyectos.

## Verificaciones

```bash
python -m pytest -q --migrations
python manage.py check
python manage.py makemigrations --check --dry-run
python -m black --check .
python -m ruff check .
python -m mypy .
```

Las pruebas usan la base de test de Django; no requieren migrar la SQLite de
desarrollo ni iniciar un servidor SMTP. `--migrations` explicita que se verifica
el esquema instalado desde migraciones.

`mypy.ini` ignora los imports sin tipos (Django y Segno no los publican) y
excluye las migraciones generadas, por lo que mypy no verifica el tipado
interno de Django.

## Arranque local

Antes de migrar una base existente, revisar nombres de actividades duplicados:
la migracion de unicidad los rechaza y no los elimina automaticamente. Para una
base nueva o una base revisada:

```bash
python manage.py migrate
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>. Al finalizar una inscripcion, la aplicacion la
registra, muestra la confirmacion y envia el correo con el resumen y el codigo QR.

El correo se envia a un servidor SMTP en `localhost:1025`, configurable con
`CORREO_SMTP_HOST` y `CORREO_SMTP_PUERTO` en `config/settings.py`. Estos
requirements no instalan ni inician ese servidor. Sin servidor, la inscripcion se registra igual
y el error de envio aparece en la terminal de `runserver`. Para ver los correos
durante una demostracion se puede iniciar un servidor SMTP local de pruebas en
ese puerto, por ejemplo Mailpit (interfaz web en <http://127.0.0.1:8025/>).

## Envio de correos con Brevo

Si la variable de entorno `BREVO_API_KEY` tiene una clave, el correo se envia
por la API HTTP de Brevo en lugar de SMTP. `CORREO_REMITENTE` debe ser una
direccion verificada como remitente en esa cuenta de Brevo. Brevo no admite
imagenes incrustadas, por lo que el QR viaja como adjunto `qr.png`.

```bash
export BREVO_API_KEY="<clave de Brevo>"
export CORREO_REMITENTE="<remitente verificado>"
python manage.py runserver
```

La clave nunca se versiona. Las pruebas simulan la API y la ignoran aunque este
definida en el entorno.

## Despliegue en Render

`render.yaml` define un Web Service gratuito. En Render: **New > Blueprint**,
elegir el repositorio e indicar como Blueprint Path
`Trabajos_Grupales/Trabajos_Practicos/Evaluables/Tp6/Programa/render.yaml`.

Render genera `DJANGO_SECRET_KEY` y desactiva `DEBUG`; sin esas variables,
`settings.py` usa los valores de desarrollo. El disco del plan gratuito no
persiste: cada arranque migra la base y carga los turnos de los proximos siete
dias, por lo que las inscripciones se pierden al reiniciarse el servicio.

Render bloquea el SMTP saliente en el plan gratuito, por lo que el correo sale
por Brevo. Al crear el Blueprint, Render pide los valores de `BREVO_API_KEY` y
`CORREO_REMITENTE`. Sin ellos, la confirmacion avisa que el correo no pudo
enviarse.
