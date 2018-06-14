from unittest import mock
from time import strftime
from django.db.models import Func, ImageField
from factory.fuzzy import BaseFuzzyAttribute
from dal import autocomplete
from users.auth import AuthenticationTestMixin


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'


def get_directory_path(instance, filename):
    date_str = strftime('%Y-%m-%d-%S')
    instance_model = instance._meta.verbose_name_plural
    instance_consumer = instance.cliente.company.customer.customer_name
    instance_company = instance.cliente.company.company_name

    return '{0}/{1}/{2}/{3}-{4}'.format(instance_consumer, instance_company, instance_model, date_str, filename)


class FuzzyImage(BaseFuzzyAttribute):

    def __init__(self, *args, **kwargs):
        super(FuzzyImage, self).__init__(*args, **kwargs)

    def fuzz(self):
        file = mock.Mock(spec=ImageField)
        file._committed = True
        return file


class BasicAutocomplete(AuthenticationTestMixin, autocomplete.Select2QuerySetView):
    app_label_name = ''
    title = ''
    description = ''
    key_words = {}
    post_key_words = {}
    ordering = ''

    def has_add_permission(self, request):
        return True

    def get_key_words(self):
        return self.key_words

    def get_queryset(self):
        if self.request.user and self.q:
            qs = self.model.objects.filter(**self.get_key_words()).order_by(self.ordering)
            return qs
        elif self.request.user and self.request.POST:
            return self.model.objects

    def get_post_key_words(self):
        return self.post_key_words

    def create_object(self, text):
        """Create an object given a text."""
        self.post_key_words = {self.create_field: text}
        self.post_key_words.update(self.get_post_key_words())
        return self.get_queryset().create(**self.post_key_words)