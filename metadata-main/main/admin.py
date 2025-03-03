from django.contrib import admin
from .models import UploadedFile  # Импортируем модель

admin.site.register(UploadedFile)  # Регистрируем её в админке
