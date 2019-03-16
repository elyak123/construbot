
import os
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings


if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')  # pragma: no cover


app = Celery('construbot')


class CeleryConfig(AppConfig):
    name = 'construbot.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        app.config_from_object('django.conf:settings')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)

        if hasattr(settings, 'SENTRY_DSN'):
            # Celery signal registration
            import sentry_sdk
            from sentry_sdk.integrations.celery import CeleryIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration

            sentry_logging = LoggingIntegration(
                level=settings.SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
                event_level=None,  # Send no events from log messages
            )
            sentry_sdk.init(dsn=settings.SENTRY_DSN, integrations=[sentry_logging, CeleryIntegration()])


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')  # pragma: no cover
