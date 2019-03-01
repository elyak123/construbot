from time import strftime
from django import shortcuts
from django.core.exceptions import PermissionDenied
from django.db.models import Func
from dal import autocomplete
from construbot.users.auth import AuthenticationTestMixin


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'


def get_directory_path(instance, filename):
    date_str = strftime('%Y-%m-%d-%H-%M-%S')
    instance_model = instance._meta.verbose_name_plural
    instance_customer = instance.cliente.company.customer
    instance_company = instance.cliente.company.company_name

    return '{0}-{1}/{2}/{3}/{4}-{5}'.format(
        instance_customer.id, instance_customer.customer_name, instance_company, instance_model, date_str, filename
    )


def get_image_directory_path(instance, filename):
    date_str = strftime('%Y-%m-%d-%H-%M-%S')
    instance_model = instance._meta.verbose_name_plural
    instance_customer = instance.estimateconcept.concept.project.cliente.company.customer
    instance_company = instance.estimateconcept.concept.project.cliente.company.company_name

    return '{0}-{1}/{2}/{3}/{4}-{5}'.format(
        instance_customer.id, instance_customer.customer_name, instance_company, instance_model, date_str, filename
    )


def get_object_403_or_404(model, user, **kwargs):
    try:
        obj = shortcuts.get_object_or_404(model, **kwargs)
    except model.DoesNotExist as e:
        if any([n[-7:] == 'company' for n in kwargs.keys()]):
            kwargs = get_rid_of_company_kw(kwargs)
            try:
                obj = model.objects.filter(**kwargs)
                raise PermissionDenied
                # return object_or_403(user, obj)
            except model.DoesNotExist as e:
                raise e
        raise e
    return obj


def object_or_403(user, obj):
    if obj.company in user.company.all():
        user.currently_at = obj.company
        return obj
    else:
        raise PermissionDenied


def get_rid_of_company_kw(kwargs):
    kw = [n for n in kwargs.keys() if n[-7:] == 'company']
    del kwargs[kw[0]]
    return kwargs


class BasicAutocomplete(AuthenticationTestMixin, autocomplete.Select2QuerySetView):
    app_label_name = ''
    title = ''
    description = ''
    ordering = ''

    def has_add_permission(self, request):
        return True

    def get_key_words(self):
        raise NotImplementedError(
            'Es necesario sobreescribir el metodo get_key_words'
            'para realizar el query.'
        )

    def get_queryset(self):
        if self.request.user and self.q:
            qs = self.model.objects.filter(**self.get_key_words()).order_by(self.ordering)
            return qs
        elif self.request.user and self.request.POST:
            return self.model.objects

    def get_post_key_words(self):
        return {}

    def create_object(self, text):
        """Create an object given a text."""
        self.post_key_words = {self.create_field: text}
        self.post_key_words.update(self.get_post_key_words())
        return self.get_queryset().create(**self.post_key_words)
