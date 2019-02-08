from django import template
from django.db.models import Sum


register = template.Library()


@register.filter(name='totalvigentes')
def totalvigentes(contratos):
    # Asumimos que si se ejecuta este filtro, se tiene permiso
    total_vigentes = contratos.aggregate(total_contato=Sum('monto'))
    return total_vigentes['total_contato']
