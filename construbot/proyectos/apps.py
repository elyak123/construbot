from django.apps import AppConfig


class ProyectosConfig(AppConfig):
    name = 'construbot.proyectos'
    verbose_name = "Proyectos"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
