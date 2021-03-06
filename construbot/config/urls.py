from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views
from construbot.users.views import UserRedirectView

urlpatterns = [
    url(r'^$', UserRedirectView.as_view(), name='home'),
]
if not settings.CONSTRUBOT_AS_LIBRARY:
    urlpatterns += [
        # Standalone allauth configuration
        # User management
        url(r'^accounts/', include('construbot.account_config.urls')),
        # Django Admin, use {% url 'admin:index' %}
        url(settings.ADMIN_URL, admin.site.urls),
    ]

urlpatterns += [
    # Your stuff: custom urls includes go here
    url(r'^proyectos/', include('construbot.proyectos.urls', namespace='proyectos')),
    # In-app user management
    url(r'^users/', include('construbot.users.urls', namespace='users')),
    # REST API
    url(r'^api/v1/', include('construbot.api.urls', namespace='api')),

    url(r'^core/', include('construbot.core.urls', namespace='core')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and not settings.CONSTRUBOT_AS_LIBRARY:  # pragma: no cover
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
