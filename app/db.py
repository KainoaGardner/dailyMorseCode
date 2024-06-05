import psycopg2
import psycopg2.pool
import os
from contextlib import contextmanager

from app.quotes import quotes

dbpool = psycopg2.pool.ThreadedConnectionPool(
    2,
    3,
    host="localhost",
    port="5432",
    dbname="flask_db",
    user="postgres",
    password="root",
)


@contextmanager
def db_cursor():
    conn = dbpool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
            conn.commit()

    except:
        conn.rollback()
        raise
    finally:
        dbpool.putconn(conn)


with db_cursor() as cur:
    cur.execute(open("app/database/makeDatabase.sql", "r").read())

    for quote in quotes:
        text = quote["quote"]
        author = quote["author"]
        cur.execute(
            f"INSERT INTO text (text,author) VALUES ('{text}','{author}') ON CONFLICT (text) DO NOTHING;"
        )
