#from django.contrib.auth.forms import UserCreationForm
from .utils           	import ContextManager
from .temporalhelp              import CreationMixin, BaseListMixin, BaseEditMixin, UpdateMixin
# Los que "ya están"
from django.shortcuts           import render
from .models                    import ExtendUser
from django.views.generic       import UpdateView
from django.views.generic       import DetailView
from django.core.exceptions     import PermissionDenied
from django.contrib.auth        import views as auth_views
from .forms            			import UserForm, UserCreationForm, NoAdminUserForm
from django.forms               import inlineformset_factory, ValidationError
from .utils          			import AuthenticationTestMixin
from django.contrib.auth.models import Group
# from contratos.models                import Estimate
import copy

# Create your views here.

# class FormOptions(object):
#     model_form_options = {
#         'profile': {
#             'model': Profile,
#             'form': ProfileForm,
#         },
#     }

class ProfileDetail(object):
    """docstring for ProfileDetail"""
    
    def __init__(self, arg):
        super(ProfileDetail, self).__init__()
        self.arg = arg
        pass

class ProfileSettings(AuthenticationTestMixin, DetailView):
    title          = 'Configuración de perfil'
    description    = ''
    template_name  = 'home/detail_user.html'
    model          = ExtendUser
    app_label_name = 'home'

    def get_context_data(self, **kwargs):
        context = super(ProfileSettings, self).get_context_data(**kwargs)
        context['companies'] = ExtendUser.objects.get(id=self.kwargs['pk']).company.all()
        return context

    def get_queryset(self):
        if not self.kwargs['pk']:
            self.kwargs['pk'] = self.current_user.id

        if self.permiso_administracion or self.current_user.id == int(self.kwargs['pk']):
            self.model = ExtendUser
            return super(ProfileSettings, self).get_queryset()
        else:
            raise PermissionDenied

class NewUser(CreationMixin):
    tengo_que_ser_admin = True
    app_label_name   = 'Home'
    description      = 'Usuario nuevo'
    template_name    = 'home/newuser.html'
    success_url      = 'home:index'
    form_class       = UserCreationForm

    def get_context_data(self, **kwargs):
        context                 = super(NewUser, self).get_context_data(**kwargs)
        return context


    def post(self, request, *args, **kwargs):
        self.object = None
        form        = self.get_form()
        if form.is_valid():
        	form.save()
        	form._save_m2m()

class ProfileEdit(UpdateMixin):
    app_label_name = 'Home'
    description    = ''
    template_name  = 'home/newuser.html'
    success_url    = 'accounts:profile-settings'

    def get_form_class(self):
        if not self.permiso_administracion:
            self.form_class = NoAdminUserForm
        else:
            self.form_class = UserForm
        return self.form_class

    def get_object(self, queryset=None):
        if self.is_this_my_profile:
            obj = self.current_user.user
        elif self.permiso_administracion:
            obj = Profile.objects.get(pk=self.kwargs['pk']).user
        else:
            raise PermissionDenied
        return obj

    def clean_groups(self):
        form     = self.get_form()
        l_groups = form.data.getlist('groups')
        if self.permiso_administracion and self.is_this_my_profile: 
            group = Group.objects.get(name='Administrators')
            if str(group.id) not in l_groups:
                count =  Profile.objects.filter(user__groups=group, customer=self.current_user.customer).count()
                if count==1:
                    raise ValidationError('¡No puedes quedarte sin administradores!')
        return l_groups

    def get_form(self):
        self.form              = super(ProfileEdit, self).get_form(form_class=self.form_class)
        self.form.clean_groups = self.clean_groups
        return self.form

    def get_form_kwargs(self):
        kwargs = super(ProfileEdit, self).get_form_kwargs()
        if not kwargs.get('instance'):
            if not self.kwargs:
                kwargs['instance'] = self.current_user.user
            else:
                kwargs['instance'] = Profile.objects.get(pk = self.kwargs['pk']).user
        return kwargs

    @property
    def is_this_my_profile(self):
        if not self.kwargs.get('pk') or int(self.kwargs.get('pk')) == self.current_user.id:
            my_profile = True
        else:
            my_profile = False
        return my_profile
    
    def post(self, request, *args, **kwargs):
        self.object  = self.get_object()
        form         = self.get_form()
        if form.is_valid():
        	form.save()
        	form._save_m2m()
        	return self.form_valid(form)
        else:
            return self.form_invalid(form=form)

    def form_invalid(self, form=None, profile_form=None):
        form.is_valid()
        return self.render_to_response(self.get_context_data(form=form))

class ProfileList(BaseListMixin):
    tengo_que_ser_admin = True
    title          = 'Administración de Usuarios'
    description    = '' 
    app_label_name = 'home'
    template_name  = 'home/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        self.queryset = ExtendUser.objects.filter(company = self.current_user.currently_at)
        return super(ProfileList, self).get_queryset()

class DeleteUser(ProfileList):
    def get_queryset(self):
        user_delete = ExtendUser.objects.get(id=self.kwargs['pk'])
        user_delete.delete()
        self.queryset = ExtendUser.objects.filter(company = self.current_user.currently_at)
        return super(ProfileList, self).get_queryset()

class AlertRequest(BaseListMixin):
    tengo_que_ser_admin = True
    title          = ''
    description    = '' 
    app_label_name = 'home'
    template_name  = 'home/alert.html'
    context_object_name = 'estimates'

    def get_context_data(self, **kwargs):
        context = super(AlertRequest, self).get_context_data(**kwargs)
        context['id'] = self.kwargs['pk']
        return context

    # def get_queryset(self):
    #     self.queryset = Estimate.objects.filter(supervised_by=ExtendUser.objects.get(id=self.kwargs['pk'])).all()
    #     return super(AlertRequest, self).get_queryset()
