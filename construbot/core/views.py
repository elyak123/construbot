from chunked_upload.views import ChunkedUploadView
from construbot.proyectos.forms import ContratoDummyFileForm

class ChunkUpload(ChunkedUploadView):
    def post(self, request, *args, **kwargs):
    	import pdb; pdb.set_trace()
    	return super(ChunkUpload, self).post(request, *args, **kwargs)
