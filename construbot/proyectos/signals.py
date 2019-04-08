from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from construbot.proyectos.models import ImageEstimateConcept


@receiver(post_delete, sender=ImageEstimateConcept)
def delete_generator_images(sender, instance, using):
    instance.image.delete(save=False)


@receiver(post_save, sender=ImageEstimateConcept)
def save_file_size(sender, instance, created, **kwargs):
    instance.size = instance.image.size
    instance.save()
