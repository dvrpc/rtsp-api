from contextlib import contextmanager
import psycopg2


@contextmanager
def db(conn_string: str):
    conn = psycopg2.connect(conn_string)
    try:
        with conn.cursor() as cur:
            yield cur
    finally:
        conn.close()
