from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import UploadedFile
import subprocess
import json
import shutil
import os
import time

def uploaded_files(request):
    """Возвращает список загруженных файлов из базы данных."""
    files = UploadedFile.objects.all().values("id", "filename", "file_size", "metadata")
    return JsonResponse(list(files), safe=False)

def index(request):
    return render(request, 'main/index.html')

def analyze(request):
    return render(request, 'main/analyze.html')

def upload_file(request):
    """Загружает файл, анализирует его метаданные и сохраняет в БД."""
    if request.method == 'POST' and request.FILES.get('file'):
        fs = FileSystemStorage()
        file = request.FILES['file']
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        try:
            # Получаем размер файла
            file_size = os.path.getsize(file_path)

            # Получаем метаданные через ExifTool
            if not shutil.which("exiftool"):
                raise FileNotFoundError("ExifTool не найден. Убедитесь, что он установлен.")

            metadata_output = subprocess.run(["exiftool", "-j", file_path], capture_output=True, text=True).stdout
            metadata = json.loads(metadata_output)[0] if metadata_output else {}

            # Сохраняем в базу данных
            uploaded_file = UploadedFile(filename=filename, file_size=file_size, metadata=metadata)
            uploaded_file.save()

            file_url = fs.url(filename)
            return render(request, 'main/upload.html', {'file_url': file_url, 'metadata': json.dumps(metadata, indent=4, ensure_ascii=False)})

        except FileNotFoundError as e:
            return render(request, 'main/upload.html', {'error': f"Ошибка: {str(e)}"})
        except json.JSONDecodeError:
            return render(request, 'main/upload.html', {'error': "Ошибка при обработке JSON-данных. Возможно, файл не содержит метаданных."})
        except Exception as e:
            return render(request, 'main/upload.html', {'error': f"Ошибка при обработке файла: {str(e)}"})
        finally:
            # Удаляем временный файл после обработки
            if os.path.exists(file_path):
                os.remove(file_path)

    return render(request, 'main/upload.html')

def compare_metadata(metadata1, metadata2):
    """Сравнивает два JSON-объекта и возвращает различия."""
    differences = {}
    for key in set(metadata1.keys()).union(metadata2.keys()):
        value1 = metadata1.get(key, "Нет данных")
        value2 = metadata2.get(key, "Нет данных")
        if value1 != value2:
            differences[key] = {"File_1": value1, "File_2": value2}
    return differences

def compare_files(request):
    """Загружает два файла, анализирует их метаданные и сравнивает их."""
    metadata1, metadata2, differences, error = None, None, None, None
    file1_size, file2_size, file1_mtime, file2_mtime = None, None, None, None

    if request.method == 'POST' and 'file1' in request.FILES and 'file2' in request.FILES:
        fs = FileSystemStorage()
        file1 = request.FILES['file1']
        file2 = request.FILES['file2']

        file1_name = fs.save(file1.name, file1)
        file2_name = fs.save(file2.name, file2)

        file1_path = fs.path(file1_name)
        file2_path = fs.path(file2_name)

        try:
            # Получаем размер файлов
            file1_size = os.path.getsize(file1_path)
            file2_size = os.path.getsize(file2_path)

            # Получаем дату последнего изменения
            file1_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file1_path)))
            file2_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file2_path)))

            if not shutil.which("exiftool"):
                raise FileNotFoundError("ExifTool не найден. Убедитесь, что он установлен.")

            metadata1 = subprocess.run(["exiftool", "-j", file1_path], capture_output=True, text=True).stdout
            metadata2 = subprocess.run(["exiftool", "-j", file2_path], capture_output=True, text=True).stdout

            metadata1 = json.loads(metadata1)[0] if metadata1 else {}
            metadata2 = json.loads(metadata2)[0] if metadata2 else {}

            # Сравниваем метаданные
            differences = compare_metadata(metadata1, metadata2)

        except FileNotFoundError as e:
            error = f"Ошибка: {str(e)}"
        except json.JSONDecodeError:
            error = "Ошибка при обработке JSON-данных. Возможно, файлы не содержат метаданных."
        except Exception as e:
            error = f"Ошибка при обработке файлов: {str(e)}"
        finally:
            # Удаляем временные файлы
            if os.path.exists(file1_path):
                os.remove(file1_path)
            if os.path.exists(file2_path):
                os.remove(file2_path)

    return render(request, 'main/compare.html', {
        'metadata1': json.dumps(metadata1, indent=4, ensure_ascii=False) if metadata1 else None,
        'metadata2': json.dumps(metadata2, indent=4, ensure_ascii=False) if metadata2 else None,
        'differences': differences,
        'error': error,
        'file1_size': file1_size,
        'file2_size': file2_size,
        'file1_mtime': file1_mtime,
        'file2_mtime': file2_mtime
    })
