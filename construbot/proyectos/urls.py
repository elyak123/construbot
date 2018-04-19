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
        regex=r'^listado/sitios/$',
        view=views.SitioListView.as_view(),
        name='listado_de_sitios'
    ),
    url(
        regex=r'^listado/destinatarios/$',
        view=views.DestinatarioListView.as_view(),
        name='listado_de_destinatarios'
    ),
    url(
        regex=r'^contrato/catalogo-edit/(?P<pk>\d+)/$',
        view=views.CatalogoConceptosInlineFormView.as_view(),
        name='catalogo_conceptos'
    ),
    url(
        regex=r'^contrato/catalogo-list/(?P<pk>\d+)/$',
        view=views.CatalogoConceptos.as_view(),
        name='catalogo_conceptos_listado'
    ),
    url(
        regex=r'^contrato/detalle/(?P<pk>\d+)/$',
        view=views.ContratoDetailView.as_view(),
        name='contrato_detail'
    ),
    url(
        regex=r'^cliente/detalle/(?P<pk>\d+)/$',
        view=views.ClienteDetailView.as_view(),
        name='cliente_detail'
    ),
    url(
        regex=r'^sitio/detalle/(?P<pk>\d+)/$',
        view=views.SitioDetailView.as_view(),
        name='sitio_detail'
    ),
    url(
        regex=r'^destinatario/detalle/(?P<pk>\d+)/$',
        view=views.DestinatarioDetailView.as_view(),
        name='destinatario_detail'
    ),
    url(regex=r'^contrato/nuevo/$',
        view=views.ContratoCreationView.as_view(),
        name='nuevo_contrato'),

    url(regex=r'^cliente/nuevo/$',
        view=views.ClienteCreationView.as_view(),
        name='nuevo_cliente'),

    url(regex=r'^sitio/nuevo/$',
        view=views.SitioCreationView.as_view(),
        name='nuevo_sitio'),

    url(regex=r'^destinatario/nuevo/$',
        view=views.DestinatarioCreationView.as_view(),
        name='nuevo_destinatario'),

    url(regex=r'^editar/contrato/(?P<pk>\d+)/$',
        view=views.ContratoEditView.as_view(),
        name='editar_contrato'),

    url(regex=r'^editar/cliente/(?P<pk>\d+)/$',
        view=views.ClienteEditView.as_view(),
        name='editar_cliente'),

    url(regex=r'^editar/sitio/(?P<pk>\d+)/$',
        view=views.SitioEditView.as_view(),
        name='editar_sitio'),

    url(regex=r'^editar/destinatario/(?P<pk>\d+)/$',
        view=views.DestinatarioEditView.as_view(),
        name='editar_destinatario'),

    url(regex=r'cliente-autocomplete/$',
        view=views.ClienteAutocomplete.as_view(),
        name='cliente-autocomplete'),

    url(regex=r'sitio-autocomplete/$',
        view=views.SitioAutocomplete.as_view(),
        name='sitio-autocomplete'),
    url(regex=r'^unit-autocomplete/$',
        view=views.UnitAutocomplete.as_view(create_field='unit'),
        name='unit-autocomplete'),
]
