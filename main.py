from contextlib import contextmanager

import fastapi
import psycopg2

from api import access, frequency, gap, reliability

app = fastapi.FastAPI()


@contextmanager
def db(conn_string: str):
    conn = psycopg2.connect(conn_string)
    try:
        with conn.cursor() as cur:
            yield cur
    finally:
        conn.close()


def configure():
    configure_routing()


def configure_routing():
    app.include_router(access.router)
    app.include_router(frequency.router)
    app.include_router(gap.router)
    app.include_router(reliability.router)
