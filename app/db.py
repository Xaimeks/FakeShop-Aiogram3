import psycopg2
import logging
from os import getenv
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host = getenv("DB_HOST"),
            port = getenv("DB_PORT"),
            dbname = getenv("DB_NAME"),
            user = getenv("DB_USER"),
            password = getenv("DB_PASSWORD")
        )
        return connection
    except Exception as e:
        logging.error(f"Ошибка при подключении: {e}")
        return None
