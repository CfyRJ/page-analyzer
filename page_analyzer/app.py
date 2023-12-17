import os

from flask import Flask, render_template, \
    redirect, request, url_for, \
    flash, get_flashed_messages, abort

from dotenv import load_dotenv

from page_analyzer import db
from page_analyzer import url as _url
from page_analyzer import html


app = Flask(__name__)

load_dotenv()
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
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

        for error in errors:
            flash(error, 'error')

        messages = get_flashed_messages(with_categories=True)
        app.logger.info(f'{url} URL validation error.')

        return render_template(
            'index.html',
            input_url=url,
            messages=messages,
        ), 422

    normalize_url = _url.normalize_url(url)

    conn = db.create_connection(app.config)
    url = db.get_url_by_name(conn, normalize_url)
    if url:
        flash('Страница уже существует', 'info')
        id = url.id
    else:
        id = db.add_url(conn, normalize_url)
        if id:
            app.logger.info(
                f'{url} Writing data to the database was successful.',
            )
            flash('Страница успешно добавлена', 'success')
        else:
            abort(500)

    db.close(conn)

    return redirect(url_for('show_url', id=id), 302)


@app.get('/urls')
def show_urls():
    conn = db.create_connection(app.config)
    urls = db.get_url_check(conn)
    db.close(conn)

    return render_template(
        'urls.html',
        urls=urls
    ), 200


@app.get('/urls/<id>')
def show_url(id):
    conn = db.create_connection(app.config)
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
    conn = db.create_connection(app.config)
    url = db.get_url(conn, id)

    response = _url.get_response(url.name)
    if not response:
        app.logger.info(
            f"""{url.name} An error occurred
            while requesting the response URL.""")

        flash('Произошла ошибка при проверке', 'error')

        return redirect(url_for('show_url', id=id), 302)

    status_code = response.status_code

    check_data = html.get_check_result(response)
    check_data.update({
        'url_id': id,
        'status_code': status_code,
    })

    app.logger.info(f'{url.name} The response was successfully received.')
    flash('Страница успешно проверена', 'success')

    flage = db.add_url_check(conn, check_data)
    db.close(conn)

    if flage:
        abort(500)

    return redirect(url_for('show_url', id=id), 302)


@app.errorhandler(500)
def page_500(error):
    app.logger.info('An error 500 occurred.')
    return """<h1>Internal Server Error</h1>
    <p>The server encountered an internal error and was unable
    to complete your request. Either the server is overloaded or
    there is an error in the application.</p>
    """
