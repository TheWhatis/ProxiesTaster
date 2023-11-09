"""Скрипт для установлки пакета"""
from setuptools import setup


name = 'proxies-taster'
version = '1.2.0'

# Long description
with open('README.md', 'r') as readme:
    long_description = readme.read()

url = 'https://github.com/TheWhatis/ProxiesTaster'


if __name__ == '__main__':
    setup(
        name=name,
        version=version,

        author='Whatis',
        author_email='asdwdagwahwabe@gmail.com',

        description='Пакет для проверки прокси',

        long_description=long_description,
        long_description_content_type='text/markdown',

        license='GPL',
        platforms='any',

        url=url,
        download_url=f"{url}/dist/{name}-{version}.zip",

        packages=['proxies_taster'],
        include_package_data=True,
        install_requires=[
            'aiohttp',
            'aiohttp-proxy',
            'fake-useragent',
            'PyEventEmitter'
        ]
    )
