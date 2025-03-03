from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils import get_file_metadata, save_metadata_to_db, delete_file
import os

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('uploaded_file'):
        uploaded_file = request.FILES['uploaded_file']
        fs = FileSystemStorage()
        file_name = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(file_name)

        try:
            # Get metadata as dictionary
            metadata = get_file_metadata(file_path)
            
            # Save metadata to database
            metadata_record = save_metadata_to_db(file_path, metadata)
            
            # Store file path and metadata in session
            request.session['current_file_path'] = file_path
            request.session['metadata'] = metadata
            
            return render(request, 'main/file_uploaded.html', {
                'metadata': metadata,
                'file_type': metadata.get('FileType', 'unknown type'),
                'success_message': "File uploaded and metadata saved successfully."
            })
        except Exception as e:
            if file_path and os.path.exists(file_path):
                delete_file(file_path)
            return render(request, 'main/file_uploaded.html', {
                'error_message': f"Error processing file: {str(e)}"
            })

    return render(request, 'main/index.html')
