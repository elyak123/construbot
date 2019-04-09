from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from django import forms
from construbot.proyectos.models import ImageEstimateConcept, Units


@receiver(post_delete, sender=ImageEstimateConcept)
def delete_generator_images(sender, instance, using, **kwargs):
    instance.image.delete(save=False)


@receiver(pre_delete, sender=Units)
def delete_unit_watcher(sender, instance, **kwargs):
    if instance.concept_set.count() > 0:
        raise forms.ValidationError(
            'No es posible eliminar debido a que tiene conceptos'
        )
