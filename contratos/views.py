from django.shortcuts import render
from accounts.views       import AuthenticationTestMixin
from django.views         import View
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import DetailView

# Create your views here.

# class PmgtMenuMixin(object):
#     app_label_name = 'Proyectos'
#     tengo_que_ser_admin = True
#     menu_specific  = [
#         {
#             'title'  :'Contrato',
#             'url'    : '',
#             'icon'   : 'glyphicon glyphicon-bookmark',
#             'parent' : True,
#             'child': '',
#             'type': 'submenu',
#             'submenu': [
#                 {
#                     'title'    : 'Cat. Conceptos',
#                     'url'      : '',
#                     'urlkwargs': '',
#                     'icon'     : ''
#                 },
#                 {
#                     'title'    : 'Estimaciones',
#                     'url'      : 'pmgt:PmgtList',
#                     'urlkwargs': {'modelform':'estimate'},
#                     'icon'     : ''
#                 },
#                 {
#                     'title'    : 'Facturación',
#                     'url'      : '',
#                     'urlkwargs': '',
#                     'icon'     : ''
#                 },
#                 {
#                     'title'    : 'Gastos',
#                     'url'      : 'pmgt:nueva-factura',
#                     'urlkwargs': '',
#                     'icon'     : ''
#                 },
#                 { 
#                     'title'    : 'Mano de Obra',
#                     'url'      : '',
#                     'urlkwargs': '',
#                     'icon'     : ''
#                 },
#                 {
#                     'title'    : 'Fianzas',
#                     'url'      : '',
#                     'urlkwargs': '',
#                     'icon'     : ''
#                 },
#             ],
#         },
#         {   
#             'title'  : 'Cátalogos',
#             'url'    : '',
#             'urlkwargs': '',
#             'icon'   : 'glyphicon glyphicon-book',
#             'parent' : True,
#             'child': '',
#             'type': 'submenu',
#             'submenu': [
#                 {
#                     'title'    : 'Unidades',
#                     'url'      : 'pmgt:BasicCreateView',
#                     'urlkwargs': {'modelform':'units'},
#                     'icon'     : ''
#                 },
#                {
#                     'title'    : 'Mano de obra',
#                     'url'      : '',
#                     'urlkwargs': '',
#                     'icon'     : '',
#                     'type': '',
#                 },
#                 {
#                     'title'    : 'Materiales',
#                     'url'      : 'pmgt:PmgtList',
#                     'urlkwargs': {'modelform':'materials'},
#                     'icon'     : '',
#                     'type': '',
#                 },
#                 {
#                     'title'    : 'Proveedores',
#                     'url'      : 'pmgt:PmgtList',
#                     'urlkwargs': {'modelform':'supplier'},
#                     'icon'     : '',
#                     'type': '',
#                 },
#                 {
#                     'title'    : 'Fianzas',
#                     'url'      : '',
#                     'urlkwargs': '',
#                     'icon'     : '',
#                     'type': '',
#                 },
#             ]
#         },
#         {
#             'title'  : 'Reportes',
#             'url'    : 'pmgt:pmgt_dashboard',
#             'icon'   : 'glyphicon glyphicon-sort-by-attributes',
#             'parent' : True,
#             'child': '',
#             'type': 'submenu',
#             'submenu': [
#                 {
#                     'title'    : 'Historial de materiales',
#                     'url'      : 'pmgt:historial-materiales',
#                     'urlkwargs': '',
#                     'icon'     : '',
#                     'type': '',
#                 },
#                 {
#                     'title'    : 'Reporte Financiero',
#                     'url'      : '',
#                     'urlkwargs': '',
#                     'icon'     : '',
#                     'type': '',
#                 },
#             ],
#         },
#     ]
#     model_form_options = {
#         'units': {
#             'model': models.Units,
#             'form' : forms.UnitFormSet
#         },
#         'estimate': {
#             'model': models.Estimate,
#             'form' : forms.EstimateForm
#         },
#         'concept': {
#             'model': models.Concept,
#             'form' : forms.ConceptForm
#         },
#         'invoice': {
#             'model': models.ExpenseInvoice,
#             'form': forms.ExpenseInvoiceForm
#         },
#         'supplier':{
#             'model': models.Supplier,
#             'form' : ''
#         },
#         'materials':{
#             'model': models.ExpenseInvoiceConceptName,
#             'form' : ''
#         }
#     }
#     def get_context_data(self, **kwargs):
#         context = super(PmgtMenuMixin, self).get_context_data(**kwargs)
#         context['contratos'] = Contrato.objects.filter(
#             cliente__company = self.current_user.currently_at,
#             status=True
#         )
#         return context

# class BasicPmgtEdition(PmgtMenuMixin, BaseEditMixin):
#     description   = 'Administracion de Proyectos'
#     template_name = 'pmgt/form.html'

#     def get_success_url(self):
#         url = reverse('login')
#         return url

# class BasicPmgtUpdateView(BasicPmgtEdition, UpdateMixin):
#     pass

# class BasicPmgtListView(PmgtMenuMixin, BaseListMixin):
#     """docstring for UnitListView"""
#     def get_queryset(self):
#         self.model = self.model_form_options[self.kwargs['modelform']]['model']
#         return super(BasicPmgtListView, self).get_queryset()

# class EstimateList(BasicPmgtListView):
#     app_label_name = 'Proyectos'
#     description = ''
#     def get_title(self):
#         title = 'Listado de %s' % self.kwargs['modelform']
#         return title

# class EstimateUpdateView(BasicPmgtUpdateView):
#     tengo_que_ser_admin = False
#     template_name = 'pmgt/form.html'
#     title         = 'Edicion de Estimación.'
#     model         = models.Estimate

#     def get_object(self, queryset=None):
#         self.object = get_object_or_404(
#             self.model, 
#             pk=self.kwargs['pk'], 
#             project__cliente__company = self.current_user.currently_at
#         )
#         return self.object
    
#     def get_form_class(self):
#         return forms.EstimateForm

#     def get_initial(self):
#         init_dict = {}
#         init_dict['draft_by'] = self.current_user
#         init_dict['project'] = self.kwargs['pk']
#         return super(EstimateUpdateView, self).get_initial()

#     def form_valid(self, form):
#         conceptFormClass = forms.estimateConceptInlineForm()
#         self.conceptForm = conceptFormClass(self.request.POST, instance=self.object)
#         if self.conceptForm.is_valid():
#             self.conceptForm.save()
#             return super(EstimateUpdateView, self).form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def get_context_data(self, **kwargs):
#         context = super(EstimateUpdateView, self).get_context_data(**kwargs)
#         project_instance = models.Estimate.objects.get(pk=self.kwargs.get('pk')).project
#         concept_set_count = project_instance.concept_set.all().count()
#         formset = forms.estimateConceptInlineForm()
#         context['generator_inline_concept'] = formset(instance=self.object)
#         context['project_instance'] = project_instance
#         return context

#     def get_success_url(self):
#         project_id = models.Estimate.objects.get(pk=self.kwargs.get('pk')).project.id
#         url = reverse_lazy('pmgt:ContractDetail', kwargs={
#             'pk': project_id
#         })
#         return url

# class ContractDetail(PmgtMenuMixin, AuthenticationTestMixin, DetailView):
#     """
#         Contract Detail Regarding estimates and liabilities
#     """
#     description = 'Vista de detalle del contrato.'
#     model       = Contrato

#     def get_title(self):
#         self.title = 'Detalle de Contrato'
#         return self.title

#     def get_context_data(self, **kwargs):
#         context = super(ContractDetail, self).get_context_data(**kwargs)
#         if self.object.estimate_set.all().exists():
#             estimate_set = self.object.estimate_set.annotate(
#                 total_estimate=Round(
#                     Sum(
#                         F('estimateconcept__cuantity_estimated') * F('concept__unit_price')
#                     )
#                 )
#             ).order_by('start_date')
#             concept_set  = self.object.concept_set.all()
#             context['app_label_name'] = self.app_label_name
#             context['estimate_set']   = estimate_set
#             context['concept_set']    = concept_set
#             context["algo"]="/algo/"
#         return context


#     def get_object(self, queryset=None):
#         self.object = get_object_or_404(
#             self.model, 
#             pk=self.kwargs['pk'], 
#             cliente__company=self.current_user.currently_at
#         )
#         return self.object

# class DeleteEstimate(ContractDetail):

#     def get_context_data(self, **kwargs):
#         context = super(DeleteEstimate, self).get_context_data(**kwargs)

#         new_consecutive = self.kwargs['esid']
#         try:
#             del_estimate = models.Estimate.objects.get(consecutive = self.kwargs['esid'], project = self.object)
#         except MultipleObjectsReturned:
#             """
#                 En caso de que haya un error a la mitad de la ejecucuón
#                 (que el servidor se apague momentaneamente por ejemplo)
#                 y existan dos estimaciones con el mismo consecutivo...
                
#                 Tarea:
#                 Solicitar a carlos un mensaje especial advirtiendo que se eliminarán mas de
#                 una estimación por tener concecutivos repetidos.
#             """
#             del_estimate = models.Estimate.objects.filter(consecutive = self.kwargs['esid'], project = self.object)
#         del_estimate.delete()
#         all_estimates = models.Estimate.objects.filter(project = self.object)
#         for estimate in all_estimates:
#             if estimate.consecutive > int(new_consecutive):
#                 estimate.consecutive = estimate.consecutive-1
#                 estimate.save()
            

#         if self.object.estimate_set.all().exists():
#             estimate_set = self.object.estimate_set.annotate(
#                 total_estimate=Round(
#                     Sum(
#                         F('estimateconcept__cuantity_estimated') * F('concept__unit_price')
#                     )
#                 )
#             ).order_by('start_date')
#             concept_set  = self.object.concept_set.all()
#             context['app_label_name'] = self.app_label_name
#             context['estimate_set']   = estimate_set
#             context['concept_set']    = concept_set
#             context["algo"]="/algo/"
#         return context

# class EstimateCreationView(BasicPmgtCreateView, BasicPmgtUpdateView):
#     """
#         a través del contrato
#         url:
#         pmgt:pmgt_new_estimate
#     """
#     form_class = forms.EstimateForm
#     model      = Contrato

#     def get(self, request, *args, **kwargs):
#         """
#         Handles GET requests and instantiates blank versions of the form
#         and its inline formsets.
#         """
#         self.object = None
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         fill_data = self.fill_concept_formset()
#         inlineform = forms.estimateConceptInlineForm(count=self.concept_count)
#         generator_inline_concept = inlineform(initial=fill_data)
#         return self.render_to_response(
#                   self.get_context_data(form=form,
#                                         generator_inline_concept=generator_inline_concept,
#                                         )
#                                      )

#     def post(self, request, *args, **kwargs):
#         """
#         Handles POST requests, instantiating a form instance and its inline
#         formsets with the passed POST variables and then checking them for
#         validity.
#         """
#         self.object = None
#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def fill_concept_formset(self):
#         """
#         Aqui me quedé
#         """
#         project_instance = get_object_or_404(
#             Contrato, 
#             pk=self.kwargs.get('pk'), 
#             cliente__company=self.current_user.currently_at
#         )
#         concepts = models.Concept.objects.filter(project=project_instance).order_by('id')
#         data = [{'concept': x, 'cuantity_estimated': 0, 'concept_text_input': x.concept_text} for x in concepts]
#         self.concept_count = concepts.count()
#         return data

#     def get_initial(self):
#         initial_dict = super(EstimateCreationView, self).get_initial()

#         max_consecutive = Estimate._meta.model._default_manager.filter(
#             project = self.kwargs['pk']
#         ).aggregate(Max('consecutive'))['consecutive__max'] or 0
#         max_consecutive+=1

#         initial_dict['consecutive'] = max_consecutive
#         initial_dict['project'] = self.kwargs['pk']
#         initial_dict['draft_by'] = self.current_user
#         return initial_dict

#     def form_valid(self, form):
#         """
#         Called if all forms are valid. Creates EstimateForm instance along with the
#         associated Generator instances then redirects to success url
#         Args:
#             form: EstimateForm Form
#             generator_inline_concept

#         Returns: an HttpResponse to success url

#         """
#         form.save()
#         fill_data = self.fill_concept_formset()
#         inlineform = forms.estimateConceptInlineForm(count=self.concept_count)
#         generator_inline_concept = inlineform(self.request.POST, instance=form.instance)
#         if generator_inline_concept.is_valid():
#             generator_inline_concept.save()
#         else:
#             return self.form_invalid(form, generator_inline_concept)
#         return super(EstimateCreationView, self).form_valid(form)

#     def form_invalid(self, form, generator_inline_concept):
#         """
#         Called if a form is invalid. Re-renders the context data with the
#         data-filled forms and errors.

#         Args:
#             form: EstimateForm Form
#             generator_inline_concept:
#         """
#         return self.render_to_response(
#                  self.get_context_data(form=form,
#                                        generator_inline_concept=generator_inline_concept
#                                        )
#         )
#         """
#         Pequeño Cambio en éste método cuando se presiona el botón "cancelar".
#         A little change in this method when the button "cancelar" is pressed.
#         """
#     def get_success_url(self):
#         url = reverse_lazy('pmgt:ContractDetail', kwargs={
#             'pk': self.kwargs['pk']
#         })
#         return url

#     def get_context_data(self, **kwargs):
#         context = super(EstimateCreationView, self).get_context_data(**kwargs)
#         context['project_instance'] = Contrato.objects.get(pk=self.kwargs['pk'])
#         return context

# class BasicPmgtDetailView(PmgtMenuMixin, GenericEstimateDetailView):
#     description = 'Vista detalle de la estimación.'
#     title       = 'Detalle de la Estimación'

#     def get_context_data(self, **kwargs):
#         context = super(BasicPmgtDetailView, self).get_context_data(**kwargs)
#         concept_set_amount = self.object.concept_set.annotate(
#                 total_concept_amount=Round(
#                         F('total_cuantity') * F('unit_price')
#                 ),
#             ).order_by('id')

#         contratado = self.object.concept_set.aggregate(
#             suma = Round(
#                     Sum(F('total_cuantity') * F('unit_price'))
#                 ),
#         )

#         cuantity_estimated = []
#         last_estimate_total = 0
#         historic_total = 0
#         for concept in concept_set_amount:
#             estimateconcept = concept.estimateconcept_set.filter(estimate=self.object)
#             estimateconcept_amount = estimateconcept.annotate(
#                 total_amount=Round(F('cuantity_estimated') * F('concept__unit_price'))
#             )
#             conceptos = models.EstimateConcept.objects.filter(
#                 concept  = concept,
#                 estimate__consecutive__lte = self.object.consecutive,
#                 estimate__project = self.object.project
#             )
#             sumatoria = conceptos.aggregate(
#                 estimado=Round(Sum('cuantity_estimated'))
#             )

#             my_list = {}
            
#             if self.object.consecutive > 1:
#                 try:
#                     last_estimateconcept = concept.estimateconcept_set.filter(
#                         estimate__consecutive=self.object.consecutive-1
#                     )
#                     last_estimateconcept_amount = last_estimateconcept.annotate(
#                         total_amount=Round(F('cuantity_estimated') * F('concept__unit_price'))
#                     )
#                     my_list.update({
#                         'last_cuantity': last_estimateconcept.first().cuantity_estimated,
#                         'last_amount'  : last_estimateconcept_amount.first().total_amount,
#                     })
#                 except AttributeError:
#                     my_list.update({
#                         'last_cuantity': 0,
#                         'last_amount'  : 0,
#                     })
#                 last_estimate_total += my_list['last_amount']

#             sumatoria = sumatoria['estimado']
#             acumulado = sumatoria * concept.unit_price
#             historic_total += acumulado
#             my_list.update({
#                 'concept': concept, 
#                 'cuantity':estimateconcept.first().cuantity_estimated,
#                 'amount': estimateconcept_amount.first().total_amount,
#                 'observations': estimateconcept_amount.first().observations,
#                 'sumatoria': sumatoria,
#                 'acumulado': acumulado,
#             })
#             cuantity_estimated.append(my_list)
#         context['auth_by_es1']  = self.object.auth_by.all()[0:2]
#         context['auth_by_es2']  = self.object.auth_by.all()[2:5]
#         context['auth_by_es3']  = self.object.auth_by.all()[5:8]
#         context['auth_by_gen1'] = self.object.auth_by_gen.all()[0:2]
#         context['auth_by_gen2'] = self.object.auth_by_gen.all()[2:5]
#         context['auth_by_gen3'] = self.object.auth_by_gen.all()[5:8]
#         context['last_estimate_total'] = last_estimate_total
#         context['historic_total'] = historic_total
#         context['concept_set']  = cuantity_estimated
#         context['contratado'] = contratado
#         context['client'] = self.object.project.cliente
#         return context

# class UnitAutocomplete(PmgtAutocomplete):
#     model        = models.Units
#     company_wise = False

#     def get_key_words(self):
#         self.key_words = {'unit__unaccent__icontains':self.q}
#         return self.key_words

#     def get_queryset(self):
#         if self.current_user:
#             qs = self.model.objects.filter(**self.get_key_words())
#             return qs
#         elif self.current_user and self.request.POST:
#             return self.model.objects

# class SupplierAutocomplete(PmgtAutocomplete):
#     model = models.Supplier

#     def get_key_words(self):
#         self.key_words = {
#             'supplier_name__unaccent__icontains':self.q,
#             'company': self.current_user.currently_at
#         }
#         return self.key_words

#     def get_post_key_words(self):
#         obj = {}
#         if self.current_user.currently_at:
#             obj.update({'company': self.current_user.currently_at})
#         return obj

# class ExpenseInvoiceConceptAutocomplete(PmgtAutocomplete):
#     model = models.ExpenseInvoiceConceptName

#     def get_key_words(self):
#         self.key_words = {
#             'concept_name__unaccent__icontains':self.q,
#             'company__in': self.current_user.company.all()
#         }
#         return self.key_words

#     def get_post_key_words(self):
#         obj = {}
#         if self.current_user.currently_at:
#             obj.update({'company': self.current_user.currently_at})
#         return obj

# class CompanyAutocomplete(PmgtAutocomplete):
#     model        = models.Company
#     company_wise = False

#     def get_queryset(self):
#         if self.current_user and self.q:
#             companies = [x.company_name for x in self.current_user.company.all()]
#             qs = self.model.objects.filter(
#                 company_name__unaccent__icontains=self.q,
#                 company_name__in=companies
#             )
#             return qs
#         elif self.current_user and self.request.POST:
#             return self.model.objects
