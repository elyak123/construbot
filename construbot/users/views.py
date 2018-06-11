from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView, TemplateView, DeleteView
from .auth import AuthenticationTestMixin
from django.shortcuts import get_object_or_404
from django import http
from .apps import UsersConfig
from .models import User, Company
from .forms import UsuarioInterno


class UsersMenuMixin(AuthenticationTestMixin):
    app_label_name = UsersConfig.verbose_name
    tengo_que_ser_admin = True
    menu_specific = [
        {
            'title': 'Listado',
            'url': 'users:list',
            'icon': 'list',
            'parent': True,
            'type': 'submenu',
            'submenu': '',
        }, {
            'title': 'Crear',
            'url': 'users:new',
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
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(UsersMenuMixin, UpdateView):
    fields = ['username', 'first_name', 'last_name', 'email']

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',)

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


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
