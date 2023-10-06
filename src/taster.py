#!/usr/bin/env python

# Json
import json

# typing
from typing import Union
from typing import Literal

# Dataclasses
from dataclasses import dataclass

# logging
import logging

# Asyncio
import asyncio

# UserAgent
from fake_useragent import UserAgent

# Aiohttp
import aiohttp
from aiohttp.client_reqrep import ClientResponse
from aiohttp_proxy import ProxyConnector

# Exceptoins
# Aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.client_exceptions import ServerDisconnectedError
from aiohttp.client_exceptions import ClientHttpProxyError
from aiohttp.client_exceptions import ClientOSError
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.client_exceptions import ClientPayloadError
from aiohttp.client_exceptions import InvalidURL

# Proxy
from aiohttp_proxy.errors import InvalidServerReply
from aiohttp_proxy.errors import InvalidServerVersion
from aiohttp_proxy.errors import SocksConnectionError
from aiohttp_proxy.errors import NoAcceptableAuthMethods
from aiohttp_proxy.errors import SocksError


# Доступные протоколы
Protocol = Literal['http', 'https', 'socks4', 'socks5']


# Доступные протоколы HTTP
UrlProtocol = Literal['http', 'https']


@dataclass
class ProxyDict:
    """
    Датакласс для прокси;
    ---------------------
    .. Датакласс для прокси, когда
       передается вместе с протоклом


    :param protocol: ``Protocol``
        .. Протокол, по которому подключаться

    :param proxy: ``str``
        .. Сам прокси ip:port

    """
    protocol: Protocol
    proxy: str


@dataclass
class WorkedProxy(ProxyDict):
    """
    Класс для прокси которые
    были проверены

    :param response: ``ClientResponse``
        .. Объект ответа от сервера

    :param status: ``int``
        .. Http код ответа

    :param body: ``Union[dict, str]``
        .. Тело ответа

    :param country: ``Union[str, False]``
        .. Страна прокси
    """
    response: ClientResponse
    status: int
    body: Union[dict, str]
    country: Union[str, False]


# Тип для обозначения прокси, которые нужно передать
Proxies = list[
    Union[str, ProxyDict]
]


class ProxiesTaster:
    # Список ошибок, которые возникают
    # при неправильной работе прокси
    except_errors: tuple = (
        InvalidServerReply,
        ClientConnectorError,
        InvalidServerVersion,
        ServerDisconnectedError,
        asyncio.exceptions.TimeoutError,
        asyncio.TimeoutError,
        ConnectionResetError,
        SocksConnectionError,
        ClientHttpProxyError,
        ClientOSError,
        ClientResponseError,
        ClientPayloadError,
        NoAcceptableAuthMethods,
        SocksError,
        InvalidURL
    )

    def __init__(self, proxies: Proxies):
        """
        Иницилизация класса и
        передача необходимых фильтров
        и параметров

        :param proxies: ``Proxies``
            .. Список прокси
        """
        # Список прокси
        self.proxies = proxies

        # Количество асинхронных задач
        self.workers = 200

        # Провряемые протоколы
        self.protocols: list[Protocol] = [
            'http',
            'https',
            'socks4',
            'socks5'
        ]

        # Логгер
        self.logger = logging


    def set_logger(self, logger):
        """
        Установить свой логгер

        :param logger:
            .. Объект логгера

        :param returns: ``None``
            .. Ничего не возвращает
        """
        self.logger = logger


    def set_workers(self, workers: int):
        """
        Установить количество асинхронных
        задач "воркеров"

        :param workers: ``int``
            .. Количество асинхронных задач

        :param returns: ``None``
            .. Ничего не возвращает;
        """
        self.workers = workers if workers > 0 else 1


    def set_protocols(self, protocols: list[Protocol]):
        """
        Установить определяемые
        протоколы (что-то вроде фильтра)

        :param protocols: ``list[Protocol]``
            .. Список определяемых протоколов: http,
               https, socks4, socks5

        :param returns: ``None``
            .. Ничего не возвращает;
        """
        self.protocols = protocols


    async def exc(
            self,
            protocol: Protocol,
            proxy: str,
    ) -> Union[WorkedProxy, False]:
        """
        Делает запрос через aiohttp
        и, с помощью exceptions, определяет
        что прокси рабочий или нет

        :param protocol: ``Protocol``
            .. Протокол, по которому обращаться к прокси

        :param proxy: ``str``
            .. Сам прокси

        :param returns: ``None``
            .. This is returns
               Description;
        """
        # Заголовки
        headers = {
            "User-Agent": UserAgent().random,
            "Accept": "*/*",
            "Proxy-Connection": "Keep-Alive"
        }

        # Разделяем строку прокси, для проверки валидности
        splitted_proxy = proxy.split("@")
        len_splitted_proxy = len(splitted_proxy)

        # Если общий формат неправильный, то возвращаем ошибку
        try:
            if len_splitted_proxy == 1:
                port = splitted_proxy[0].split(":")[1]
            elif len_splitted_proxy == 2:
                port = splitted_proxy[1].split(":")[1]
        except Exception:
            self.logger.error(f"Invalid format proxy '{proxy}'")
            return False

        # Если порт неправильный, то возвращаем ошибку
        try:
            port = int(port)
        except Exception:
            self.logger.error(f"Error converted proxy port from string to integer value. Port: '{port}'")
            return False

        # Если порт не входит в диапазон поддерживаемых
        if port >= 65535:
            self.logger.error(f"Port value '{port}' must be in range 0-65535")
            return False

        # Продолжаем проверку прокси
        async with aiohttp.ClientSession(
                # В зависимости от протокола, разные способ
                # использования прокси
                **{} if protocol == 'http' else {
                    "connector": ProxyConnector.from_url(
                        f"{protocol}://{proxy}"
                    )
                }
        ) as session:
            try:
                # Общие параметры для прокси
                kwargs = {
                    "headers": headers,
                    "timeout": 10
                }

                # Получаем ответ от сервера
                url = 'https' if 'socks' in protocol else protocol
                url = f"{url}://ipinfo.io/json"
                response = await session.get(
                    *[url],
                    # В зависимости от протокола, разные способ
                    # использования прокси
                    **kwargs if protocol != 'http' else {
                        **kwargs, **{
                            "proxy": f"{protocol}://{proxy}"
                        }
                    }
                )
            except ProxiesTaster.except_errors as e:
                pass
            except AttributeError as error:
                # Выделяем определенную ошибку, которая возникает
                # при неправильной работе прокси (AttributeError) и
                # блокируем вывод исключеыния для него
                if str(error) == "'NoneType' object has no attribute 'get_extra_info'":
                    self.logger.error(error)
                    self.logger.error(f"Proxy {proxy}")
                    return False

                # Иначе просто выводим исключыение
                raise error
            else:
                try:
                    body = await response.text()
                except ProxiesTaster.except_errors:
                    pass
                else:
                    try:
                        body = json.loads(body)
                    except ValueError:
                        pass
                    finally:
                        return WorkedProxy(
                            protocol,
                            proxy,
                            response,
                            response.status,
                            body,
                            body['country'] if "country" in body else False
                        )
        return False


    async def check(
            self,
            proxy: str,
            protocol: Union[Protocol, False] = False
    ) -> Union[WorkedProxy, False]:
        """
        Проверяет прокси на роботоспособность
        и определяет его сетевой протокол

        Проверка производиться перебором
        протоколов и попыткой подключения
        к ним. Автоматически проверяется
        работоспособность

        :param proxy: ``str``
            .. Сам прокси ip:port

        :param returns: ``Union[WorkedProxy, False]``
            .. Если успешно - выдает протокол, прокси
               и расположение (результат ответа от ipinfo.io)
        """

        if not protocol:
            # Protocol in string
            if (protocol := proxy.split('://'))[0] in [
                    'socks5',
                    'socks4',
                    'http',
                    'https'
            ]:
                if protocol[0] in self.protocols:
                    if result := await self.exc(protocol[0], proxy):
                        return result
                    return False

            # SOCKS5
            if 'socks5' in self.protocols:
                if result := await self.exc('socks5', proxy):
                    return result

            # SOCKS4
            if 'socks4' in self.protocols:
                if result := await self.exc('socks4', proxy):
                    return result

            # HTTPS
            if 'https' in self.protocols:
                if result := await self.exc('https', proxy):
                    return result

            # HTTP
            if 'http' in self.protocols:
                if result := await self.exc('http', proxy):
                    return result
        elif protocol in self.protocols:
            if result := await self.exc(protocol, proxy):
                return result

        # Если прокси не работает
        return False


    async def check_all(self, proxies: Proxies) -> list[WorkedProxy]:
        """
        Проверяет список прокси b
        и определяет их протокол

        :param proxies: ``Proxies``
            .. Список прокси

        :param returns: ``list[WorkedProxy]``
            .. Возвращает готовый список прокси
               (если не нашел таких, то пустой список);
        """
        result = []

        for proxy in proxies:
            match proxy:
                case str():
                    defined = await self.check(proxy)
                case ProxyDict():
                    defined = await self.check(proxy.proxy, proxy.protocol)

            if defined:
                proxy = proxy.proxy if "proxy" in proxy else proxy
                self.logger.info(f"Proxy '{proxy}' work")
                self.logger.debug(f"Proxy '{proxy}' work data: '{defined}")
                result.append(defined)
            else:
                self.logger.info(f"Proxy '{proxy}' dont work")

        return result


    async def run(self) -> list[WorkedProxy]:
        """
        Запускает весь процесс проверки
        и возвращает уже рабочие прокси

        :param returns: ``list[WorkedProxy]``
            .. Рабочие прокси
        """
        # Задачи
        tasks = []

        # Вычесляем колчиество сколько каждый отдельный
        # асинхронный запрос будет проверять прокси
        count_proxies: int = len(self.proxies)
        count_proxies_in_worker: int = round(count_proxies / self.workers)

        # Получаем прокси которые
        # не вошли в основные списки
        # (остатки)
        remainder_proxies: int = 0
        if count_proxies_in_worker > 0:
            remainder_proxies = count_proxies % count_proxies_in_worker

        worker_proxy: Proxies = []

        # Создаем задачи (корутины)
        for proxy in self.proxies:
            worker_proxy.append(proxy)

            if len(worker_proxy) >= count_proxies_in_worker:
                if len(tasks) == self.workers - 1 and remainder_proxies:
                    match proxy:
                        case str():
                            worker_proxy.append(proxy)
                        case ProxyDict():
                            worker_proxy.append(proxy)
                        case list():
                            worker_proxy.append(ProxyDict(*proxy))
                        case dict():
                            worker_proxy.append(ProxyDict(**proxy))

                tasks.append(self.check_all(worker_proxy))
                worker_proxy = []

        # Распаковываем ответ
        return sum(
            # Фильтруем полученные пакеты
            # прокси (списки), исключая пустые
            filter(
                None, await asyncio.gather(*tasks)
            ), []
        )
