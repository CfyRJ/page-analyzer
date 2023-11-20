from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for


app = Flask(__name__)
app.secret_key = "secret_key"


def validate(url: str) -> bool:
    return 'hus'


@app.route('/')
def index():

    return render_template(
        'index.html',
        input_url='',
        error='')


@app.post('/urls')
def show_urls():
    url = request.form.get('url')

    error = validate(url)
    if error:
        return redirect(url_for('index')), 302

    # return redirect(url_for('urls'), 302)
