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
class CheckedProxy:
    """
    Датакласс для уже проверенного прокси;
    --------------------------------------
    .. Датакласс для проверенного прокси.
       Определяет ключи и значения, которые
       должны быть в рабочем, определенном прокси


    :param status: ``int``
        .. Статус ответа от сервера
           (от ipinfo в данном случае)

    :param proxy: ``ProxyString``
        .. Строка прокси ip:port

    :param protocol: ``Protocol``
        .. Протокол, по которому обращаемся

    :param data: ``str | dict[str, str]``
        .. ClientResponse либо любые другие данные

    :param text: ``str``
        .. Данные ответа в текстовом формате
          (можно конвертировать в json, например)
    """

    status: int
    proxy: ProxyString
    protocol: Protocol
    data: str | dict[str, str] | ClientResponse
    text: str


# Тип для обозначения прокси, которые нужно передать
Proxies = list[ProxyString | ProxyDict]

# Тип для обозначения стран (для фильтрации)
Country = list[str]

# Тип для обозначения допустимых протоколов
# (типов прокси) (для фильтрации)
Type = list[Protocol]

class ProxiesTaster:
    def __init__(
            self,
            proxies: Proxies,
            workers: int = 200,
            country: Country = [],
            ptype: Type = []
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
               задач (минимум 4)

        :param country: ``Country`` - default: []
            .. По какой стране(ам) фильтровать

        :param ptype: ``Type`` - default: []
            .. По какому типу(ам) фильтровать
        """
        self.proxies = proxies

        # Workers
        self.workers = 4
        if workers > 4:
            self.workers = round(workers / 4) + workers % 4

        # Filters
        self.country = country
        self.type = ptype

        # Defaults
        self.logger = logging
        self.prepared = []


    @staticmethod
    def get_url_protocol(protocol: Protocol) -> UrlProtocol:
        """
        Получить корректный протокол для url
        requests

        :param protocol: ``Protocol``
            .. Протокол: http, https, socks4, socks5

        :param returns: ``str``
            .. Возвращает протокол для
               url (или ошибка, если неизвестен)
        """
        if "http" in protocol:
            return protocol

        if "socks" in protocol:
            return "https"

        raise AssertionError(f"Undefined protocol {protocol}")


    @staticmethod
    def cast_to_string(prepared: list) -> list:
        """
        Преобразовать отдельные элементы
        прокси из обработанного массива (
        через prepare_results) в строки

        :param prepared: ``list``
            .. Список обработанных прокси

        :param returns: ``list``
            .. Список прокси в виде строки;
        """
        casted = []
        for proxy in prepared:
            casted.append(
                f"{proxy['protocol']}://{proxy['proxy']} {proxy['country']}"
            )

        return casted

    def set_logger(self, logger):
        """
        Установить свой логгер

        :param logger:
            .. Объект логгера

        :param returns: ``None``
            .. Ничего не возвращает
        """
        self.logger = logger


    async def except_proxy(
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
        headers = {
            "User-Agent": UserAgent().random,
            "Accept": "*/*",
            "Proxy-Connection": "Keep-Alive"
        }

        # Список ошибок, которые
        # возникают при неправильной работе
        # прокси
        except_errors = (
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

        # В зависимости от протокола, разные способ
        # использования прокси
        if protocol == "http":
            kwargs = {}
        else:
            kwargs = {
                "connector": ProxyConnector.from_url(f"{protocol}://{proxy}")
            }

        # Продолжаем проверку прокси
        async with aiohttp.ClientSession(**kwargs) as session:
            try:
                # В зависимости от протокола, разные способ
                # использования прокси
                if "connector" in kwargs:
                    getArgs = [url]
                    getKwargs = {
                        "headers": headers,
                        "timeout": 10
                    }
                else:
                    getArgs = [url]
                    getKwargs = {
                        "headers": headers,
                        "timeout": 10,
                        "proxy": f"{protocol}://{proxy}"
                    }

                # Получаем ответ от сервера
                response = await session.get(*getArgs, **getKwargs)
            except except_errors:
                # Если где-то на прошлом этапе произошла ошибка,
                # то прокси не работает
                return invalid_result
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
                # Тут примерно такая же проверка
                # Из-за того, что response.text() делает доп запрос на сервер
                # для получения данных
                try:
                    return protocol, proxy, response, await response.text()
                except except_errors:
                    # Иначе возвращаем то, что прокси не работает
                    return invalid_result

        return invalid_result


    async def check_proxy_and_define_protocol(
            self, proxy: ProxyString
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

        site = "ipinfo.io/json"

        # Генерируем 4 корутины для создания
        # 4х асинхронных запросов, которые определят

        # Запускаем 4 запроса и ожидаем ответа
        result: list[ExceptedProxy] = await asyncio.gather(
            # Типы прокси
            *[
                self.except_proxy(
                    "socks4", proxy,
                    f"{ProxiesTaster.get_url_protocol('socks4')}://{site}"
                ),
                self.except_proxy(
                    "socks5", proxy,
                    f"{ProxiesTaster.get_url_protocol('socks5')}://{site}"
                ),
                self.except_proxy(
                    "http", proxy,
                    f"{ProxiesTaster.get_url_protocol('http')}://{site}"
                ),
                self.except_proxy(
                    "https", proxy,
                    f"{ProxiesTaster.get_url_protocol('https')}://{site}"
                )
            ]
        )

        # Функция, которая конвертирует данные
        # для возврата из функции
        def get_result_data(
                protocol: Protocol,
                proxy: ProxyString,
                response: ClientResponse,
                text: str
        ):
            if response.status == 200:
                data = response
            else:
                data = {
                    "status": response.status
                }

            return {
                "status": response.status,
                "proxy": proxy,
                "protocol": protocol,
                "data": data,
                "text": text
            }

        # socks4
        if result[0][1]:
            return get_result_data(*result[0])

        # socks5
        if result[1][1]:
            return get_result_data(*result[1])

        # https
        if result[3][1]:
            return get_result_data(*result[3])

        # http
        if result[2][1]:
            return get_result_data(*result[2])

        # Если прокси не работает
        return False


    async def check_proxy(
            self,
            protocol: Protocol,
            proxy: ProxyString
    ) -> Union[bool, CheckedProxy]:
        """
        Проверяет прокси на работоспособность
        также выдает его расположение

        :param protocol: ``str``
            .. Сетевой протокол, по которому
               работает прокси: http, https, socks4, socks5

        :param proxy: ``str``
            .. Сам прокси: ip:port

        :param returns: ``False | dict[str, str]``
            .. Ответ от ipinfo.io и сам прокси
               Если не работает - False
        """

        # Проверяем прокси
        checked = await self.except_proxy(
            protocol,
            proxy,
            f"{ProxiesTaster.get_url_protocol(protocol)}://ipinfo.io/json"
        )

        # Если работает
        if checked[1]:
            if checked[2].status == 200:
                data = checked[2]
            else:
                data = {
                    "status": checked[2].status
                }

            return {
                "status": checked[2].status,
                "proxy": proxy,
                "protocol": protocol,
                "data": data,
                "text": checked[3]
            }

        # Если нет
        return False


    async def check_and_define_protocol_proxies(
            self, proxies: Proxies
    ) -> list[CheckedProxy]:
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
            if isinstance(proxy, str):
                defined = await self.check_proxy_and_define_protocol(
                    proxy
                )
            elif isinstance(proxy, dict):
                defined = await self.check_proxy(
                    proxy["protocol"], proxy["proxy"]
                )

            if defined:
                proxy = proxy["proxy"] if "proxy" in proxy else proxy
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

        try:
            remainder_proxies: int = count_proxies % count_proxies_in_worker
        except ZeroDivisionError:
            remainder_proxies = 0

        worker_proxy: Proxies = []

        # Создаем задачи (корутины)
        for proxy in self.proxies:
            worker_proxy.append(proxy)

            if len(worker_proxy) >= count_proxies_in_worker:
                if len(tasks) == self.workers - 1 and remainder_proxies:
                    worker_proxy.append(proxy)

                tasks.append(
                    self.check_and_define_protocol_proxies(
                        worker_proxy
                    )
                )
                worker_proxy = []

        return tasks


    def country_proxy_filter(self, prepared: list) -> list:
        """
        Фильтровать обработанные прокси
        (через функцию prepare_results)
        по их стране (протоколу, socks4, socks5, http...)

        :param prepared: ``list``
            .. Список обработанных прокси

        :param returns: ``list``
            .. Отфильтрованные прокси;
        """

        filtered = []
        if self.country:
            for proxy in prepared:
                if proxy['country'] and proxy['country'] in self.country:
                    filtered.append(proxy)
        else:
            return prepared

        return filtered


    def type_proxy_filter(self, prepared: list) -> list:
        """
        Фильтровать обработанные прокси
        (через функцию prepare_results)
        по их типу (протоколу, socks4, socks5, http...)

        :param prepared: ``list``
            .. Список обработанных прокси

        :param returns: ``list``
            .. Отфильтрованные прокси;
        """
        filtered = []
        if self.type:
            for proxy in prepared:
                if proxy['protocol'] in self.type:
                    filtered.append(proxy)
        else:
            return prepared

        return filtered


    async def get_excepted(self) -> list:
        """
        Получаем проверенные прокси

        :param returns: ``list``
            .. Проверенные прокси;
        """
        return await asyncio.gather(
            *self.get_tasks()
        )


    async def get_prepared(self) -> list:
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

        for proxies in await self.get_excepted():
            for proxy in proxies:
                if proxy["status"] == 200:
                    # Устанавливаем значения по
                    # умолчанию для новых параметров
                    proxy['parsed_text'] = {}
                    proxy['country'] = ''

                    # Если ошибка при получаении данных м сервиса
                    if proxy["text"]:
                        try:
                            # Parsed text
                            proxy['parsed_text'] = json.loads(
                                proxy["text"]
                            )

                            # Country
                            proxy['country'] = proxy[
                                'parsed_text'
                            ]['country']
                        except Exception:
                            # То не добавляем в список
                            continue
                    else:
                        continue

                    prepared.append(proxy)

        return prepared


    async def run(self):
        """
        Запустить проверку

        :param returns: ``None``
            .. Ничего не возвращает;
        """
        self.prepared = self.country_proxy_filter(
            self.type_proxy_filter(
                await self.get_prepared()
            )
        )


    def get(self) -> list:
        """
        Получить уже готовые, проверенные
        прокси

        :param returns: ``list``
            .. Возвращает обработанные
               прокси;
        """
        return self.prepared
