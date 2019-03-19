from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^signup/$', views._SignupView.as_view(), name='account_signup'),
    url(r'^login/$', views._LoginView.as_view(), name='account_login'),
    url(r'^logout/$', views._LogoutView.as_view(), name='account_logout'),

    url(r'^password/change/(?:(?P<username>[\w.@+-]+)/)?$', views._PasswordChangeView.as_view(),
        name='account_change_password'),
    url(r'^password/set/$', views._PasswordSetView.as_view(), name='account_set_password'),

    url(r'^inactive/$', views._AccountInactiveView.as_view(), name='account_inactive'),

    # E-mail
    url(r'^email/$', views._EmailView.as_view(), name='account_email'),
    url(r'^confirm-email/$', views._EmailVerificationSentView.as_view(),
        name='account_email_verification_sent'),
    url(r'^confirm-email/(?P<key>[-:\w]+)/$', views._ConfirmEmailView.as_view(),
        name='account_confirm_email'),

    # password reset
    url(r'^password/reset/$', views._PasswordResetView.as_view(),
        name='account_reset_password'),
    url(r'^password/reset/done/$', views._PasswordResetDoneView.as_view(),
        name='account_reset_password_done'),
    url(r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        views._PasswordResetFromKeyView.as_view(),
        name='account_reset_password_from_key'),
    url(r'^password/reset/key/done/$', views._PasswordResetFromKeyDoneView.as_view(),
        name='account_reset_password_from_key_done'),
]
