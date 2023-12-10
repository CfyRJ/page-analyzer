import requests
import validators
from urllib.parse import urlparse


def get_response(url: str) -> (None, requests.models.Response):
    try:
        response = requests.get(url, timeout=1)
    except (requests.exceptions.RequestException,
            requests.exceptions.Timeout):
        return None

    if response and response.status_code == 200:
        return response

    return None


def validate_url(url: str) -> list:
    errors = []

    if not url:
        return ['URL обязателен']
    if not validators.url(url):
        errors.append('Некорректный URL')
    if len(url) > 255:
        errors.append('Длина URl превышает 255 символов')

    return errors


def normalize_url(url: str) -> str:
    url = urlparse(url)
    return f'{url.scheme}://{url.netloc}'
