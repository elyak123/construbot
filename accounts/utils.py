from accounts.models            import ExtendUser
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions     import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
# Para ContextManager
from django.views.generic.base import ContextMixin
from django.urls               import reverse
import copy

class ContextManager(ContextMixin):
    """This context manager allows us to get basic information about the
    the page being rendered to the template"""
    menu = [
        {
            'title'    : 'Home',
            'url'      : 'home:index',
            'urlkwargs': None,
            'icon'     : 'glyphicon glyphicon-home',
            'parent'   : False,
            'child'    : False,
        },
        {
            'title'    : 'Documentos',
            'url'      : 'oficios:Start',
            'urlkwargs': '',
            'icon'     : 'glyphicon glyphicon-folder-open',
            'parent'   : False,
            'child'    : False,
        },
        {
            'title'    : 'Pendientes',
            'url'      : 'pendientes:Tasklist',
            'urlkwargs': '',
            'icon'     : 'glyphicon glyphicon-check',
            'parent'   : False,
            'child'    : False,
            'group'    : 'Pendientes'
        },
        {
            'title'    : 'Proyectos',
            'url'      : 'pmgt:pmgt_dashboard',
            'urlkwargs': '',
            'icon'     : 'glyphicon glyphicon-road',
            'parent'   : False,
            'child'    : False,
        },

    ]

    menu_specific = []

    def get_title(self):
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
                shallow_menu.insert(count + 1 , single_menu)

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
            'title'       : self.get_title(),
            'description' : self.description
        }
        context['home'] = home_dict
        context['menu'] = self.get_menu()
        context['app_label_name'] = self.app_label_name.lower()
        return context

class AuthenticationTestMixin(UserPassesTestMixin, ContextManager):
    
    login_url = 'login'
    tengo_que_ser_admin = False

    def test_func(self):
        try:
            self.current_user = ExtendUser.objects.select_related('user', 'currently_at').prefetch_related('company').get(pk=self.request.user.profile.id)
        except (ObjectDoesNotExist, AttributeError) as e:
            return False

        if self.current_user.company.exists():
            if not self.current_user.currently_at:
                self.current_user.currently_at = self.current_user.company.first()
                self.current_user.save()
        else:
            raise AttributeError('Current User must have company')

        self.user_groups = [x.name.lower() for x in self.current_user.user.groups.all()]
        try:
            self.user_pass = self.current_user.user.is_authenticated()
        except TypeError:
            self.user_pass = self.current_user.user.is_authenticated
        self.permiso_administracion = self.auth_admin()
        self.debo_ser_admin = self.get_tengo_que_ser_admin()

        if self.user_pass:
            if self.debo_ser_admin and not self.permiso_administracion:
                raise PermissionDenied
            elif self.app_label_name.lower() in self.user_groups:
                return True
            else:
                raise PermissionDenied
        else:
            return False

    def auth_admin(self):
        return self.current_user.is_administrator()

    def get_context_data(self, **kwargs):
        context = super(AuthenticationTestMixin, self).get_context_data(**kwargs)
        context['current_user'] = self.current_user
        context['user_pass'] = self.user_pass
        context['is_administrador'] = self.permiso_administracion
        return context

    def get_tengo_que_ser_admin(self):
        return self.tengo_que_ser_admin