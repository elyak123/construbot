from django.apps import AppConfig


class ProyectosConfig(AppConfig):
    name = 'construbot.proyectos'
    verbose_name = "Proyectos"

    def ready(self):
        from construbot.proyectos.signals import handlers
        pass
