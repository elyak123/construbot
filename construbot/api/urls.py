from django.conf.urls import url

from . import views

app_name = 'construbot.api'

urlpatterns = [
    url(regex='customer/list/', view=views.customer_list, name='customerlist'),
]
