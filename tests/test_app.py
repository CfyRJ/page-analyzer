import pytest

from page_analyzer.app import app


@pytest.fixture
def client():
    return app.test_client()


def test_index(client):
    response = client.get('/')
    print(response.data)
    assert bytes('Анализатор страниц', encoding='utf-8') in response.data
