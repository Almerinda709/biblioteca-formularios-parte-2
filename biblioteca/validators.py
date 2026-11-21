
from django.core.exceptions import ValidationError
from django.utils import timezone


def validar_ano_publicacao(ano):
    ano_atual = timezone.localdate().year

    if ano < 1450 or ano > ano_atual:
        raise ValidationError(
            f"O ano deve estar entre 1450 e {ano_atual}."
        )
