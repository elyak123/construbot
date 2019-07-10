from django.db.models import Sum, F
from construbot.core.utils import Round
from .models import Contrato, Estimate


def contratosvigentes(user):
    if user.nivel_acceso.nivel >= 3:
        contratos = Contrato.objects.select_related('cliente').filter(
            status=True, cliente__company=user.currently_at).annotate(total_estimado=Round(Sum(
                F('estimate__estimateconcept__cuantity_estimated') *
                F('estimate__estimateconcept__concept__unit_price')
            ) / F('monto') * 100
            )).order_by('-monto')
    elif user.nivel_acceso.nivel == 2:
        contratos = Contrato.objects.select_related('cliente').filter(
            status=True, cliente__company=user.currently_at, users=user).annotate(total_estimado=Round(Sum(
                F('estimate__estimateconcept__cuantity_estimated') *
                F('estimate__estimateconcept__concept__unit_price')
            ) / F('monto') * 100
            )).order_by('-monto')
    else:
        contratos = Contrato.objects.select_related('cliente').filter(
            status=True, cliente__company=user.currently_at, users=user
            ).order_by('-folio')
    return contratos


def sumatoria_query(queryset, campo):
    return queryset.aggregate(total=Sum(campo))


def estimacionespendientes_facturacion(company, almenos_coordinador, user):
    kw = {'project__cliente__company': company, 'invoiced': False}
    if not almenos_coordinador:
        kw['project__users'] = user
    return Estimate.objects.select_related('project').filter(**kw)


def estimacionespendientes_pago(company, almenos_coordinador, user):
    kw = {'project__cliente__company': company, 'invoiced': True, 'paid': False}
    if not almenos_coordinador:
        kw['project__users'] = user
    return Estimate.objects.select_related('project').filter(**kw)


def total_sinpago(estimaciones):
    return estimaciones.aggregate(total=Round(Sum(F('estimateconcept__cuantity_estimated') * F('concept__unit_price'))))['total']


def totalsinfacturar(estimaciones):
    return estimaciones.aggregate(
        total=Round(Sum(F('estimateconcept__cuantity_estimated') * F('concept__unit_price')))
    )['total']
