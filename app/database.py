import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
# import pymysql  # Codigo Stephany

#def get_connection():
#    return pymysql.connect(
#        host="localhost",
#        user="root",
#        password="$Aec@202604@",
#        database="usuarios",
#        cursorclass=pymysql.cursors.DictCursor
#    )

load_dotenv()

def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL não encontrada no .env")

    return psycopg2.connect(
        dsn=database_url,
        cursor_factory=RealDictCursor,
    )