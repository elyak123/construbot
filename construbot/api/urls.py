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
        regex=r'^users/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        view=views.UserRetrive.as_view(), name='get_user'
    )
]
