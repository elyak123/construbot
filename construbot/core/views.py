from chunked_upload.views import ChunkedUploadView
from construbot.proyectos.forms import ContratoDummyFileForm
from construbot.core.models import ChunkedCoreUpload


class ChunkUpload(ChunkedUploadView):
    field_name = 'id_contrato_pdf'
    model = ChunkedCoreUpload

    def post(self, request, *args, **kwargs):
        return super(ChunkUpload, self).post(request, *args, **kwargs)
