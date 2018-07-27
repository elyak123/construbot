from django.core.urlresolvers import reverse
from django.db.models.functions import Lower
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView, TemplateView, DeleteView
from .auth import AuthenticationTestMixin
from django.shortcuts import get_object_or_404
from django import http
from .apps import UsersConfig
from .models import User, Company
from .forms import UsuarioInterno, UsuarioEdit, UsuarioEditNoAdmin, CompanyForm


class UsersMenuMixin(AuthenticationTestMixin):
    app_label_name = UsersConfig.verbose_name
    tengo_que_ser_admin = True
    menu_specific = [
        {
            'title': 'Listados',
            'url': '',
            'always_appear': False,
            'icon': 'list',
            'parent': True,
            'type': 'submenu',
            'submenu': [
                {
                    'title': 'Usuarios',
                    'url': 'users:list',
                    'always_appear': False,
                    'urlkwargs': '',
                    'icon': 'bookmark',
                },
                {
                    'title': 'Compañías',
                    'url': 'users:company_list',
                    'always_appear': False,
                    'urlkwargs': '',
                    'icon': 'person',
                },
            ],
        }, {
            'title': 'Crear',
            'url': 'users:new',
            'always_appear': False,
            'icon': 'star',
            'parent': True,
            'type': 'submenu',
            'submenu': '',
        }
    ]


class UserDetailView(UsersMenuMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'
    tengo_que_ser_admin = False

    def get_object(self, queryset=None):
        if not self.kwargs['username']:
            self.kwargs['username'] = self.request.user.username
        return get_object_or_404(User, username=self.kwargs['username'], company=self.request.user.currently_at)

    def get_tengo_que_ser_admin(self):
        if self.kwargs['username'] == self.request.user.username:
            return False
        else:
            return True


class UserRedirectView(UsersMenuMixin, RedirectView):
    tengo_que_ser_admin = False
    permanent = False

    def get_redirect_url(self):
        return reverse('proyectos:proyect_dashboard')


class UserUpdateView(UsersMenuMixin, UpdateView):
    tengo_que_ser_admin = False

    def get_form_class(self, form_class=None):
        if self.permiso_administracion:
            return UsuarioEdit
        else:
            return UsuarioEditNoAdmin

    def get_success_url(self):
        return reverse('users:detail', kwargs={'username': self.object.username})

    def get_object(self):
        return self.request.user


class UserCreateView(UsersMenuMixin, CreateView):
    form_class = UsuarioInterno
    app_label_name = UsersConfig.verbose_name
    template_name = 'users/create_user.html'

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('users:detail', kwargs={'username': self.object.username})

    def get_initial(self):
        initial = super(UserCreateView, self).get_initial()
        initial['customer'] = self.request.user.customer
        return initial

class CompanyCreateView(UsersMenuMixin, CreateView):
    form_class = CompanyForm
    app_label_name = UsersConfig.verbose_name
    template_name = 'proyectos/creation_form.html'

    def get_success_url(self):
        return reverse('users:company_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super(CompanyCreateView, self).get_initial()
        initial['customer'] = self.request.user.customer
        return initial


class UserDeleteView(UsersMenuMixin, DeleteView):
    template_name = 'core/delete.html'

    def get_object(self):
        obj = get_object_or_404(
            User,
            company=self.request.user.currently_at,
            pk=self.kwargs['pk']
        )
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return http.HttpResponse()


class UserListView(UsersMenuMixin, ListView):
    app_label_name = UsersConfig.verbose_name
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        qs = self.model.objects.filter(company=self.request.user.currently_at).exclude(id=self.request.user.id)
        return qs


class CompanyChangeView(TemplateView, AuthenticationTestMixin):
    app_label_name = UsersConfig.verbose_name

    def get(self, request, *args, **kwargs):
        new_company = get_object_or_404(Company, company_name=self.kwargs['company'])
        if new_company in self.request.user.company.all():
            self.request.user.currently_at = new_company
            self.request.user.save()
            return http.HttpResponse(self.request.user.currently_at.company_name)

class CompanyListView(UsersMenuMixin, ListView):
    paginate_by = 10
    model = Company
    ordering = '-company_name'

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = self.model.objects.filter(
                customer=self.request.user.customer).order_by(
                Lower('company_name')
            )
        return super(CompanyListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(CompanyListView, self).get_context_data(**kwargs)
        context['model'] = self.model.__name__
        return context


class CompanyDetailView(UsersMenuMixin, DetailView):
    model = Company

    def get_context_object_name(self, obj):
        return obj.__class__.__name__.lower()

    def get_object(self, queryset=None):
        return get_object_or_404(
            self.model, pk=self.kwargs['pk']
        )
