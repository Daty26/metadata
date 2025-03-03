from django.db import models

# Create your models here.

class FileMetadata(models.Model):
    file_name = models.CharField(max_length=255)
    original_path = models.CharField(max_length=1024)
    file_size = models.BigIntegerField(null=True)
    file_type = models.CharField(max_length=100, null=True, blank=True)
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.file_name

    class Meta:
        db_table = 'main_filemetadata'
        verbose_name = 'File Metadata'
        verbose_name_plural = 'File Metadata'
