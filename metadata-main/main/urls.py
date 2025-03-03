from django.http import JsonResponse
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('analyze/', views.analyze, name='analyze'),
    path('upload/', views.upload_file, name='upload_file'),
    path('compare/', views.compare_files, name='compare_files'),
    path('uploaded_files/', views.uploaded_files, name='uploaded_files'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
