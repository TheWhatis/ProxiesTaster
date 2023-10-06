#!/usr/bin/env python

# Standarts
import json
import logging

# Asyncio
import asyncio

# types
# typing
from typing import Union
from typing import Literal

# Dataclasses
from dataclasses import dataclass
from dataclasses import asdict

# Aiohttp
from aiohttp.client_reqrep import ClientResponse

# useragent
from fake_useragent import UserAgent

# aiohttp
import aiohttp
from aiohttp_proxy import ProxyConnector

# Exceptoins
# Aiohttp_proxy exceptions
from aiohttp_proxy.errors import InvalidServerReply
from aiohttp_proxy.errors import InvalidServerVersion
from aiohttp_proxy.errors import SocksConnectionError
from aiohttp_proxy.errors import NoAcceptableAuthMethods
from aiohttp_proxy.errors import SocksError

# Aiohttp exceptions
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.client_exceptions import ServerDisconnectedError
from aiohttp.client_exceptions import ClientHttpProxyError
from aiohttp.client_exceptions import ClientOSError
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.client_exceptions import ClientPayloadError
from aiohttp.client_exceptions import InvalidURL

# My types
# Показывает какие протоколы будут использоваться
# в прокси
Protocol = Literal['http', 'https', 'socks4', 'socks5']

# Показывает какие будут использоваться
# протоколы в url адресе
UrlProtocol = Literal['http', 'https']

# Для удобства сделал свой тип
ProxyString = str

# Прокси, которые прошли проверку через exceptions
# Грубо говоря, которые уже были проверены, но не обработаны
ExceptedProxy = tuple[
    Protocol,
    Union[ProxyString, bool],
    Union[ClientResponse, bool],
    Union[str, bool]
]

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
    proxy: ProxyString

@dataclass
class CheckedProxy(ProxyDict):
    """
    Датакласс для уже проверенного прокси;
    --------------------------------------
    .. Датакласс для проверенного прокси.
       Определяет ключи и значения, которые
       должны быть в рабочем, определенном прокси


    :param status: ``int``
        .. Статус ответа от сервера
           (от ipinfo в данном случае)

    :param data: ``str | dict[str, str]``
        .. ClientResponse либо любые другие данные

    :param text: ``str``
        .. Данные ответа в текстовом формате
          (можно конвертировать в json, например)
    """

    status: int
    data: str | dict[str, str] | ClientResponse
    text: str

@dataclass
class PreparedProxy(CheckedProxy):
    """
    Датакласс для обработанного прокси

    :param parsed_response: ``dict``
        .. Распаршенный ответ

    :param country: ``str``
        .. Страна прокси
    """
    response: Union[dict, False]
    country: Union[str, False]


# Тип для обозначения прокси, которые нужно передать
Proxies = list[ProxyString | ProxyDict]

# Тип для обозначения стран (для фильтрации)
Country = list[str]

# Тип для обозначения допустимых протоколов
# (типов прокси) (для фильтрации)
Protocols = list[Protocol]

class ProxiesTaster:
    def __init__(
            self,
            proxies: Proxies,
            workers: int = 200,
            country: Country = [],
            protocols: Protocols = [
                'socks4',
                'socks5',
                'http',
                'https'
            ]
    ):
        """
        Иницилизация класса и
        передача необходимых фильтров
        и параметров

        :param self:
            .. Объект этого класса

        :param proxies: ``Proxies``
            .. Список прокси

        :param workers: ``int`` - default: 200
            .. Количество параллельных
               задач (минимум 1)

        :param country: ``Country`` - default: []
            .. По какой стране(ам) фильтровать

        :param protocols: ``Protocols`` - default: ['socks4', 'socks5', 'http', 'https']
            .. По какому протоколам фильтровать
        """
        self.proxies = proxies

        # Filters
        self.set_country(country)
        self.set_protocols(protocols)

        # Workers
        self.set_workers(workers)

        # Defaults
        self.set_logger(logging)

        # Здесь будут хранится
        # уже обработанные прокси
        self.prepared = []

        # Другие статичные значения

        # Список ошибок, которые
        # возникают при неправильной работе
        # прокси
        self.except_errors = (
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


    @staticmethod
    def get_url_protocol(protocol: Protocol) -> UrlProtocol:
        """
        Получить корректный протокол для url
        requests

        :param protocol: ``Protocol``
            .. Протокол: http, https, socks4, socks5

        :param returns: ``str``
            .. Возвращает протокол для url
        """
        return 'https' if 'socks' in protocol else protocol


    @staticmethod
    def cast_to_string(prepared: list[PreparedProxy]) -> list[PreparedProxy]:
        """
        Преобразовать отдельные элементы
        прокси из обработанного массива (
        через prepare_results) в строки

        :param prepared: ``list``
            .. Список обработанных прокси

        :param returns: ``list``
            .. Список прокси в виде строки;
        """
        return [
            f"{proxy.protocol}://{proxy.proxy} {proxy.country}"
            for proxy in prepared
        ]


    @staticmethod
    def get_headers() -> dict:
        return {
            "User-Agent": UserAgent().random,
            "Accept": "*/*",
            "Proxy-Connection": "Keep-Alive"
        }


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
        Установить "воркеров" - количество
        параллельных запросов

        В зависимости от количества
        получаемых типов (протоколов)
        будет увеличиваться/уменьшатся
        скорость работы скрипта

        Чем меньше необходимо получить
        типов (протоколов) прокси, тем
        выше скорость скрипта

        :param workers: ``int``
            .. Количество параллельных запросов
               Минимум 1

        :param returns: ``None``
            .. Ничего не возвращает;
        """
        self.workers = workers if workers else 1


    def set_country(self, country: Country):
        """
        Установить фильтр по стране

        :param country: ``Country``
            .. Какую страну(ы) включать
               на выход из проверок

        :param returns: ``None``
            .. Ничего не возвращает;
        """
        self.country = country


    def set_protocols(self, protocols: Protocols):
        """
        Установить фильтр по протоколам

        :param protocols: ``Protocols``
            .. Какой протоколы включать
               на выход из проверок

        :param returns: ``None``
            .. Ничего не возвращает;
        """
        self.protocols = protocols


    async def exc(
            self,
            protocol: Protocol,
            proxy: ProxyString,
            url: str
    ) -> ExceptedProxy:
        """
        Определить не рабочий прокси;
        -----------------------------
        .. Делает запрос через aiohttp
           и, с помощью exceptions, определяет
           что прокси рабочий или нет

        :param protocol: ``Protocol``
            .. Протокол, по которому обращаться к прокси

        :param proxy: ``ProxyString``
            .. Сам прокси

        :param url: ``str``
            .. Ссылка на ресурс, на который
               будет делаться запрос

        :param returns: ``None``
            .. This is returns
               Description;
        """
        # Заголовки
        headers = ProxiesTaster.get_headers()

        invalid_result = protocol, False, False, False

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
            return invalid_result

        # Если порт неправильный, то возвращаем ошибку
        try:
            port = int(port)
        except Exception:
            self.logger.error(f"Error converted proxy port from string to integer value. Port: '{port}'")
            return invalid_result

        # Если порт не входит в диапазон поддерживаемых
        if port >= 65535:
            self.logger.error(f"Port value '{port}' must be in range 0-65535")
            return invalid_result

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
            except self.except_errors as e:
                pass
            except AttributeError as error:
                # Выделяем определенную ошибку, которая возникает
                # при неправильной работе прокси (AttributeError) и
                # блокируем вывод исключеыния для него
                if str(error) == "'NoneType' object has no attribute 'get_extra_info'":
                    self.logger.error(error)
                    self.logger.error(f"Proxy {proxy}")
                    return invalid_result

                # Иначе просто выводим исключыение
                raise error
            else:
                try:
                    return protocol, proxy, response, await response.text()
                except self.except_errors:
                    pass

        return invalid_result


    async def check(
            self,
            proxy: ProxyString,
            protocol: Union[Protocol, False] = False
    ) -> Union[bool, CheckedProxy]:
        """
        Проверяет прокси на роботоспособность
        и определяет его сетевой протокол

        Проверка производиться перебором
        протоколов и попыткой подключения
        к ним. Автоматически проверяется
        работоспособность

        :param proxy: ``str``
            .. Сам прокси ip:port

        :param returns: ``Union[bool, CheckecProxy]``
            .. Если успешно - выдает протокол, прокси
               и расположение (результат ответа от ipinfo.io)
        """

        # Сайт который будет выдавать
        # информацию по прокси (страну, ip и т.д.)
        site = "ipinfo.io/json"

        # Функция, которая конвертирует данные
        # для возврата из функции
        async def get_result_data(protocol, proxy, site):
            # Получаем проверенный прокси
            data = await self.exc(
                protocol, proxy,
                f"{ProxiesTaster.get_url_protocol(protocol)}://{site}"
            )

            if data[1]:
                return CheckedProxy(
                    data[0],        # Protocol
                    data[1],        # Proxy
                    data[2].status, # Status
                    data[2],        # Data
                    data[3]         # Text
                )

            return False

        if not protocol:
            # Protocol in string
            if (protocol := proxy.split('://'))[0] in [
                    'socks5',
                    'socks4',
                    'http',
                    'https'
            ]:
                if protocol[0] in self.protocols:
                    if result := await get_result_data(
                            protocol[0], proxy, site
                    ):
                        return result
                    return False

            # SOCKS5
            if 'socks5' in self.protocols:
                if result := await get_result_data('socks5', proxy, site):
                    return result

            # SOCKS4
            if 'socks4' in self.protocols:
                if result := await get_result_data('socks4', proxy, site):
                    return result

            # HTTPS
            if 'https' in self.protocols:
                if result := await get_result_data('https', proxy, site):
                    return result

            # HTTP
            if 'http' in self.protocols:
                if result := await get_result_data('http', proxy, site):
                    return result
        elif protocol in self.protocols:
            if result := await get_result_data(protocol, proxy, site):
                return result

        # Если прокси не работает
        return False


    async def check_all(self, proxies: Proxies) -> list[CheckedProxy]:
        """
        Проверяет список прокси и определяет
        их протокол

        :param proxies: ``Proxies``
            .. Список прокси. Либо строка, либо словарь: {
                protocol: Protocol,
                proxy: ProxyString
            }

        :param returns: ``list[CheckedProxy]``
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


    def get_tasks(self) -> list:
        """
        Получить распределенные задачи
        по списку прокси и "воркерам"

        :param returns: ``list``
            .. Список задач;
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

        return tasks


    def country_filter(self, prepared: list) -> list:
        """
        Фильтровать обработанные прокси
        (через функцию prepare_results)
        по их стране (протоколу, socks4, socks5, http...)

        :param prepared: ``list``
            .. Список обработанных прокси

        :param returns: ``list``
            .. Отфильтрованные прокси;
        """
        # Здесь будут отфильтрованные
        # прокси
        filtered = []

        # Если вообще имеются
        # параметр для фильтрации
        if self.country:
            # Перебираем прокси
            for proxy in prepared:
                if proxy.country and proxy.country in self.country:
                    filtered.append(proxy)
        else:
            # Иначе просто возвращаем
            # неотфильтрованные значения
            return prepared

        return filtered


    async def get_excepted(self) -> list[CheckedProxy]:
        """
        Получаем проверенные прокси

        :param returns: ``list``
            .. Проверенные прокси;
        """
        # Получаем распределенные по задачам
        # прокси (по параллельным запросам)
        # и запускаем их всех
        return await asyncio.gather(
            *self.get_tasks()
        )


    async def get_prepared(self) -> list[PreparedProxy]:
        """
        Получает проверенные прокси,
        исключает те, которые не вернули
        код ответа 200, а также разворачивает
        их в удобный формат для работы

        :param returns: ``list``
            .. Возвращает прокси
               в удобном формате;
        """
        # Сортировка и доп проверка
        prepared = []

        # Перебираем пачки проверенных прокси
        for proxies in await self.get_excepted():
            # Перебираем проверенные прокси
            for proxy in proxies:
                # Если он рабочий даже без
                # авторизации и других условий,
                # то продолжаем обработку
                if proxy.status == 200:
                    # Распределяем полученные параметры
                    response = False
                    try:
                        response = json.loads(proxy.text)
                    except ValueError:
                        continue
                    finally:
                        country = False
                        if response:
                            country = response['country']

                        prepared.append(
                            PreparedProxy(
                                proxy.protocol,
                                proxy.proxy,
                                proxy.status,
                                proxy.data,
                                proxy.text,
                                response,
                                country
                            )
                        )

        return prepared


    async def run(self) -> list:
        """
        Запустить проверку

        :param returns: ``list``
            .. Возвращает обработанные прокси;
        """
        # Целиком запускем проверку, обработку и
        # фильтрацию переданных прокси
        # Устанавливаем их в свойство
        self.prepared = self.country_filter(
            await self.get_prepared()
        )

        return self.prepared


    def get(self) -> list:
        """
        Получить уже готовые, проверенные
        прокси

        :param returns: ``list``
            .. Возвращает обработанные
               прокси;
        """
        return self.prepared
