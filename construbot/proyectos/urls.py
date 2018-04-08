from django.conf.urls import url

from . import views

app_name = 'construbot.proyectos'

urlpatterns = [
    url(
        regex=r'^$',
        view=views.ContratoListView.as_view(),
        name='listado_de_contratos'
    ),
    url(regex=r'^contratos/nuevo/$',
        view=views.ContratoCreationView.as_view(),
        name='nuevo_contrato'),
]
