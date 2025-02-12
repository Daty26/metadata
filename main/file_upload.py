from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils import delete_file, get_file_metadata


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('uploaded_file'):
        uploaded_file = request.FILES['uploaded_file']

        fs = FileSystemStorage()
        file_name = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(file_name)
        # print(get_exif_metadata(file_path))

        try:
            metadata = get_file_metadata(file_path)
            mime_type = metadata.get("mime_type", "unknown type")

            return render(request, 'main/file_uploaded.html', {
                'metadata': metadata,
                'file_type': mime_type,
            })
        finally:
            delete_file(file_path)

    return render(request, 'main/index.html')
