from flask import Flask
from flask import render_template
from flask import redirect, request
from flask import url_for
from flask import flash, get_flashed_messages

import requests
from bs4 import BeautifulSoup

import validators
from urllib.parse import urlparse

from page_analyzer.database_queries import TableUrls
from page_analyzer.database_queries import UrlChecks
from page_analyzer.database_queries import join_table


app = Flask(__name__)
app.secret_key = "secret_key"


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

    if TableUrls.check_url(url):
        id = TableUrls.select_id(url)
        flash('Страница уже существует', 'info')
    else:
        flash('Страница успешно добавлена', 'success')
        TableUrls.insert(url)

    id = TableUrls.select_id(url)
    return redirect(url_for('show_url', id=id), 302)


@app.get('/urls')
def show_urls():
    urls = join_table()

    return render_template(
        'urls.html',
        urls=urls
    ), 200


@app.get('/urls/<id>')
def show_url(id):
    url = TableUrls.select_url(id)

    messages = get_flashed_messages(with_categories=True)
    checks = UrlChecks.select_checks_url(id)

    return render_template(
        'url.html',
        url=url,
        messages=messages,
        checks=checks,
    )


@app.route('/urls/<id>/checks', methods=['post'])
def checks(id):
    url = request.form.to_dict()

    try:
        response = requests.get(url['name'], timeout=1)
        flash('Страница успешно проверена', 'success')
    except (requests.exceptions.RequestException,
            requests.exceptions.Timeout):
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_url', id=id), 302)

    status_code = response.status_code

    if status_code != 200:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_url', id=id), 302)

    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.h1.string if soup.h1.string else ''
    title = soup.title.string if soup.title.string else ''
    try:
        description = soup.find(attrs={"name": "description"})['content']
    except TypeError:
        description = ''

    UrlChecks.insert({
        'url_id': url['id'],
        'status_code': status_code,
        'h1': h1,
        'title': title,
        'description': description
    })

    return redirect(url_for('show_url', id=id), 302)
