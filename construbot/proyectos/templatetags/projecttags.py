import datetime
from django import template

register = template.Library()

@register.simple_tag
def get_amortizacion_de_anticipo(porcentaje, monto_total):
    return monto_total * (porcentaje / 100)

@register.simple_tag
def get_subtotal(porcentaje, monto_total):
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
