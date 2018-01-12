from django.conf.urls import url
from .                import views, models
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [

    url(r'^profile_settings/(?:(?P<pk>\d+)/)?$', views.ProfileSettings.as_view(), name='profile-settings'),
    url(r'^profile_edit/(?:(?P<pk>\d+)/)?$', views.ProfileEdit.as_view(), name='profile-edit'),
    url(r'^profile_list/$', views.ProfileList.as_view(), name='profile-list'),
    url(r'^delete_user/(?P<pk>\d+)$', views.DeleteUser.as_view(), name='delete-user'),
    url(r'^new_user/$', views.NewUser.as_view(), name='new_user'),
    url(r'^alert/(?P<pk>\d+)$', views.AlertRequest.as_view(), name='alert-request'),


	#url(r'^profile', views.ProfileDetail, name='ProfileDetail'),
    url(r'^password_change/$', auth_views.password_change, {
    	'template_name': 'accounts/password_change_form.html', 
    	'post_change_redirect':'accounts:password_change_done'}, name='password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done, {
    	'template_name': 'accounts/password_change_done.html'}, name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
]