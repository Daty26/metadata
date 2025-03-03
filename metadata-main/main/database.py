import psycopg2

# Подключение к PostgreSQL
conn = psycopg2.connect(
    dbname="file_uploads",
    user="postgres",  # Замени на свой логин
    password="226029",  # Замени на свой пароль
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Функция для добавления данных о загруженных файлах
def insert_file_info(filename, file_size):
    cur.execute(
        "INSERT INTO uploaded_files (filename, file_size) VALUES (%s, %s)",
        (filename, file_size)
    )
    conn.commit()

# Закрываем соединение
def close_connection():
    cur.close()
    conn.close()
