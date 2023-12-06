import psycopg2
import psycopg2.extras


def add_urls(url: str, database_url: str) -> bool:
    conn = psycopg2.connect(database_url)
    with conn.cursor() as cur:

        try:
            cur.execute("""
                INSERT INTO urls (name)
                VALUES (%s);
                """,
                        (url,))
            conn.commit()
            res = True
        except psycopg2.Error:
            res = False

    conn.close()

    return res


def get_url_by_name(url: str, database_url: str) -> int:
    conn = psycopg2.connect(database_url)
    with conn.cursor() as cur:

        cur.execute("""
            SELECT id FROM urls
            WHERE name = %s;
            """,
                    (url, ))
        id = cur.fetchone()

    conn.close()

    return id[0] if id else 0


def get_url(id: int, database_url: str) -> dict:
    conn = psycopg2.connect(database_url)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        cur.execute("""
            SELECT * FROM urls
            WHERE id = %s;
            """,
                    (id, ))
        url = cur.fetchone()

    conn.close()

    return url


def add_url_checks(check_date: dict, database_url: str) -> bool:
    conn = psycopg2.connect(database_url)
    with conn.cursor() as cur:

        try:
            cur.execute("""
                INSERT INTO url_checks (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description)
                VALUES (%s, %s, %s, %s, %s);
                """,
                        (check_date['url_id'],
                         check_date['status_code'],
                         check_date['h1'],
                         check_date['title'],
                         check_date['description'])
                        )
            conn.commit()
            res = True
        except psycopg2.Error:
            res = False

    conn.close()

    return res


def get_checks_url(url_id: int, database_url: str) -> list:
    conn = psycopg2.connect(database_url)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        cur.execute("""SELECT * FROM url_checks
                    WHERE url_id = %s
                    ORDER BY created_at DESC;""",
                    (url_id)
                    )
        checks = cur.fetchall()

    conn.close()

    return checks


def get_url_check(database_url: str) -> list:
    conn = psycopg2.connect(database_url)
    with conn.cursor() as cur:

        cur.execute("""SELECT id, name FROM urls ORDER BY id DESC;""")
        table_urls = cur.fetchall()
        cur.execute("""SELECT
                    url_checks.url_id,
                    url_checks.created_at,
                    status_code
                       FROM url_checks JOIN (
                           SELECT url_id, MAX(created_at) AS created_at
                           FROM url_checks GROUP BY url_id) AS tab
                       ON url_checks.url_id=tab.url_id
                       AND url_checks.created_at=tab.created_at;""")
        url_checks = cur.fetchall()

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
