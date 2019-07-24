from django.db import models
from chunked_upload.models import ChunkedUpload
from chunked_upload.settings import STORAGE
from construbot.core.utils import get_directory_path


class ChunkedCoreUpload(ChunkedUpload):
    file = models.FileField(max_length=255, upload_to=get_directory_path,
                            storage=STORAGE)

    class Meta:
        verbose_name = "ChunkedCoreUpload"
        verbose_name_plural = "ChunkedCoreUploads"
