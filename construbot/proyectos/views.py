from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.db.models import Max
from django.db.models.functions import Lower
from django.http import JsonResponse
from dal import autocomplete
from users.auth import AuthenticationTestMixin
from .apps import ProyectosConfig
from .models import Contrato, Cliente, Sitio, Units, Concept, Destinatario, Estimate
from .forms import (ContratoForm, ClienteForm, SitioForm, DestinatarioForm, ContractConceptInlineForm, EstimateForm,
                    estimateConceptInlineForm)


class ProyectosMenuMixin(AuthenticationTestMixin):
    app_label_name = ProyectosConfig.verbose_name
    menu_specific = [
        {
            'title': 'Catalogos',
            'url': '',
            'icon': 'book',
            'parent': True,
            'type': 'submenu',
            'submenu': [
                {
                    'title': 'Contratos',
                    'url': 'construbot.proyectos:listado_de_contratos',
                    'urlkwargs': '',
                    'icon': 'bookmark',
                },
                {
                    'title': 'Clientes',
                    'url': 'construbot.proyectos:listado_de_clientes',
                    'urlkwargs': '',
                    'icon': 'person',
                },
                {
                    'title': 'Ubicaciones',
                    'url': 'construbot.proyectos:listado_de_sitios',
                    'urlkwargs': '',
                    'icon': 'map-marker',
                },
                {
                    'title': 'Contactos',
                    'url': 'construbot.proyectos:listado_de_destinatarios',
                    'urlkwargs': '',
                    'icon': 'people',
                },
            ],
        }
    ]
    model_options = {
        'Contrato': {
            'model': Contrato,
        },
        'Cliente': {
            'ordering': 'cliente_name',
            'model': Cliente,
        },
        'Sitio': {
            'ordering': 'sitio_name',
            'model': Sitio,
        },
        'Destinatario': {
            'ordering': 'destinatario_text',
            'model': Destinatario,
        },
    }

    def get_company_query(self, opcion):
        company_query = {
            'Contrato': {
                'cliente__company': self.request.user.currently_at
            },
            'Cliente': {
                'company': self.request.user.currently_at
            },
            'Sitio': {
                'company': self.request.user.currently_at
            },
            'Destinatario': {
                'cliente__company': self.request.user.currently_at
            },
            'Estimate': {
                'project__cliente__company': self.request.user.currently_at
            },
        }
        return company_query[opcion]


class DynamicList(ProyectosMenuMixin, ListView):
    paginate_by = 10

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = self.model.objects.filter(
                **self.get_company_query(self.model.__name__)).order_by(
                Lower(self.model_options[self.model.__name__]['ordering'])
            )
        return super(DynamicList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(DynamicList, self).get_context_data(**kwargs)
        context['model'] = self.model.__name__
        return context


class ContratoListView(DynamicList):
    model = Contrato
    ordering = '-fecha'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            **self.get_company_query(self.model.__name__))
        return super(ContratoListView, self).get_queryset()


class ClienteListView(DynamicList):
    model = Cliente


class SitioListView(DynamicList):
    model = Sitio


class DestinatarioListView(DynamicList):
    model = Destinatario


class CatalogoConceptos(ProyectosMenuMixin, ListView):
    model = Concept
    ordering = 'code'

    def get(self, request, *args, **kwargs):
        contrato = get_object_or_404(Contrato, pk=self.kwargs['pk'], cliente__company=self.request.user.currently_at)
        queryset = self.model.objects.filter(project=contrato)
        json = {}
        json['conceptos'] = []
        for concepto in queryset:
            aux = {}
            aux["code"] = concepto.code
            aux["concept_text"] = concepto.concept_text
            aux["unit"] = concepto.unit.unit
            aux["cuantity"] = concepto.total_cuantity
            aux["unit_price"] = concepto.unit_price
            json['conceptos'].append(aux)
        return JsonResponse(json)


class DynamicDetail(ProyectosMenuMixin, DetailView):
    def get_context_object_name(self, obj):
        return obj.__class__.__name__.lower()

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'], **self.get_company_query(self.model.__name__))


class ContratoDetailView(DynamicDetail):
    model = Contrato


class ClienteDetailView(DynamicDetail):
    model = Cliente


class SitioDetailView(DynamicDetail):
    model = Sitio


class DestinatarioDetailView(DynamicDetail):
    model = Destinatario


class EstimateDetailView(DynamicDetail):
    model = Estimate

    def get_context_data(self, **kwargs):
        context = super(EstimateDetailView, self).get_context_data(**kwargs)
        conceptos = self.model.get_concept_total(self.object)
        context["conceptos"] = conceptos["conceptos"]
        context["totales"] = conceptos["totales"]
        return context


class ContratoCreationView(ProyectosMenuMixin, CreateView):
    form_class = ContratoForm
    template_name = 'proyectos/creation_form.html'

    def get_initial(self):
        initial_obj = super(ContratoCreationView, self).get_initial()
        max_id = self.form_class.Meta.model.objects.filter(
            cliente__company=self.request.user.currently_at
        ).aggregate(Max('folio'))['folio__max'] or 0
        max_id += 1
        initial_obj['currently_at'] = self.request.user.currently_at.company_name
        initial_obj['folio'] = max_id
        return initial_obj

    def get_context_data(self, **kwargs):
        context = super(ContratoCreationView, self).get_context_data(**kwargs)
        context['company'] = self.request.user.currently_at
        return context

    def form_valid(self, form):
        if form.cleaned_data['currently_at'] == self.request.user.currently_at.company_name:
            return super(ContratoCreationView, self).form_valid(form)
        else:
            return super(ContratoCreationView, self).form_invalid(form)


class DynamicCreation(ProyectosMenuMixin, CreateView):
    template_name = 'proyectos/creation_form.html'

    def get_initial(self):
        initial_obj = super(DynamicCreation, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            return super(DynamicCreation, self).form_valid(form)
        else:
            return super(DynamicCreation, self).form_invalid(form)


class ClienteCreationView(DynamicCreation):
    form_class = ClienteForm


class SitioCreationView(DynamicCreation):
    form_class = SitioForm


class DestinatarioCreationView(DynamicCreation):
    form_class = DestinatarioForm


class EstimateCreationView(ProyectosMenuMixin, UpdateView):
    """
        a través del contrato
        url:
        pmgt:pmgt_new_estimate
    """
    form_class = EstimateForm
    model = Contrato
    template_name = 'proyectos/estimate_form.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        fill_data = self.fill_concept_formset()
        inlineform = estimateConceptInlineForm(count=self.concept_count)
        generator_inline_concept = inlineform(initial=fill_data)
        image_formset_prefix = [x.nested.prefix for x in generator_inline_concept.forms]
        return self.render_to_response(
            self.get_context_data(form=form,
                                  generator_inline_concept=generator_inline_concept,
                                  image_formset_prefix=image_formset_prefix,
                                  )
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            fill_data = self.fill_concept_formset()
            inlineform = estimateConceptInlineForm(count=self.concept_count)
            generator_inline_concept = inlineform(initial=fill_data)
            return self.form_invalid(form, generator_inline_concept)

    def fill_concept_formset(self):
        """
        Aqui me quedé
        """
        project_instance = get_object_or_404(
            Contrato,
            pk=self.kwargs.get('pk'),
            cliente__company=self.request.user.currently_at
        )
        concepts = Concept.objects.filter(project=project_instance).order_by('id')
        data = [{'concept': x, 'cuantity_estimated': 0, 'concept_text_input': x.concept_text} for x in concepts]
        self.concept_count = concepts.count()
        return data

    def get_initial(self):
        initial_dict = super(EstimateCreationView, self).get_initial()

        max_consecutive = Estimate._meta.model._default_manager.filter(
            project=self.kwargs['pk']
        ).aggregate(Max('consecutive'))['consecutive__max'] or 0
        max_consecutive += 1

        initial_dict['consecutive'] = max_consecutive
        initial_dict['project'] = self.kwargs['pk']
        initial_dict['draft_by'] = self.request.user
        return initial_dict

    def form_valid(self, form):
        """
        Called if all forms are valid. Creates EstimateForm instance along with the
        associated Generator instances then redirects to success url
        Args:
            form: EstimateForm Form
            generator_inline_concept

        Returns: an HttpResponse to success url

        """
        form.save()
        fill_data = self.fill_concept_formset()
        inlineform = estimateConceptInlineForm(count=self.concept_count)
        generator_inline_concept = inlineform(self.request.POST, instance=form.instance)
        if generator_inline_concept.is_valid():
            generator_inline_concept.save()
        else:
            return self.form_invalid(form, generator_inline_concept)
        return super(EstimateCreationView, self).form_valid(form)

    def form_invalid(self, form, generator_inline_concept):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.

        Args:
            form: EstimateForm Form
            generator_inline_concept:
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  generator_inline_concept=generator_inline_concept
                                  )
        )
        """
        Pequeño Cambio en éste método cuando se presiona el botón "cancelar".
        A little change in this method when the button "cancelar" is pressed.
        """
    def get_success_url(self):
        url = reverse_lazy('proyectos:contrato_detail', kwargs={
            'pk': self.kwargs['pk']
        })
        return url

    def get_context_data(self, **kwargs):
        context = super(EstimateCreationView, self).get_context_data(**kwargs)
        context['project_instance'] = Contrato.objects.get(pk=self.kwargs['pk'])
        return context


class DynamicEdition(ProyectosMenuMixin, UpdateView):
    template_name = 'proyectos/creation_form.html'

    def get_object(self):
        obj = get_object_or_404(
            self.form_class.Meta.model,
            pk=self.kwargs['pk'],
            **self.get_company_query(self.form_class.Meta.model.__name__)
        )
        return obj

    def get_initial(self):
        initial_obj = super(DynamicEdition, self).get_initial()
        initial_obj['company'] = self.request.user.currently_at
        return initial_obj

    def form_valid(self, form):
        if form.cleaned_data['company'] == self.request.user.currently_at:
            return super(DynamicEdition, self).form_valid(form)
        else:
            return super(DynamicEdition, self).form_invalid(form)


class ContratoEditView(ProyectosMenuMixin, UpdateView):
    form_class = ContratoForm
    template_name = 'proyectos/creation_form.html'

    def get_object(self):
        obj = get_object_or_404(
            Contrato,
            pk=self.kwargs['pk'],
            cliente__company=self.request.user.currently_at
        )
        return obj

    def get_initial(self):
        initial_obj = super(ContratoEditView, self).get_initial()
        initial_obj['currently_at'] = self.request.user.currently_at.company_name
        return initial_obj

    def form_valid(self, form):
        currently = form.cleaned_data.get('currently_at')
        if currently and currently == self.request.user.currently_at.company_name:
            self.object = form.save()
            return super(ContratoEditView, self).form_valid(form)
        else:
            return super(ContratoEditView, self).form_invalid(form)


class ClienteEditView(DynamicEdition):
    form_class = ClienteForm


class SitioEditView(DynamicEdition):
    form_class = SitioForm


class DestinatarioEditView(DynamicEdition):
    form_class = DestinatarioForm


class EstimateEditView(ProyectosMenuMixin, UpdateView):
    template_name = 'proyectos/estimate_form.html'
    model = Estimate

    def get_object(self, queryset=None):
        self.object = get_object_or_404(
            self.model,
            pk=self.kwargs['pk'],
            project__cliente__company=self.request.user.currently_at
        )
        return self.object

    def get_form_class(self):
        return EstimateForm

    def get_initial(self):
        init_dict = {}
        init_dict['draft_by'] = self.request.user
        init_dict['project'] = self.kwargs['pk']
        return super(EstimateEditView, self).get_initial()

    def form_valid(self, form):
        conceptformclass = estimateConceptInlineForm()
        self.conceptForm = conceptformclass(self.request.POST, instance=self.object)
        if self.conceptForm.is_valid():
            self.conceptForm.save()
            return super(EstimateEditView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(EstimateEditView, self).get_context_data(**kwargs)
        project_instance = Estimate.objects.get(pk=self.kwargs.get('pk')).project
        # concept_set_count = project_instance.concept_set.all().count()
        formset = estimateConceptInlineForm()(instance=self.object)
        image_formset_prefix = [x.nested.prefix for x in formset.forms]
        context['generator_inline_concept'] = formset
        context['image_formset_prefix'] = image_formset_prefix
        context['project_instance'] = project_instance
        return context

    def get_success_url(self):
        project_id = Estimate.objects.get(pk=self.kwargs.get('pk')).project.id
        url = reverse_lazy('proyectos:contrato_detail', kwargs={
            'pk': project_id
        })
        return url


class CatalogoConceptosInlineFormView(ProyectosMenuMixin, UpdateView):
    form_class = ContractConceptInlineForm
    template_name = 'proyectos/catalogo-conceptos-inline.html'

    def get_object(self):
        self.model = self.form_class.fk.related_model._meta.model
        obj = get_object_or_404(
            self.model,
            cliente__company=self.request.user.currently_at,
            pk=self.kwargs['pk']
        )
        return obj

    def get_success_url(self):
        return reverse(
            'construbot.proyectos:contrato_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class DynamicDelete(ProyectosMenuMixin, DeleteView):
    template_name = 'proyectos/delete.html'

    def get_object(self):
        self.model = self.model_options[self.kwargs['model']]['model']
        obj = get_object_or_404(
            self.model,
            **self.get_company_query(self.kwargs['model']),
            pk=self.kwargs['pk']
        )
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            folio = self.object.folio
        except AttributeError:
            folio = 0
        if folio:
            qs = self.model.objects.filter(**self.get_company_query(self.kwargs['model']))
            for i in qs:
                if i.folio > folio:
                    i.folio -= 1
                    i.save()
        self.object.delete()
        return JsonResponse({"exito": True})


class BaseAutocompleteView(AuthenticationTestMixin, autocomplete.Select2QuerySetView):
    app_label_name = ProyectosConfig.verbose_name


class ClienteAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Cliente.objects.filter(
                cliente_name__unaccent__icontains=self.q,
                company=self.request.user.currently_at
            )
        else:
            qs = Cliente.objects.none()
        return qs


class SitioAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Sitio.objects.filter(
                sitio_name__unaccent__icontains=self.q,
                company=self.request.user.currently_at
            )
        else:
            qs = Sitio.objects.none()
        return qs


class DestinatarioAutocomplete(BaseAutocompleteView):
    def get_queryset(self):
        if self.q:
            qs = Destinatario.objects.filter(
                destinatario_text__unaccent__icontains=self.q,
                cliente__company=self.request.user.currently_at
            )
        else:
            qs = Destinatario.objects.none()
        return qs


class UnitAutocomplete(BaseAutocompleteView):
    model = Units

    def get_key_words(self):
        self.key_words = {
            'unit__unaccent__icontains': self.q
        }
        return self.key_words

    def has_add_permission(self, request):
        return True

    def get_queryset(self):
        if self.q:
            qs = self.model.objects.filter(**self.get_key_words())
            return qs
        elif self.request.POST:
            return self.model.objects
