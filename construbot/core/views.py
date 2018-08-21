from django.conf import settings


class NewUserMixin(object):

    def check_for_uuid(self):
        if settings.UUID in self.request.user.username or settings.UUID in self.request.user.currently_at.company_name:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(NewUserMixin, self).get_context_data(**kwargs)
        context['is_new_user'] = self.check_for_uuid()
        return context
