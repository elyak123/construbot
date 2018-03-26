import copy
from django.views.generic.base import ContextMixin
from django.urls import reverse
from .menu import main_menu


class ContextManager(ContextMixin):
    """This context manager allows us to get basic information about the
    the page being rendered to the template"""
    menu = main_menu

    menu_specific = []

    def get_title(self):
        # TODO: Los titulos deben provenir de los
        #       templates...
        if not self.title:
            return self.__str__()
        return self.title

    def get_menu(self, extra_menu=None):
        context_menu = copy.deepcopy(self.menu)
        menu_2 = copy.deepcopy(self.menu_specific)
        menu_2.reverse()
        if len(self.user_groups) == 0:
            context_menu = []
        shallow_menu = []
        for count, single_menu in enumerate(context_menu):
            if single_menu['title'].lower() in self.user_groups:
                shallow_menu.insert(count + 1, single_menu)

        if len(menu_2) > 0:
            another_copy = copy.deepcopy(self.menu)
            for counter, element in enumerate(another_copy):
                if self.app_label_name.lower() == element['title'].lower():
                    for number, el in enumerate(menu_2, 1):
                        shallow_menu.insert(counter + 1, el)
        if extra_menu:
            shallow_menu.append(extra_menu)
        return self.get_reverse_menu_urls(shallow_menu)

    def get_reverse_menu_urls(self, cxt_menu):
        for element in cxt_menu:
            if element.get('url'):
                element['url'] = reverse(element['url'], kwargs=element.get('urlkwargs'))
            if element.get('submenu'):
                for subelement in element['submenu']:
                    if subelement.get('url'):
                        subelement['url'] = reverse(subelement['url'], kwargs=subelement.get('urlkwargs'))
        return cxt_menu

    def get_admin_menu(self):
        pass

    def get_context_data(self, **kwargs):
        context = super(ContextManager, self).get_context_data(**kwargs)
        home_dict = {
            'title': self.get_title(),
            'description': self.description
        }
        context['home'] = home_dict
        context['menu'] = self.get_menu()
        context['app_label_name'] = self.app_label_name.lower()
        return context
