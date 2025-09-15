from contextlib import contextmanager
import psycopg


@contextmanager
def db(conn_string: str):
    conn = psycopg.connect(conn_string)
    try:
        with conn.cursor() as cur:
            yield cur
    finally:
        conn.close()
