import psycopg2
import os
import datetime
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class Url():
    def __init__(self, id, name, created_at) -> None:
        self.id = id
        self.name = name
        self.created_at = created_at


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
        except psycopg2.Error:
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


class UrlChecks:
    def insert(check_date: dict) -> bool:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO url_checks (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        created_at)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                        (check_date['url_id'],
                         check_date['status_code'],
                         check_date['h1'],
                         check_date['title'],
                         check_date['description'],
                         datetime.datetime.now())
                        )
            conn.commit()
            res = True
        except psycopg2.Error:
            res = False

        cur.close()
        conn.close()

        return res

    @classmethod
    def select_checks_url(cls, url_id: int) -> list:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""SELECT * FROM url_checks
                    WHERE url_id = %s
                    ORDER BY created_at DESC;""",
                    (url_id)
                    )
        checks = cur.fetchall()

        cur.close()
        conn.close()

        checks = [cls.make_check(check) for check in checks]

        return checks

    def make_check(check: list) -> dict:
        return {'id': check[0],
                'url_id': check[1],
                'status_code': check[2],
                'h1': check[3],
                'title': check[4],
                'description': check[5],
                'data': check[6]}


def join_table() -> list:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""SELECT id, name FROM table_urls ORDER BY id DESC;""")
    table_urls = cur.fetchall()
    cur.execute("""SELECT url_checks.url_id, url_checks.created_at, status_code
                   FROM url_checks JOIN (
                       SELECT url_id, MAX(created_at) AS created_at
                       FROM url_checks GROUP BY url_id) AS tab
                   ON url_checks.url_id=tab.url_id
                   AND url_checks.created_at=tab.created_at;""")
    url_checks = cur.fetchall()

    cur.close()
    conn.close()

    res = []
    for id, name in table_urls:
        for url_id, created_at, status_code in url_checks:
            if id == url_id:
                res.append({'id': id,
                            'name': name,
                            'last_data': created_at,
                            'status_code': status_code})
                break
        else:
            res.append({'id': id,
                        'name': name,
                        'last_data': '',
                        'status_code': ''})
    return res
