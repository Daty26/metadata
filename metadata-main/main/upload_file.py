import os
import subprocess

import psycopg2
from django.core.files.storage import FileSystemStorage
from django.core.serializers import json
from django.shortcuts import render


# Функция для вставки данных в PostgreSQL
def insert_file_info(filename, file_size, metadata):
    conn = psycopg2.connect(
        dbname="matadata",
        user="postgres",
        password="226029",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO uploaded_files (filename, file_size, metadata) VALUES (%s, %s, %s)",
        (filename, file_size, json.dumps(metadata))
    )
    conn.commit()
    cur.close()
    conn.close()

# Обновлённая функция загрузки файлов
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        fs = FileSystemStorage()
        file = request.FILES['file']
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)
        file_size = os.path.getsize(file_path)

        # Получаем метаданные через exiftool
        try:
            metadata_json = subprocess.run(["exiftool", "-j", file_path], capture_output=True, text=True).stdout
            metadata = json.loads(metadata_json)[0] if metadata_json else {}
        except Exception as e:
            metadata = {"error": str(e)}

        # Записываем в базу
        insert_file_info(filename, file_size, metadata)

        return render(request, 'main/upload.html', {'file_url': fs.url(filename)})

    return render(request, 'main/upload.html')

def uploaded_files(request):
    conn = psycopg2.connect(
        dbname="matadata",
        user="postgres",
        password="226029",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT filename, file_size, metadata FROM uploaded_files")
    files = cur.fetchall()
    cur.close()
    conn.close()

    return render(request, 'main/uploaded_files.html', {'files': files})
