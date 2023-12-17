from bs4 import BeautifulSoup


def get_check_result(response) -> dict:
    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.h1.string if soup.h1 else ''
    title = soup.title.string if soup.title else ''

    description = soup.find(attrs={"name": "description"})
    if description:
        description = description['content']
    else:
        description = ''

    return {'h1': h1,
            'title': title,
            'description': description
            }
