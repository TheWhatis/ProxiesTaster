# Typing
from typing import Union
from typing import Literal

# ClientResponse
from aiohttp.client_reqrep import ClientResponse

# Dataclass
from dataclasses import dataclass


Protocol: type = Literal['http', 'https', 'socks4', 'socks5']
"""Доступные протоколы для Прокси"""


@dataclass
class ProxyDict:
    """
    Датакласс для прокси, когда
    передается вместе с протоклом

    :param protocol: Протокол, по которому подключаться
    :type protocol: Protocol

    :param proxy: Сам прокси ip:port
    :type proxy: str
    """
    protocol: Protocol
    proxy: str


@dataclass
class WorkedProxy(ProxyDict):
    """
    Класс для прокси которые
    были проверены

    :param url: Ссылка на прокси
    :type url: str

    :param response: Объект ответа от сервера
    :type response: ClientResponse

    :param status: Http код ответа
    :type status: int

    :param body: Тело ответа
    :type body: Union[dict, str]

    :param country: Страна прокси
    :type country: Union[str, False]
    """
    url: str
    response: ClientResponse
    status: int
    body: Union[dict, str]
    country: Union[str, False]


Proxies: type = list[Union[str, ProxyDict]]
"""Тип данных обозначающий в каком формате
передавать прокси для их проверки и обработки"""
