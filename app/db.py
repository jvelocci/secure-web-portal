import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "dbname": "company_portal_db",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def get_db_connection():
    return psycopg.connect(**DATABASE_CONFIG)
