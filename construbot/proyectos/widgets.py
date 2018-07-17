from django import forms
from .models import Concept
from django.core.exceptions import ObjectDoesNotExist


class ConceptDummyWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        """
            esto se queda asi.... todavia no se porque, espero que se sepa con
            las pruebas de las vistas.
        """
        try:
            value_instance = Concept.objects.get(pk=value)
            self.value = value_instance
        except:
            self.value = str(Concept.objects.get(concept_text=value).id)
            widget = forms.Select(choices=(self.value,))
            return widget.render(name, self.value, attrs)
        return super(ConceptDummyWidget, self).render(name, self.value, attrs)

    def value_from_datadict(self, data, files, name):
        """
            Funcion que usa la vista, todavia para pasar los datos al render
            en algunos casos es un numero, otros es texto, se maneja deacuerdo
            a como venga.
        """
        data_name = data.get(name)
        try:
            value = str(Concept.objects.get(concept_text=data_name).id)
            return value
        except ObjectDoesNotExist:
            if isinstance(data_name, int):
                return data_name
            else:
                raise


class FileNestedWidget(forms.ClearableFileInput):
    template_name = 'proyectos/file_input.html'