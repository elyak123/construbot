from django.db.models import Func
from time import strftime


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'


def get_directory_path(instance, filename):
    date_str = strftime('%Y-%m-%d-%S')
    instance_model = instance._meta.verbose_name_plural
    instance_consumer = instance.cliente.company.customer.customer_name
    instance_company = instance.cliente.company.company_name

    return '{0}/{1}/{2}/{3}-{4}'.format(instance_consumer, instance_company, instance_model, date_str, filename)
