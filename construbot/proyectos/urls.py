from django.conf.urls import url

from . import views

app_name = 'construbot.proyectos'

urlpatterns = [
    url(
        regex=r'^$',
        view=views.ContratoListView.as_view(),
        name='listado_de_contratos'
    ),
]
