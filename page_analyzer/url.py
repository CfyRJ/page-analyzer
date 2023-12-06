import requests


def get_response(url: str) -> (None, requests.models.Response):
    try:
        response = requests.get(url, timeout=1)
    except (requests.exceptions.RequestException,
            requests.exceptions.Timeout):
        return None

    if response and response.status_code == 200:
        return response

    return None
