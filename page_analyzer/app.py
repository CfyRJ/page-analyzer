from flask import Flask
from flask import render_template
from flask import redirect, request
from flask import url_for
from flask import flash, get_flashed_messages

import validators
import psycopg2
import os
import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse


app = Flask(__name__)
app.secret_key = "secret_key"

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def execute_query(connect, query):
    cursor = connect.cursor()
    try:
        cursor.execute(query)
        connect.commit()
        print("Success!")
    except:
        print("Error")


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'index.html',
        input_url='',
        messages=messages)


@app.post('/urls')
def add_url():
    url = request.form.get('url')

    if not validators.url(url):
        if url == '':
            flash('URL обязателен', 'error')
        else:
            flash('Некорректный URL', 'error')

        messages = get_flashed_messages(with_categories=True)

        return render_template(
            'index.html',
            input_url=url,
            messages=messages,
        ), 422

    url = urlparse(url)
    url = f'{url.scheme}://{url.netloc}'

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO table_urls (name, created_at)
        VALUES (%s, %s);
        """,
        (url, datetime.datetime.now()))
    cur.execute("""
        SELECT id FROM table_urls
        WHERE name = %s;
        """,
        (url, ))
    id = cur.fetchone()[0]
    cur.execute("""
        SELECT * FROM table_urls
        WHERE id = %s;
        """,
        (15, ))
    url = cur.fetchone()
    cur.close()
    conn.close()

    print(url)

    return redirect(url_for('show_url', id=id), 302)


@app.get('/urls')
def show_urls():
    urls = []

    return render_template(
        'urls.html',
        urls=urls,
    )


@app.get('/url/<id>')
def show_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM table_urls
        WHERE id = %s;
        """,
        (id, ))
    url = cur.fetchone()
    cur.close()
    conn.close()
    # print(url)

    # url = {'id': url[0], 'name': url[1], 'created_at': url[2]}
    messages = ''
    checks = ''

    return render_template(
        'url.html',
        url=url,
        messages=messages,
        checks=checks,
    )


@app.route('/url/<id>/checks', methods=['post'])
def checks(id):
    id = 0

    return redirect(url_for('show_url', id = id), 302)
