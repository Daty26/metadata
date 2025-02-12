from django.shortcuts import render
# from django.http import  HttpResponse
from django.core.files.storage import FileSystemStorage
from .file_upload import upload_file

# Create your views here.
def index(request):
    return render(request, 'main/index.html')
def analyze(request):
    return render(request, 'main/analyze.html')
