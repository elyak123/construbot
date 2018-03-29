from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView
from .auth import AuthenticationTestMixin
from .apps import UsersConfig
from .models import User
from .forms import UsuarioInterno


class UserDetailView(AuthenticationTestMixin, DetailView):
    app_label_name = UsersConfig.verbose_name
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        if self.kwargs.get('username'):
            return User.objects.get(username=self.kwargs['username'])
        else:
            return self.request.user


class UserRedirectView(AuthenticationTestMixin, RedirectView):
    app_label_name = UsersConfig.verbose_name
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(AuthenticationTestMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserCreateView(AuthenticationTestMixin, CreateView):
    form_class = UsuarioInterno
    app_label_name = UsersConfig.verbose_name
    template_name = 'users/create_user.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse('users:detail', kwargs={'username': self.object.username})

    def get_initial(self):
        initial = super(UserCreateView, self).get_initial()
        initial['customer'] = self.request.user.customer
        return initial

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(UserCreateView, self).get_context_data(**kwargs)

class UserListView(AuthenticationTestMixin, ListView):
    app_label_name = UsersConfig.verbose_name
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return self.model.objects.filter(company=self.request.user.currently_at)
