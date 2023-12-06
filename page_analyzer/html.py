from bs4 import BeautifulSoup


def get_check_result(response) -> dict:
    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.h1.string if soup.h1 else ''
    title = soup.title.string if soup.title else ''
    try:
        description = soup.find(attrs={"name": "description"})['content']
    except TypeError:
        description = ''

    return {'h1': h1,
            'title': title,
            'description': description
            }
