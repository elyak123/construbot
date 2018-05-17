from django import template
from django.db.models import F, Sum
from construbot.core.utils import Round
from construbot.proyectos import models


register = template.Library()


@register.filter(name='contratosvigentes')
def contratosvigentes(empresa):
    contratos = models.Contrato.objects.select_related('cliente').filter(
            status=True, cliente__company=empresa).annotate(total_estimado=Round(Sum(
                F('estimate__estimateconcept__cuantity_estimated') *
                F('estimate__estimateconcept__concept__unit_price')
            ) / F('monto') * 100
            )).order_by('-monto')
    return contratos


@register.filter(name='totalvigentes')
def totalvigentes(empresa):
    total_vigentes = contratosvigentes(empresa).aggregate(total_contato=Sum('monto'))
    return total_vigentes


@register.filter(name='estimacionespendientes')
def estimacionespendientes(empresa):
    estimaciones = models.Estimate.objects.select_related('project').filter(
            project__cliente__company=empresa, invoiced=False)
    return estimaciones


@register.filter(name='totalsinfacturar')
def totalsinfacturar(empresa):
    total_sin_facturar = estimacionespendeintes(empresa).aggregate(
            total=Round(Sum(
                F('estimateconcept__cuantity_estimated') * F('concept__unit_price')
            )))
    return total_sin_facturar


@register.filter(name='estimacionesfacturadas')
def estimacionesfacturadas(empresa):
    estimaciones_facturadas = models.Estimate.objects.filter(
            project__cliente__company=empresa, invoiced=True, paid=False
    )
    return estimaciones_facturadas


@register.filter(name='totalsinpago')
def totalsinpago(empresa):
    total_sin_pago = estimacionesfacturadas(empresa).aggregate(
            total=Round(Sum(
                F('estimateconcept__cuantity_estimated') * F('concept__unit_price')
            )))
    return total_sin_pago
