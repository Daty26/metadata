import os
import json
import subprocess
from datetime import datetime
from django.utils.timezone import make_aware
from .models import FileMetadata

def parse_datetime(date_str):
    """
    Parse datetime string from metadata into Python datetime object
    """
    if not date_str:
        return None
        
    try:
        # Common datetime formats in metadata
        formats = [
            "%Y:%m:%d %H:%M:%S",  # Standard EXIF format
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m:%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",   # ISO format
            "%Y-%m-%dT%H:%M:%S.%f" # ISO format with microseconds
        ]
        
        for fmt in formats:
            try:
                # Parse the datetime and make it timezone-aware
                dt = datetime.strptime(date_str.split('+')[0], fmt)
                return make_aware(dt)
            except ValueError:
                continue
                
        return None
    except Exception:
        return None


def get_file_metadata(file_path):
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    try:
        # Run exiftool to get metadata in JSON format
        result = subprocess.run(
            ["exiftool", "-json", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse JSON output and get the first item (exiftool returns a list)
        metadata = json.loads(result.stdout)[0] if result.stdout else {}
        
        # Add file size
        try:
            file_size = os.path.getsize(file_path)
            metadata["FileSize"] = file_size
        except Exception as e:
            metadata["FileSize"] = 0
            
        return metadata
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error running exiftool: {e.stderr}")
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing metadata: {str(e)}")
    except Exception as e:
        raise Exception(f"Error getting metadata: {str(e)}")


def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {str(e)}")
        return False


def update_file_metadata(file_path, metadata_updates):
    """
    Update file metadata using PowerShell commands for dates
    """
    try:
        # First update non-date metadata with exiftool
        args = ['exiftool']
        args.append('-overwrite_original')
        
        # Handle each metadata field
        for key, value in metadata_updates.items():
            if value and key not in ['FileModifyDate', 'FileAccessDate', 'FileCreateDate']:
                args.extend([f'-{key}={value}'])
        
        args.append(file_path)
        
        # Run exiftool to update metadata
        result = subprocess.run(args, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Failed to update metadata: {result.stderr}")

        # Handle file system dates using PowerShell
        if any(key in metadata_updates for key in ['FileModifyDate', 'FileAccessDate', 'FileCreateDate']):
            try:
                def validate_and_format_date(date_str):
                    """Validate and format date for PowerShell"""
                    if not date_str:
                        return None
                        
                    print(f"Processing date: {date_str}")  # Debug log
                    
                    try:
                        # Try different date formats
                        date_formats = [
                            '%Y:%m:%d %H:%M:%S',  # From exiftool
                            '%Y-%m-%d %H:%M:%S',  # Standard format
                            '%m/%d/%Y, %I:%M:%S %p',  # From form input
                            '%Y-%m-%dT%H:%M:%S'  # ISO format
                        ]
                        
                        date_obj = None
                        for fmt in date_formats:
                            try:
                                # Remove timezone if present
                                clean_date = date_str.split('+')[0].strip()
                                date_obj = datetime.strptime(clean_date, fmt)
                                print(f"Successfully parsed with format: {fmt}")  # Debug log
                                break
                            except ValueError:
                                continue
                        
                        if not date_obj:
                            print(f"Failed to parse date: {date_str}")  # Debug log
                            return None
                            
                        # Ensure date is within valid range (1970-2099)
                        if date_obj.year < 1970 or date_obj.year > 2099:
                            print(f"Date out of valid range: {date_obj}")  # Debug log
                            return None
                            
                        # Format for PowerShell
                        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                        print(f"Formatted date for PowerShell: {formatted_date}")  # Debug log
                        return formatted_date
                    except Exception as e:
                        print(f"Error processing date: {str(e)}")  # Debug log
                        return None

                # Build PowerShell command with validated dates
                ps_commands = []
                
                # Map metadata fields to PowerShell properties
                date_mapping = {
                    'FileModifyDate': ('LastWriteTime', metadata_updates.get('FileModifyDate')),
                    'FileAccessDate': ('LastAccessTime', metadata_updates.get('FileAccessDate')),
                    'FileCreateDate': ('CreationTime', metadata_updates.get('FileCreateDate'))
                }

                print("\nProcessing date updates:")  # Debug log
                for meta_key, (ps_prop, date_value) in date_mapping.items():
                    print(f"\nHandling {meta_key}: {date_value}")  # Debug log
                    if date_value:
                        formatted_date = validate_and_format_date(date_value)
                        if formatted_date:
                            cmd = (
                                f"$file = Get-Item '{file_path.replace('\\', '\\\\')}' -Force; "
                                f"$file.{ps_prop} = (Get-Date '{formatted_date}')"
                            )
                            ps_commands.append(cmd)
                            print(f"Added command: {cmd}")  # Debug log

                if ps_commands:
                    # Join commands and execute
                    ps_script = "; ".join(ps_commands)
                    print(f"\nExecuting PowerShell script:\n{ps_script}")  # Debug log
                    
                    ps_result = subprocess.run(
                        ['powershell', '-NoProfile', '-Command', ps_script],
                        capture_output=True,
                        text=True
                    )
                    
                    if ps_result.returncode != 0:
                        print(f"Warning: Failed to update file system dates: {ps_result.stderr}")
                    else:
                        print("Successfully updated file system dates")

                    # Update the file dates using exiftool as well
                    date_args = ['exiftool', '-overwrite_original']
                    for meta_key, (_, date_value) in date_mapping.items():
                        if date_value:
                            date_args.extend([f'-{meta_key}={date_value}'])
                    date_args.append(file_path)
                    
                    print(f"\nUpdating dates with exiftool:\n{' '.join(date_args)}")  # Debug log
                    date_result = subprocess.run(date_args, capture_output=True, text=True)
                    if date_result.returncode != 0:
                        print(f"Warning: Failed to update exiftool dates: {date_result.stderr}")
                    else:
                        print("Successfully updated exiftool dates")

                    # Verify the changes
                    verify_cmd = f"Get-Item '{file_path.replace('\\', '\\\\')}' | Select-Object CreationTime, LastWriteTime, LastAccessTime | Format-List"
                    verify_result = subprocess.run(
                        ['powershell', '-NoProfile', '-Command', verify_cmd],
                        capture_output=True,
                        text=True
                    )
                    print("\nCurrent file dates:")
                    print(verify_result.stdout)

            except Exception as e:
                print(f"Warning: Error updating file system dates: {str(e)}")

        # Get updated metadata
        updated_metadata = get_file_metadata(file_path)
        return updated_metadata
    except Exception as e:
        raise Exception(f"Error updating file metadata: {str(e)}")


def save_metadata_to_db(file_path, metadata):
    """
    Save or update metadata in the database
    """
    try:
        # Extract basic file info
        file_name = metadata.get("FileName", "")
        file_size = metadata.get("FileSize", 0)
        file_type = metadata.get("FileType", None)
        mime_type = metadata.get("MIMEType", None)
        created_at = parse_datetime(metadata.get("CreateDate", ""))
        modified_at = parse_datetime(metadata.get("ModifyDate", ""))

        # Try to find existing record or create new one
        metadata_record, created = FileMetadata.objects.update_or_create(
            file_name=file_name,
            defaults={
                'original_path': file_path,
                'file_size': file_size,
                'file_type': file_type,
                'mime_type': mime_type,
                'created_at': created_at,
                'modified_at': modified_at,
                'metadata': metadata
            }
        )
        return metadata_record
    except Exception as e:
        raise Exception(f"Error saving to database: {str(e)}")


def get_writable_tags():
    """
    Get list of writable metadata tags from exiftool
    """
    try:
        result = subprocess.run(
            ['exiftool', '-listw'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to get writable tags: {result.stderr}")
            
        # Parse the output into categories
        tags = {}
        current_category = None
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(' writable tags:'):
                # New category
                current_category = line.replace(' writable tags:', '')
                tags[current_category] = []
            elif current_category and not line.startswith('['):
                # Add tag to current category
                tags[current_category].append(line)
                
        return tags
    except Exception as e:
        raise Exception(f"Error getting writable tags: {str(e)}")


def get_common_writable_tags():
    """
    Returns a dictionary of commonly used writable metadata tags
    """
    return {
        'Date/Time': [
            'CreateDate',
            'ModifyDate',
            'DateTimeOriginal',
            'FileModifyDate',
            'FileCreateDate',
            'FileAccessDate'
        ],
        'Document Info': [
            'Title',
            'Author',
            'Subject',
            'Keywords',
            'Comment',
            'Software'
        ],
        'Image Info': [
            'ImageDescription',
            'Make',
            'Model',
            'Artist',
            'Copyright',
            'UserComment'
        ],
        'GPS': [
            'GPSLatitude',
            'GPSLongitude',
            'GPSAltitude',
            'GPSTimeStamp',
            'GPSDateStamp'
        ],
        'Audio/Video': [
            'AudioBitrate',
            'Duration',
            'VideoFrameRate',
            'Title',
            'Artist',
            'Album',
            'Year',
            'Genre'
        ]
    }