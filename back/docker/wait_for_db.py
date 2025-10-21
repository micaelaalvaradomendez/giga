import os
import time

import psycopg2
from psycopg2 import OperationalError


DB_NAME = os.getenv("DB_NAME", "giga")
DB_USER = os.getenv("DB_USER", "giga_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))


def wait_for_postgres(timeout=60):
    start = time.time()
    while True:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
            )
            conn.close()
            print("Database is ready.")
            return
        except OperationalError as e:
            if time.time() - start > timeout:
                raise TimeoutError(f"Database not available after {timeout}s: {e}")
            time.sleep(1)


if __name__ == "__main__":
    wait_for_postgres()

