from django.conf import settings
from django.views.generic import View


class NewUserMixin(View):

    def check_for_uuid(self):
        if settings.UUID:
            return settings.UUID in self.request.user.username or settings.UUID in self.request.user.currently_at.company_name
        else:
            return False
