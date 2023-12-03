import requests


def get_response(url: str) -> (bool, requests.models.Response):
    try:
        return requests.get(url, timeout=1)
    except (requests.exceptions.RequestException,
            requests.exceptions.Timeout):
        return False
