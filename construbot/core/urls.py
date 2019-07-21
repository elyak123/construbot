from django.conf.urls import url
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views

app_name = 'construbot.core'

urlpatterns = [
    url(
        regex=r'chunk_upload^$',
        view=views.ChunkUpload.as_view(),
        name='chunkupload'
    ),
]
