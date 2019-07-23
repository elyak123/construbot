import copy
from django.views.generic.base import ContextMixin
from django import urls
from .menu import main_menu
from django.conf import settings


class ContextManager(ContextMixin):
    """This context manager allows us to get basic information about the
    the page being rendered to the template"""
    menu = main_menu

    menu_specific = []

    def get_menu(self):
        context_menu = copy.deepcopy(self.menu)
        menu_2 = copy.deepcopy(self.menu_specific)
        menu_2.reverse()
        shallow_menu = []
        for count, single_menu in enumerate(context_menu):
            if single_menu['title'].lower() in self.user_groups:
                shallow_menu.insert(count + 1, single_menu)

        if len(menu_2) > 0 and self.nivel_permiso_usuario >= 2:
            another_copy = copy.deepcopy(self.menu)
            for counter, element in enumerate(another_copy):
                if self.app_label_name.lower() == element['title'].lower():
                    for number, el in enumerate(menu_2, 1):
                        shallow_menu.insert(counter + 1, el)
        return self.get_reverse_menu_urls(shallow_menu)

    def get_reverse_menu_urls(self, cxt_menu):
        # TODO: No se puede hacer test de este método hasta que tenga
        #       las urls definitivas "registradas" para el menú
        for element in cxt_menu:
            if element.get('url'):
                element['url'] = urls.reverse(element['url'], kwargs=element.get('urlkwargs'))
            if element.get('submenu'):
                for subelement in element['submenu']:
                    if subelement.get('url'):
                        subelement['url'] = urls.reverse(subelement['url'], kwargs=subelement.get('urlkwargs'))
        return cxt_menu

    def get_context_data(self, **kwargs):
        context = super(ContextManager, self).get_context_data(**kwargs)
        context['is_new_user'] = self.request.user.is_new
        context['menu'] = self.get_menu()
        context['allow_register'] = settings.ACCOUNT_ALLOW_REGISTRATION
        context['favicon'] = settings.FAVICON_URL
        context['app_label_name'] = self.app_label_name.lower()
        return context
