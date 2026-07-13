import os

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from the .env file")


def get_connection():
    connection = psycopg.connect(DATABASE_URL)
    register_vector(connection)
    return connection