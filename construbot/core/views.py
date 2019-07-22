from chunked_upload.views import ChunkedUploadView
from construbot.core.models import ChunkedCoreUpload


class ChunkUpload(ChunkedUploadView):
    field_name = 'id_contrato_pdf'
    model = ChunkedCoreUpload
