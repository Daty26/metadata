import psycopg2
from psycopg2.extras import Json  # For handling JSONB insertion
from datetime import datetime
from datetime import timezone
from dateutil.parser import isoparse
import re

def parse_datetime(date_str):
    try:
        if not date_str:
            print("The string is empty.")
            return datetime.utcnow()  # Return current UTC time for empty input

        # Replace colons in the date part (YYYY:MM:DD) with dashes (YYYY-MM-DD)
        # while ensuring not to modify the time portion
        date_str_fixed = re.sub(r"^(\d{4}):(\d{2}):(\d{2})", r"\1-\2-\3", date_str)
        print(f"Date string fixed: {date_str_fixed}")

        # Use isoparse to handle both timezone format cases
        return isoparse(date_str_fixed)

    except Exception as e:
        # Log the exception if needed for debugging
        print(f"Failed to parse date string: {date_str} - {e}")
        # Fallback to current UTC time
        return datetime.utcnow()


def metadata_to_db(metadata):
    db_config = {
        "dbname": "University",
        "user": "postgres",
        "password": "1234",
        "host": "localhost",
        "port": 5432
    }

    file_name = metadata.get("FileName", "")
    file_size = metadata.get("file_size", 0)
    file_type = metadata.get("FileType", None)
    mime_type = metadata.get("MIMEType", None)
    created_at = parse_datetime(metadata.get("CreateDate", ""))
    modified_at = parse_datetime(metadata.get("ModifyDate", ""))
    uploaded_at = datetime.now()
    metadata_json = metadata

    insert_query = """
        INSERT INTO file_metadata
        (file_name, file_size, file_type, mime_type, created_at, modified_at, uploaded_at, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # Execute the insert query
        cursor.execute(insert_query, (
            file_name,
            file_size,
            file_type,
            mime_type,
            created_at,
            modified_at,
            uploaded_at,
            Json(metadata_json)  # Insert as JSONB
        ))

        connection.commit()

        print("Metadata inserted successfully into file_metadata table.")

    except Exception as e:
        print(f"Error inserting metadata into database: {e}")

    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()
