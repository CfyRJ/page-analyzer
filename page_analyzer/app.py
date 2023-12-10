import os

from flask import Flask
from flask import render_template
from flask import redirect, request
from flask import url_for
from flask import flash, get_flashed_messages

from dotenv import load_dotenv

from page_analyzer import db
from page_analyzer import url as _url
from page_analyzer.html import get_check_result


app = Flask(__name__)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'index.html',
        messages=messages)


@app.post('/urls')
def add_url():
    url = request.form.get('url')
    errors = _url.validate_url(url)

    if errors:

        for i in errors:
            flash(i, 'error')

        messages = get_flashed_messages(with_categories=True)

        return render_template(
            'index.html',
            input_url=url,
            messages=messages,
        ), 422

    url_input = _url.normalize_url(url)

    conn = db.create_connection(DATABASE_URL)
    url = db.get_url_by_name(conn, url_input)
    if url:
        flash('Страница уже существует', 'info')
        id = url.id
    else:
        id, message = db.add_url(conn, url_input)
        flash(*message)

    db.close(conn)

    return redirect(url_for('show_url', id=id), 302)


@app.get('/urls')
def show_urls():
    conn = db.create_connection(DATABASE_URL)
    urls = db.get_url_check(conn)
    db.close(conn)

    return render_template(
        'urls.html',
        urls=urls
    ), 200


@app.get('/urls/<id>')
def show_url(id):
    conn = db.create_connection(DATABASE_URL)
    url = db.get_url(conn, id)
    checks = db.get_checks_url(conn, id)
    db.close(conn)

    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'url.html',
        url=url,
        messages=messages,
        checks=checks,
    )


@app.route('/urls/<id>/checks', methods=['post'])
def checks(id):
    url = request.form.to_dict()

    response = _url.get_response(url['name'])
    if not response:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_url', id=id), 302)

    status_code = response.status_code

    check_data = get_check_result(response)
    check_data.update({
        'url_id': url['id'],
        'status_code': status_code,
    })

    flash('Страница успешно проверена', 'success')

    conn = db.create_connection(DATABASE_URL)
    db.add_url_check(conn, check_data)
    db.close(conn)

    return redirect(url_for('show_url', id=id), 302)
