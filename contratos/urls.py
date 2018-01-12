from django.conf.urls import url
from .                import views, models

app_name = 'contratos'

urlpatterns = [
	# index
    # url(r'^$', views.DashboardView.as_view(), name='pmgt_dashboard'),
    # # Autocompletados
    # url(r'^unit-autocomplete/$', views.UnitAutocomplete.as_view(create_field='unit'), name='unit-autocomplete'),
    # url(r'^supplier-autocomplete/$', views.SupplierAutocomplete.as_view(create_field='supplier_name'), name='supplier-autocomplete'),
    # url(r'^expense-invoice-concept-name-autocomplete/$', views.ExpenseInvoiceConceptAutocomplete.as_view(create_field='concept_name'), name='expense-invoice-concept-name-autocomplete'),
    # url(r'^company-autocomplete/$', views.CompanyAutocomplete.as_view(), name='company-autocomplete'),
    # # Detalle contratos y estimaciones
    # url(r'^list/(?P<modelform>\w+)/$',views.EstimateList.as_view(), name='pmgt_list'),
    # url(r'^edit/estimate/(?P<pk>\d+)/$', views.EstimateUpdateView.as_view(), name='estimate_update_view'),
    # url(r'^detail/contratos/(?P<pk>\d+)/$', views.ContractDetail.as_view(), name='contract_detail'),
    # url(r'^delete/estimate/(?P<pk>\d+)/(?P<esid>\d+)/$', views.DeleteEstimate.as_view(), name='delete_estimate'),
    # url(r'^new/estimate/(?P<pk>\d+)/$', views.EstimateCreationView.as_view(), name='pmgt_new_estimate'),
    # url(r'^detail/(?P<modelform>\w+)/(?P<pk>\d+)/$', views.BasicPmgtDetailView.as_view(), name='generic_estimate_detail_view'),
]