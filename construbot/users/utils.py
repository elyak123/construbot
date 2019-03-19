from django.db.utils import IntegrityError
from django.conf import settings
from .models import NivelAcceso


def establish_access_levels():
    for nivel in settings.NIVELES_ACCESO:
        try:
            nivel_acceso, created = NivelAcceso.objects.get_or_create(**nivel)
        except IntegrityError:
            NivelAcceso.objects.get(**nivel)  # garantizar que realmente exista.
