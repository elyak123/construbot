import datetime
from django import template
from decimal import Decimal

register = template.Library()

@register.simple_tag
def get_amortizacion_de_anticipo(porcentaje, estimate_amount):
    if porcentaje is not None:
        return estimate_amount['total'] * (porcentaje / 100)
    else:
        return Decimal(0)

@register.simple_tag
def get_subtotal(porcentaje, monto_total):
    if not porcentaje:
        porcentaje = Decimal(0)
    if not monto_total:
        monto_total = Decimal(0)
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
