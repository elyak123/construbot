from django.conf.urls import url

from . import views

app_name = 'construbot.users'

urlpatterns = [
    url(
        regex=r'^$',
        view=views.UserListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^remove-is-new/(?P<pk>\d+)/$',
        view=views.RemoveIsNewUserStatus.as_view(),
        name='remove_is_new'
    ),
    url(
        regex=r'^eliminar/(?P<model>\w+)/(?P<pk>\d+)/$',
        view=views.UserDeleteView.as_view(),
        name='delete_user'
    ),
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),
    url(
        regex=r'^new/$',
        view=views.UserCreateView.as_view(),
        name='new'
    ),
    url(
        regex=r'^nuevo/company/$',
        view=views.CompanyCreateView.as_view(),
        name='new_company'
    ),
    url(
        regex=r'^company-update/(?P<pk>\d+)/$',
        view=views.CompanyEditView.as_view(),
        name='company_edit'
    ),
    url(
        regex=r'^listado/company/$',
        view=views.CompanyListView.as_view(),
        name='company_list'
    ),
    url(
        regex=r'^detalle/company/(?P<pk>\d+)/$',
        view=views.CompanyDetailView.as_view(),
        name='company_detail'
    ),
    url(
        regex=r'^detalle/(?:(?P<username>[\w.@+-]+)/)?$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^update/(?:(?P<username>[\w.@+-]+)/)?$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),
    url(
        regex=r'^company-change/(?P<company>[\w ]+)/$',
        view=views.CompanyChangeView.as_view(),
        name='company-change'
    ),
]
