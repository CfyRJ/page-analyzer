import psycopg2
import psycopg2.extras
import logging


def create_connection(config: dict) -> psycopg2.extensions.connection:
    return psycopg2.connect(config['DATABASE_URL'])


def close(conn: psycopg2.extensions.connection) -> None:
    conn.close()


def add_url(conn: psycopg2.extensions.connection, url: str) -> int:
    with conn.cursor() as cur:

        try:
            cur.execute("""
                INSERT INTO urls (name)
                VALUES (%s) RETURNING id;
                """,
                        (url,))
            conn.commit()
            id = cur.fetchone()[0]
        except psycopg2.Error:
            logging.error(
                "An error occurred while adding to the database 'urls'.",
                exc_info=True)
            id = 0

    return id


def get_url_by_name(conn: psycopg2.extensions.connection, url: str) -> object:
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

        cur.execute("""
            SELECT * FROM urls
            WHERE name = %s;
            """,
                    (url, ))
        url = cur.fetchone()

    return url


def get_url(conn: psycopg2.extensions.connection, id: int) -> object:
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

        cur.execute("""
            SELECT * FROM urls
            WHERE id = %s;
            """,
                    (id, ))
        url = cur.fetchone()

    return url


def add_url_check(conn: psycopg2.extensions.connection,
                  check_date: dict) -> bool:
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
        except psycopg2.Error:
            logging.error(
                "An error occurred while adding to the database 'url_checks'.",
                exc_info=True)
            raise psycopg2.Error('Error "url_checks"', status_code=500)


def get_checks_url(conn: psycopg2.extensions.connection, url_id: int) -> object:
    with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:

        cur.execute("""SELECT * FROM url_checks
                    WHERE url_id = %s
                    ORDER BY created_at DESC;""",
                    (url_id)
                    )
        checks = cur.fetchall()

    return checks


def get_url_check(conn: psycopg2.extensions.connection) -> list:
    with conn.cursor() as cur:

        cur.execute("""SELECT id, name FROM urls ORDER BY id DESC;""")
        urls = cur.fetchall()
        cur.execute("""SELECT
                        DISTINCT ON (url_id)
                        url_id,
                        created_at,
                        status_code
                    FROM url_checks
                    ORDER BY url_id ASC, created_at DESC;""")
        url_checks = cur.fetchall()

    res = []
    for id, name in urls:
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
