import psycopg2
import os
import datetime
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class TableUrls():
    def insert(url: str) -> bool:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO table_urls (name, created_at)
                VALUES (%s, %s);
                """,
                (url, datetime.datetime.now()))
            conn.commit()
            res = True
        except:
            res = False

        cur.close()
        conn.close()

        return res

    def select_id(url: str) -> id:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            SELECT id FROM table_urls
            WHERE name = %s;
            """,
            (url, ))
        id = cur.fetchone()[0]

        cur.close()
        conn.close()

        return id
    
    def select_url(id: int) -> dict:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM table_urls
            WHERE id = %s;
            """,
            (id, ))
        url = Url(*cur.fetchone())

        cur.close()
        conn.close()

        return url.__dict__
    
    def select_urls() -> list:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT * FROM table_urls ORDER BY id DESC;")
        urls = cur.fetchall()

        cur.close()
        conn.close()

        urls = [Url(*url).__dict__ for url in urls]

        return urls
    
    def check_url(url: str) -> bool:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT * FROM table_urls WHERE name = %s;", (url, ))
        response = True if cur.fetchone() else False

        cur.close()
        conn.close()

        return response


class Url():
    def __init__(self, id, name, created_at) -> None:
        self.id = id
        self.name = name
        self.created_at = created_at



u = TableUrls.check_url('https://ru.hexlet.ru')
print(u)