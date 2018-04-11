from django.conf.urls import url

from . import views

app_name = 'construbot.proyectos'

urlpatterns = [
    url(
        regex=r'^listado/contratos/$',
        view=views.ContratoListView.as_view(),
        name='listado_de_contratos'
    ),
    url(
        regex=r'^listado/clientes/$',
        view=views.ClienteListView.as_view(),
        name='listado_de_clientes'
    ),
    url(
        regex=r'^detalle/(?P<pk>\d+)/$',
        view=views.ContratoDetailView.as_view(),
        name='contrato_detail'
    ),
    url(regex=r'^contrato/nuevo/$',
        view=views.ContratoCreationView.as_view(),
        name='nuevo_contrato'),

    url(regex=r'^cliente/nuevo/$',
        view=views.ClienteCreationView.as_view(),
        name='nuevo_cliente'),

    url(regex=r'^sitio/nuevo/$',
        view=views.ClienteCreationView.as_view(),
        name='nuevo_sitio'),

    url(regex=r'cliente-autocomplete/$',
        view=views.ClienteAutocomplete.as_view(),
        name='cliente-autocomplete'),
    url(regex=r'sitio-autocomplete/$',
        view=views.SitioAutocomplete.as_view(),
        name='sitio-autocomplete'),
]
