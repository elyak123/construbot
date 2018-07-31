from django.db.models import Sum, F
from construbot.core.utils import Round
from .models import Contrato



def contratosvigentes(user, permiso):
    if permiso:
        contratos = Contrato.objects.select_related('cliente').filter(
            status=True, cliente__company=user.currently_at).annotate(total_estimado=Round(Sum(
                F('estimate__estimateconcept__cuantity_estimated') *
                F('estimate__estimateconcept__concept__unit_price')
            ) / F('monto') * 100
            )).order_by('-monto')
    else:
        contratos = Contrato.objects.select_related('cliente').filter(
            status=True, cliente__company=user.currently_at, users=user
            ).order_by('-folio')
    return contratos
