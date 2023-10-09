"""Скрипт для установлки пакета"""

from setuptools import setup

import os
import json

version = '1.0.0'

long_description = '''Пакет который позволяет быстро проверить,
                   распределить и отсортировать переданные прокси.'''

url = 'https://github.com/TheWhatis/ProxiesTaster'


if __name__ == '__main__':
    setup(
        name = 'proxies_taster',
        version = version,

        author = 'Whatis',
        author_email = 'asdwdagwahwabe@gmail.com',

        description = 'Пакет для проверки прокси',

        long_description = long_description,
        long_description_content_type = 'text/markdown',

        url = url,
        download_url = f"{url}/archives/{version}.zip",

        packages = ['proxies_taster'],
        install_requires = [
            'aiohttp',
            'aiohttp-proxy',
            'fake-useragent',
            'PyEventEmitter'
        ]
    )
