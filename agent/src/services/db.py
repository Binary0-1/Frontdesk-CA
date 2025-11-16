import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db():
    return psycopg2.connect(
        os.getenv("DB_URL"),
        cursor_factory=RealDictCursor
    )
