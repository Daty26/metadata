
# import datetime
# from pathlib import Path
import os
import magic
import json
import subprocess


# def format_file_size(size_in_bytes):
#     try:
#         # Define size units
#         units = ["Bytes", "KB", "MB", "GB", "TB"]
#         size = size_in_bytes
#         unit_index = 0
#
#         # Loop through the units and resize as appropriate
#         while size >= 1024 and unit_index < len(units) - 1:
#             size /= 1024.0
#             unit_index += 1
#
#         # Return formatted size with unit
#         return f"{size:.2f} {units[unit_index]}"
#     except Exception as e:
#         return f"Error formatting size: {str(e)}"


# def get_file_metadata(file_path):
#     try:
#         path = Path(file_path)
#         metadata = {
#             "file_name": path.name,
#             "file_size": format_file_size(path.stat().st_size),
#             "creation_time": datetime.datetime.fromtimestamp(path.stat().st_ctime),
#             "modification_time": datetime.datetime.fromtimestamp(path.stat().st_mtime),
#             "absolute_path": str(path.resolve()),
#             "file_extension": path.suffix,
#         }
#         return metadata
#     except Exception as e:
#         return {"error": str(e)}

def get_file_metadata(file_path):
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    metadata = {}

    # stat = os.stat(file_path)

    try:
        # print(metadata["file_size"])
        mime = magic.Magic(mime=True)
        metadata["mime_type"] = mime.from_file(file_path)

        result = subprocess.run(["exiftool", "-j", file_path], capture_output=True, text=True)
        if result.stdout:
            exif_data = json.loads(result.stdout)
            metadata = exif_data[0]
            metadata["file_size"] = os.path.getsize(file_path)
            # metadata['stat'] = stat
        else:
            metadata = "unknown type"
    except Exception as e:
        metadata = "unknown type"
        metadata["error_exiftool"] = str(e)

    return metadata


def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {str(e)}")
        return False

# def get_exif_metadata(file_path):
#     try:
#         result = subprocess.run(
#             ["exiftool", "-json", file_path], capture_output=True, text=True
#         )
#         metadata = json.loads(result.stdout)[0] if result.stdout else {}
#         return metadata
#     except Exception as e:
#         return {"error": str(e)}