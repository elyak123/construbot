from django.views.generic  import TemplateView, View, CreateView, UpdateView, ListView, DetailView
from django.views.generic.base import View
from django.core.exceptions    import ImproperlyConfigured
from django                    import http
from django.urls               import reverse, reverse_lazy
from django.shortcuts          import get_object_or_404
from accounts.models           import Company
# from pmgt.models               import Estimate
from accounts.utils            import AuthenticationTestMixin
from .                         import forms

class Index(TemplateView, AuthenticationTestMixin):
    """View to render the home page"""
    title          = 'Bienvenidos al Sistema de Administracion de INSECAMI'
    description    = 'Hola, esta es una descripción'
    template_name  = 'home/dashboard.html'
    app_label_name = 'Home'

    # menu = [
    #     {
    #         'title'    : 'Documentacion',
    #         'url'      : 'oficios:Start',
    #         'urlkwargs': None,
    #         'icon'     : 'glyphicon glyphicon-home',
    #         'parent'   : False
    #     },
    #     {
    #         'title'    : 'Actividades',
    #         'url'      : 'pendientes:Tasklist',
    #         'urlkwargs': None,
    #         'icon'     : 'glyphicon glyphicon-ok',
    #         'parent'   : False
    #     },
    #     {
    #         'title'    : 'Estimaciones',
    #         'url'      : 'pmgt:BaseTemplateView',
    #         'urlkwargs': None,
    #         'icon'     : 'glyphicon glyphicon-list-alt',
    #         'parent'   : False
    #     }
    # ]

    def __init__(self, **kwargs):
        super(Index, self).__init__(**kwargs)

class CompanyChange(Index):

    def get(self, request, *args, **kwargs):
        new_company = get_object_or_404(Company, company_name=self.kwargs['company'])
        if new_company in self.current_user.company.all():
            self.current_user.currently_at = new_company
            self.current_user.save()
            return http.HttpResponse(self.current_user.currently_at.company_name)

class BaseEditMixin(AuthenticationTestMixin):
    """docstring for BaseEditMixin"""
    operation     = None
    title = None

    def __str__(self):
        return self.model._meta.verbose_name_plural
    
    def get_title(self):
        if self.operation is None:
            raise ImproperlyConfigured('High-Level: self.operation cannot be "None"')
        elif not self.title:
            self.form_class = self.get_form_class()
            if self.model is None and self.form_class:
                try:
                    return '{} de {}'.format(
                        self.operation, self.form_class._meta.model._meta.verbose_name_plural
                    )
                except:
                    return '{} de {}'.format(
                        self.operation, self.form_class.model._meta.verbose_name_plural
                    )
            return '{} de {}'.format(
                self.operation, self.model._meta.verbose_name_plural
            )
        else:
            return self.title

    def get_form_class(self):
        if not self.form_class:
            self.form_class = self.model_form_options[self.kwargs['modelform']]['form']
        return super(BaseEditMixin, self).get_form_class()

    def get_success_url(self):
        if self.success_url:
            url = reverse_lazy(self.success_url, kwargs=self.kwargs
                )
            return url

    def get_context_data(self, **kwargs):
        context = super(BaseEditMixin, self).get_context_data(**kwargs)
        if self.kwargs.get('modelform'):
            context['form_param'] = self.form_class._meta.model._meta.verbose_name_plural.lower()
        context['operation']  = self.operation
        return context

class CreationMixin(BaseEditMixin, CreateView):
    operation = 'Create'

class UpdateMixin(BaseEditMixin, UpdateView):
    operation = 'Update'

    def get_queryset(self):
        if not self.queryset and self.kwargs.get('modelform'):
            try:
                self.form_class = self.model_form_options.get(self.kwargs.get('modelform')).get('form') or self.get_form_class()
                self.queryset   = self.form_class._meta.model._default_manager
            except:
                self.form_class = self.get_form_class()
                self.queryset   = self.form_class['model']._default_manager
        return self.queryset

    def get_context_data(self, **kwargs):
        context       = super(UpdateMixin, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        return context

class BaseListMixin(AuthenticationTestMixin, ListView):
    """BaseMixin for Displaying the List Of Documents"""

    def __str__(self):
        return self.model._meta.verbose_name_plural
    
    def get_title(self):
        if hasattr(self, 'title'):
            return self.title
        else:
            return 'Listado de {}'.format(self.model._meta.verbose_name_plural)

    def get_queryset(self):
        if not self.model and self.queryset is None:
            self.model = self.model_form_options[self.kwargs['modelform']]['model']
        return super(BaseListMixin, self).get_queryset()

# class GenericEstimateDetailView(AuthenticationTestMixin, DetailView):
#     def get_queryset(self):
#         self.model = self.model_form_options[self.kwargs['modelform']]['model']
#         return super(GenericEstimateDetailView, self).get_queryset()
