import validators
from urllib.parse import urlparse


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
