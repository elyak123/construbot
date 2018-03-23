from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from .auth import AuthenticationTestMixin
from .apps import UsersConfig
from .models import User


class UserDetailView(AuthenticationTestMixin, DetailView):
    app_label_name = UsersConfig.verbose_name
    # TODO: quitar estas variables y manejar esto desde
    # los templates
    title = ''
    description = ''
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


class UserListView(AuthenticationTestMixin, ListView):
    app_label_name = UsersConfig.verbose_name
    # TODO: quitar estas variables y manejar esto desde
    # los templates
    title = ''
    description = ''

    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return self.model.objects.filter(company=self.current_user.currently_at)
