from django.db import models

# Create your models here.
from django.db import models

class UploadedFile(models.Model):
    filename = models.CharField(max_length=255, default="")  # Добавили default=""
    file_size = models.IntegerField(default=0)  # Добавили default=0
    metadata = models.JSONField()

    def __str__(self):
        return self.filename


class ImageMetadata(models.Model):
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()  # Размер файла в кБ
    width = models.IntegerField()
    height = models.IntegerField()
    x_resolution = models.IntegerField()
    y_resolution = models.IntegerField()
    encoding_process = models.CharField(max_length=255)
    resolution_unit = models.CharField(max_length=50, blank=True, null=True)
    color_subsampling = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

