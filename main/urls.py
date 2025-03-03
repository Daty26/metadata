from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='home'),
    path('analyze/', views.analyze, name='analyze'),
    path('upload/', views.upload_file, name='upload_file'),
    path('edit-metadata/', views.edit_metadata, name='edit_metadata'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)