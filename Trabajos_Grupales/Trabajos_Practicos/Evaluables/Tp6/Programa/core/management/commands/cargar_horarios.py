"""Carga horarios de muestra para los siete días abiertos desde hoy."""

from datetime import timedelta
from typing import Any

from django.core.management import BaseCommand, call_command
from django.utils import timezone

from core.models import (
    DIA_LUNES,
    FERIADOS_DE_CIERRE,
    HORAS_DE_INICIO_PERMITIDAS,
    Actividad,
    Horario,
)

DIAS_ABIERTOS_A_CARGAR = 7


class Command(BaseCommand):
    """Genera horarios de muestra respetando los días y horas de apertura."""

    help = "Carga horarios de muestra para los siete días abiertos desde hoy."

    def handle(self, *args: Any, **options: Any) -> None:
        """Crea los turnos de cada actividad sin duplicar los existentes."""
        call_command("cargar_actividades")
        actividades = Actividad.objects.all()
        fecha = timezone.localdate()
        dias_abiertos = 0
        horarios_creados = 0

        while dias_abiertos < DIAS_ABIERTOS_A_CARGAR:
            es_feriado = (fecha.month, fecha.day) in FERIADOS_DE_CIERRE
            if fecha.weekday() != DIA_LUNES and not es_feriado:
                dias_abiertos += 1
                for actividad in actividades:
                    for hora in sorted(HORAS_DE_INICIO_PERMITIDAS):
                        _, creado = Horario.objects.get_or_create(
                            fecha=fecha,
                            hora=hora,
                            actividad=actividad,
                        )
                        horarios_creados += creado
            fecha += timedelta(days=1)

        self.stdout.write(f"Horarios de muestra creados: {horarios_creados}")
