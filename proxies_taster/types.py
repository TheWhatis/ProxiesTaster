# Typing
from typing import Union
from typing import Literal

# Enum
from enum import Enum

# Dataclass
from dataclasses import dataclass

# ClientResponse
from aiohttp.client_reqrep import ClientResponse


class Protocol(Enum):
    """
    Доступные протоколы прокси

    :param HTTP: HTTP прокси
    :type HTTP: str

    :param HTTPS: HTTPS прокси
    :type HTTPS: str

    :param SOCKS4: SOCKS4 прокси
    :type SOCKS4: str

    :param SOCKS5: SOCKS5 прокси
    :type SOCKS5: str
    """
    HTTP   = 'http'
    HTTPS  = 'https'
    SOCKS4 = 'socks4'
    SOCKS5 = 'socks5'


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
