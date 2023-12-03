from bs4 import BeautifulSoup


def get_h1(response) -> (str, None):
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.h1.string if soup.h1 else ''


def get_title(response) -> (str, None):
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.title.string if soup.title else ''


def get_description(response) -> (str, None):
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        return soup.find(attrs={"name": "description"})['content']
    except TypeError:
        return ''
