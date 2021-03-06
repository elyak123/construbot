from django.conf.urls import url
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views

app_name = 'construbot.api'

urlpatterns = [
    url(regex='customer/list/', view=views.CustomerList.as_view(), name='customerlist'),
    url(r'^api-token-auth/', TokenObtainPairView.as_view()),
    url(r'^api-token-refresh/', TokenRefreshView.as_view()),
    url(r'^api-token-verify/', TokenVerifyView.as_view()),
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
    url(
        regex=r'^migraciones/Cliente/$',
        view=views.DataMigration.cliente_migration, name='migracion_de_clientes'
    ),
    url(
        regex=r'^migraciones/Sitio/$',
        view=views.DataMigration.sitio_migration, name='migracion_de_sitios'
    ),
    url(
        regex=r'^migraciones/Destinatario/$',
        view=views.DataMigration.destinatario_migration, name='migracion_de_sitios'
    ),
    url(
        regex=r'^migraciones/Contrato/$',
        view=views.DataMigration.contrato_concept_and_estimate_migration, name='migracion_de_contratos'
    ),
]
