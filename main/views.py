from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .file_upload import upload_file
from .utils import update_file_metadata, save_metadata_to_db, delete_file, get_writable_tags, get_common_writable_tags
import os

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def analyze(request):
    return render(request, 'main/analyze.html')

def edit_metadata(request):
    # Get the current file path from session
    file_path = request.session.get('current_file_path')
    if not file_path:
        return redirect('home')
        
    # Verify file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        # Try to find the latest uploaded file with similar name
        base_name = os.path.basename(file_path)
        base_name_without_suffix = base_name.split('_')[0]  # Get name without random suffix
        media_dir = os.path.dirname(file_path)
        
        # List all files with similar name pattern
        matching_files = [f for f in os.listdir(media_dir) 
                        if f.startswith(base_name_without_suffix) and 
                        os.path.isfile(os.path.join(media_dir, f))]
        
        if matching_files:
            # Get the most recently modified file
            latest_file = max(matching_files, 
                            key=lambda f: os.path.getmtime(os.path.join(media_dir, f)))
            file_path = os.path.join(media_dir, latest_file)
            print(f"Using latest matching file: {file_path}")
            # Update session with correct path
            request.session['current_file_path'] = file_path
        else:
            return render(request, 'main/edit_metadata.html', {
                'error_message': "File not found. Please upload the file again."
            })

    if request.method == 'POST':
        try:
            # Create a dictionary of metadata updates
            metadata_updates = {}
            for key, value in request.POST.items():
                if key.startswith('metadata_'):
                    metadata_key = key.replace('metadata_', '')
                    metadata_updates[metadata_key] = value

            print(f"Updating metadata for file: {file_path}")
            # Update the actual file metadata
            updated_metadata = update_file_metadata(file_path, metadata_updates)
            
            # Save updated metadata to database
            metadata_record = save_metadata_to_db(file_path, updated_metadata)
            
            # Update session with new metadata
            request.session['metadata'] = updated_metadata
            
            return render(request, 'main/file_uploaded.html', {
                'metadata': updated_metadata,
                'success_message': "Metadata updated successfully"
            })
        except Exception as e:
            return render(request, 'main/edit_metadata.html', {
                'metadata': request.session.get('metadata', {}),
                'error_message': f"Error updating metadata: {str(e)}"
            })
    
    # For GET requests, display the edit form
    metadata = request.session.get('metadata', {})
    writable_tags = get_common_writable_tags()
    
    # Organize metadata by categories
    organized_metadata = {}
    for category, tags in writable_tags.items():
        organized_metadata[category] = {
            tag: metadata.get(tag, '') for tag in tags
            if tag in metadata or category == 'Document Info'  # Always show document info fields
        }
    
    return render(request, 'main/edit_metadata.html', {
        'organized_metadata': organized_metadata,
        'metadata': metadata,  # Keep original metadata for reference
        'current_file': os.path.basename(file_path)  # Show current file name
    })
