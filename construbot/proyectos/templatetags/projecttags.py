import decimal
from django import template
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.simple_tag
def get_amortizacion_de_anticipo(porcentaje, estimate_amount):
    if porcentaje is not None:
        return estimate_amount['total'] * (porcentaje / 100)
    else:
        return decimal.Decimal(0)


@register.simple_tag
def get_subtotal(porcentaje, monto_total):
    if not porcentaje:
        porcentaje = decimal.Decimal(0)
    if not monto_total:
        monto_total = decimal.Decimal(0)
    return monto_total - (monto_total * (porcentaje / 100))


@register.simple_tag
def get_total_retenciones(retenciones, porcentaje, monto_total):
    total_retenciones = 0
    subtotal = get_subtotal(porcentaje, monto_total)
    for ret in retenciones:
        if ret.tipo == 'AMOUNT':
            aux = ret.valor
        else:
            aux = subtotal * (ret.valor/100)
        total_retenciones = total_retenciones+aux
    return total_retenciones


@register.simple_tag
def get_total_final(retenciones, porcentaje, monto_total):
    subtotal = get_subtotal(porcentaje, monto_total)
    total_retenciones = get_total_retenciones(retenciones, porcentaje, monto_total)
    return subtotal - total_retenciones


@register.filter(is_safe=True)
def intxls(value, use_l10n=True):
    try:
        val = decimal.Decimal(value)
        if val == 0 or val is None:
            return '-'
    except (TypeError, decimal.InvalidOperation):
        pass
    return intcomma(value)


@register.filter(is_safe=True)
def moneda(value, use_l10n=True):
    val = intxls(value)
    if val == '-':
        return val
    return '$ ' + val
