from flask import Flask
from flask import render_template
from flask import redirect, request
from flask import url_for
from flask import flash, get_flashed_messages

import validators
from urllib.parse import urlparse

from page_analyzer.database_queries import TableUrls


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
        flash('URL существует', 'error')
    else:
        TableUrls.insert(url)

    id = TableUrls.select_id(url)
    return redirect(url_for('show_url', id=id), 302)


@app.get('/urls')
def show_urls():
    urls = TableUrls.select_urls()

    return render_template(
        'urls.html',
        urls=urls,
    )


@app.get('/url/<id>')
def show_url(id):
    url = TableUrls.select_url(id)

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

    return redirect(url_for('show_url', id=id), 302)
