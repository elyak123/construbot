from django.db.models.signals import post_delete
from django.dispatch import receiver
from construbot.proyectos.models import ImageEstimateConcept


@receiver(post_delete, sender=ImageEstimateConcept)
def delete_generator_images(sender, instance, using, **kwargs):
    instance.image.delete(save=False)
