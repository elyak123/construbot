from django.conf.urls import url

from . import views

app_name = 'construbot.proyectos'

urlpatterns = [
    url(
        regex=r'^listado/$',
        view=views.ContratoListView.as_view(),
        name='listado_de_contratos'
    ),
    url(
        regex=r'^detalle/(?P<pk>\d+)/$',
        view=views.ContratoDetailView.as_view(),
        name='detalle_de_contrato'
    ),
]
