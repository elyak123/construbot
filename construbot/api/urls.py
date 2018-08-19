from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from . import views

app_name = 'construbot.api'

urlpatterns = [
    url(regex='customer/list/', view=views.CustomerList.as_view(), name='customerlist'),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(
        regex=r'^users/unique/$',
        view=views.email_uniqueness, name='get_user'
    ),
    url(
        regex=r'^create/$',
        view=views.create_customer_user_and_company, name='creation'
    ),
    url(
        regex=r'^change-usr-pwd/$',
        view=views.change_user_password, name='change_pwd'
    ),
]
