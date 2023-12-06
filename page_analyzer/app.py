import os

from flask import Flask
from flask import render_template
from flask import redirect, request
from flask import url_for
from flask import flash, get_flashed_messages

import validators
from urllib.parse import urlparse

from dotenv import load_dotenv

from page_analyzer import db

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

    if db.get_url_by_name(url, DATABASE_URL):
        flash('Страница уже существует', 'info')
    else:
        flash('Страница успешно добавлена', 'success')
        db.add_urls(url, DATABASE_URL)

    id = db.get_url_by_name(url, DATABASE_URL)

    return redirect(url_for('show_url', id=id), 302)


@app.get('/urls')
def show_urls():
    urls = db.get_url_check(DATABASE_URL)

    return render_template(
        'urls.html',
        urls=urls
    ), 200


@app.get('/urls/<id>')
def show_url(id):
    url = db.get_url(id, DATABASE_URL)

    messages = get_flashed_messages(with_categories=True)
    checks = db.get_checks_url(id, DATABASE_URL)

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

    db.add_url_checks({
        'url_id': url['id'],
        'status_code': status_code,
        'h1': h1,
        'title': title,
        'description': description
    }, DATABASE_URL)

    return redirect(url_for('show_url', id=id), 302)
