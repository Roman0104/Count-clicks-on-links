import argparse
import os

import requests
from urllib.parse import urlparse
from dotenv import load_dotenv


def shorten_link(url, token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    payload = {
        'long_url': url,
        'domain': os.getenv('BITLY_DOMAIN'),
        'group_guid': os.getenv('BITLY_GROUP_GUID'),
        'title': os.getenv('BITLY_TITLE'),
    }

    response = requests.post(
        'https://api-ssl.bitly.com/v4/bitlinks',
        headers=headers,
        json=payload
    )
    response.raise_for_status()

    return response.json()['id']


def count_clicks(url, token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    params = {
        'unit': 'month',
        'units': '-1',
    }

    response = requests.get(
        f'https://api-ssl.bitly.com/v4/bitlinks/{urlparse(url).netloc}{urlparse(url).path}/clicks/summary',
        headers=headers,
        params=params
    )
    response.raise_for_status()

    return response.json()['total_clicks']


def is_bitlink(url, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'https://api-ssl.bitly.com/v4/bitlinks/{urlparse(url).netloc}{urlparse(url).path}',
        headers=headers
    )

    if response.status_code != 200 and response.status_code != 404:
        response.raise_for_status()
    return response.ok


def main():
    load_dotenv()
    token = os.getenv('BITLY_TOKEN')
    parser = argparse.ArgumentParser(
        description="Программа создания коротких ссылок и вывода количества "
                    "переходов по короткой ссылки"
    )
    parser.add_argument("user_input", help="Ввод ссылки")
    user_input = parser.parse_args().user_input

    try:
        if is_bitlink(user_input, token):
            print(
                f'Количество переходов по ссылке битли: {count_clicks(user_input, token)}')
        else:
            print(f'Битлинк {shorten_link(user_input, token)}')
    except requests.exceptions.HTTPError:
        print('Ошибка, введена некорректная ссылка')
        return


if __name__ == '__main__':
    main()
