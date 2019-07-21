from chunked_upload.models import ChunkedUpload


class ChunkedCoreUpload(ChunkedUpload):

    class Meta:
        verbose_name = "ChunkedCoreUpload"
        verbose_name_plural = "ChunkedCoreUploads"
