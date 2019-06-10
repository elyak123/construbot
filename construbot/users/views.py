import importlib
from django.conf import settings
from django import http
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
<<<<<<< HEAD
from django.core.urlresolvers import reverse
=======
from django.urls import reverse
>>>>>>> 432b8adc6f2247b6794c8149615a4b25fef180f5
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View, DetailView, ListView, RedirectView, UpdateView, CreateView, TemplateView, DeleteView
from django.http import JsonResponse
from .auth import AuthenticationTestMixin
from .apps import UsersConfig
from .models import Company
from .forms import UsuarioInterno, UsuarioEdit, UsuarioEditNoAdmin, CompanyForm, CompanyEditForm

try:
    Authclass = importlib.import_module(settings.CONSTRUBOT_AUTHORIZATION_CLASS)
except ImportError:
    from construbot.users import auth as Authclass

User = get_user_model()


class UsersMenuMixin(Authclass.AuthenticationTestMixin):
    change_company_ability = False
    app_label_name = UsersConfig.verbose_name
    permiso_requerido = 3
    menu_specific = [
        {
            'title': 'Usuarios',
            'url': 'users:list',
            'always_appear': False,
            'icon': 'person',
            'parent': False,
            'type': 'submenu',
            'submenu': [],
        }, {
            'title': 'Empresas',
            'url': 'users:company_list',
            'always_appear': False,
            'icon': 'briefcase',
            'parent': False,
            'type': 'submenu',
            'submenu': [],
        }
    ]

    def get_company_query(self, opcion):
        company_query = {
            'User': {
                'company': self.request.user.currently_at
            },
            'Company': {
                'customer': self.request.user.customer
            }
        }
        return company_query[opcion]


class UserMixin(UsersMenuMixin):

    def check_obj_permissions(self, obj):
        if self.request.user.customer != obj.customer and self.request.user.nivel_acceso.nivel < 5:
            raise PermissionDenied('El usuario no tiene acceso a permisos fuera de su cuenta.')

    def get_nivel_permiso(self):
        if (self.kwargs.get('username') == self.request.user.username) or self.kwargs.get('username') is None:
            return self.nivel_permiso_usuario
        else:
            return self.permiso_requerido

    def get_object(self, queryset=None):
        if not self.kwargs.get('username', None):
            return self.request.user
        return User.objects.select_related('customer').get(username=self.kwargs['username'])


class UserDetailView(UserMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    app_label_name = 'redirect'  # dar acceso independientemente de sus grupos
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.check_obj_permissions(self.object)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class UserRedirectView(UsersMenuMixin, RedirectView):
    tengo_que_ser_admin = False
    permanent = False
    app_label_name = 'redirect'
    permiso_requerido = 1

    def get_redirect_url(self):
        return reverse('proyectos:proyect_dashboard')


class RemoveIsNewUserStatus(View):
    def post(self, request, *args, **kwargs):
        obj = User.objects.get(pk=self.kwargs['pk'])
        obj.is_new = False
        obj.save()
        return JsonResponse({'exito': True})


class UserUpdateView(UserMixin, UpdateView):
    app_label_name = 'redirect'  # dar acceso independientemente de sus grupos
    template_name = 'users/user_form.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.check_obj_permissions(self.object)
        return super(UserUpdateView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserUpdateView, self).get_form_kwargs()
        if self.nivel_permiso_usuario >= self.permiso_requerido:
<<<<<<< HEAD
            try:
                kwargs['user'] = User.objects.get(username=self.kwargs.get('username'))
            except User.DoesNotExist:
                kwargs['user'] = self.request.user
=======
            if self.kwargs.get('username', None) and self.kwargs.get('username') != self.request.user.username:
                kwargs['user'] = self.object
>>>>>>> 432b8adc6f2247b6794c8149615a4b25fef180f5
        return kwargs

    def get_form_class(self, form_class=None):
        if self.nivel_permiso_usuario >= self.permiso_requerido:
<<<<<<< HEAD
            return UsuarioEdit
        else:
            return UsuarioEditNoAdmin
=======
            if self.kwargs.get('username', None) and self.kwargs.get('username') != self.request.user.username:
                return UsuarioEdit
        return UsuarioEditNoAdmin
>>>>>>> 432b8adc6f2247b6794c8149615a4b25fef180f5

    def get_success_url(self):
        return reverse('users:detail', kwargs={'username': self.object.username})


class UserCreateView(UsersMenuMixin, CreateView):
    form_class = UsuarioInterno
    app_label_name = UsersConfig.verbose_name
    template_name = 'users/create_user.html'

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        if self.request.user.currently_at not in self.object.company.all():
            pass
        return reverse('users:detail', kwargs={'username': self.object.username})

    def get_initial(self):
        initial = super(UserCreateView, self).get_initial()
        initial['customer'] = self.request.user.customer
        return initial


class CompanyCreateView(UsersMenuMixin, CreateView):
    form_class = CompanyForm
    app_label_name = UsersConfig.verbose_name
    template_name = 'proyectos/creation_form.html'

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('users:company_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super(CompanyCreateView, self).get_initial()
        initial['customer'] = self.request.user.customer
        return initial


class CompanyEditView(UsersMenuMixin, UpdateView):
    form_class = CompanyEditForm
    template_name = 'proyectos/company_edit_form.html'

    def get_initial(self):
        initial = super(CompanyEditView, self).get_initial()
        initial['is_new'] = self.request.user.is_new
        return initial

    def get_success_url(self):
        return reverse('users:company_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        return get_object_or_404(Company, pk=self.kwargs['pk'], user=self.request.user)


class UserDeleteView(UsersMenuMixin, DeleteView):
    template_name = 'core/delete.html'
    model_options = {
        'User': User,
        'Company': Company
    }

    def get_object(self):
        obj = get_object_or_404(
            self.model_options[self.kwargs['model']],
            **self.get_company_query(self.kwargs['model']),
            pk=self.kwargs['pk']
        )
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return http.HttpResponse()


class UserListView(UsersMenuMixin, ListView):
    template_name = 'users/user_list.html'
    change_company_ability = True
    app_label_name = UsersConfig.verbose_name
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        qs = self.model.objects.filter(company=self.request.user.currently_at).exclude(id=self.request.user.id)
        return qs


class CompanyChangeView(AuthenticationTestMixin, TemplateView):
    app_label_name = 'redirect'

    def get(self, request, *args, **kwargs):
        new_company = get_object_or_404(
            Company,
            company_name=self.kwargs['company'],
            customer=self.request.user.customer
        )
        if new_company in self.request.user.company.all():
            self.request.user.currently_at = new_company
            self.request.user.save()
            return http.HttpResponse(self.request.user.currently_at.company_name)
        else:
            raise PermissionDenied(
                f'El usuario {self.request.user.username} no tiene acceso a {new_company.company_name}'
            )


class CompanyChangeViewFromList(CompanyChangeView):

    def get(self, request, *args, **kwargs):
        new_company = get_object_or_404(
            Company,
            pk=self.kwargs['pk'],
            customer=self.request.user.customer
        )
        if new_company in self.request.user.company.all():
            self.request.user.currently_at = new_company
            self.request.user.save()
            return redirect('proyectos:proyect_dashboard')
        else:
            raise PermissionDenied(
                f'El usuario {self.request.user.username} no tiene acceso a {new_company.company_name}'
            )


class CompanyListView(UsersMenuMixin, ListView):
    paginate_by = 10
    model = Company
    ordering = '-company_name'

    def get_queryset(self):
        self.queryset = self.request.user.company
        return super(CompanyListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(CompanyListView, self).get_context_data(**kwargs)
        context['model'] = self.model.__name__
        return context


class PasswordRedirectView(UsersMenuMixin, RedirectView):
    permanent = True
    app_label_name = 'redirect'
    permiso_requerido = 1

    def get_redirect_url(self):
        return reverse('account_change_password')
