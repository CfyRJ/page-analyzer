import os

from flask import Flask
from flask import render_template
from flask import redirect, request
from flask import url_for
from flask import flash, get_flashed_messages

import validators
from urllib.parse import urlparse

from dotenv import load_dotenv

from page_analyzer.database_queries import insert_urls
from page_analyzer.database_queries import select_url
from page_analyzer.database_queries import select_url_by_name
from page_analyzer.database_queries import insert_url_checks
from page_analyzer.database_queries import select_checks_url
from page_analyzer.database_queries import join_table

from page_analyzer.work_url import get_response

from page_analyzer.work_html import get_h1
from page_analyzer.work_html import get_title
from page_analyzer.work_html import get_description


app = Flask(__name__)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


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
        message = 'URL обязателен' \
            if url == '' \
            else 'Некорректный URL'

        flash(message, 'error')
        messages = get_flashed_messages(with_categories=True)

        return render_template(
            'index.html',
            input_url=url,
            messages=messages,
        ), 422

    url = urlparse(url)
    url = f'{url.scheme}://{url.netloc}'

    if select_url_by_name(url, DATABASE_URL):
        flash('Страница уже существует', 'info')
    else:
        flash('Страница успешно добавлена', 'success')
        insert_urls(url, DATABASE_URL)

    id = select_url_by_name(url, DATABASE_URL)

    return redirect(url_for('show_url', id=id), 302)


@app.get('/urls')
def show_urls():
    urls = join_table(DATABASE_URL)

    return render_template(
        'urls.html',
        urls=urls
    ), 200


@app.get('/urls/<id>')
def show_url(id):
    url = select_url(id, DATABASE_URL)

    messages = get_flashed_messages(with_categories=True)
    checks = select_checks_url(id, DATABASE_URL)

    return render_template(
        'url.html',
        url=url,
        messages=messages,
        checks=checks,
    )


@app.route('/urls/<id>/checks', methods=['post'])
def checks(id):
    url = request.form.to_dict()

    response = get_response(url['name'])
    if not response:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_url', id=id), 302)

    status_code = response.status_code
    if status_code != 200:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_url', id=id), 302)

    h1 = get_h1(response)
    title = get_title(response)
    description = get_description(response)

    flash('Страница успешно проверена', 'success')

    insert_url_checks({
        'url_id': url['id'],
        'status_code': status_code,
        'h1': h1,
        'title': title,
        'description': description
    }, DATABASE_URL)

    return redirect(url_for('show_url', id=id), 302)
