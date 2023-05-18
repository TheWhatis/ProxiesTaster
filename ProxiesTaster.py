#!/usr/bin/env python

# Standarts
import os
import sys
import json
import select
import logging

# Asyncio
import asyncio

# args
import argparse

# types
# typing
from typing import Union
from dataclasses import dataclass
from aiohttp.client_reqrep import ClientResponse

# useragent
from fake_useragent import UserAgent

# Colorama
from colorama import init

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

# My logger
from include.logger import setting_logging, log

# My types
# Показывает какие протоколы будут использоваться
# в прокси
Protocol = Union["http", "https", "socks4", "socks5"]

# Показывает какие будут использоваться
# протоколы в url адресе
UrlProtocol = Union["http", "https"]

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


# Основной код
@log("Get url protocol")
def get_url_protocol(protocol: Protocol) -> UrlProtocol:
    """
    Получить корректный протокол для url;
    -------------------------------------
    .. Получить корректный протокол для url
       requests.


    :param protocol: ``Protocol``
        .. Протокол: http, https, socks4, socks5


    :param returns: ``str``
        .. Возвращает протокол для url (или ошибка, если неизвестен);
    """
    if "http" in protocol:
        return protocol

    if "socks" in protocol:
        return "https"

    raise AssertionError(f"Undefined protocol {protocol}")


@log("Except proxy")
async def except_proxy(
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

    DLOGGER = logging.getLogger("DLOGGER")

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
        DLOGGER.error(f"Invalid format proxy '{proxy}'")
        return invalid_result

    # Если порт неправильный, то возвращаем ошибку
    try:
        port = int(port)
    except Exception:
        DLOGGER.error(f"Error converted proxy port from string to integer value. Port: '{port}'")
        return invalid_result

    # Если порт не входит в диапазон поддерживаемых
    if port >= 65535:
        DLOGGER.error(f"Port value '{port}' must be in range 0-65535")
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
                DLOGGER.error(error)
                DLOGGER.error(f"Proxy {proxy}")
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


@log("Check proxy and define protocol (async)")
async def check_proxy_and_define_protocol(
        proxy: ProxyString
) -> Union[bool, CheckedProxy]:
    """
    Проверить прокси и определить протокол;
    ---------------------------------------
    .. Проверяет прокси на роботоспособность
       и определяет его сетевой протокол

       Проверка производиться перебором
       протоколов и попыткой подключения
       к ним. Автоматически проверяется
       работоспособность

    :param proxy: ``str``
        .. Сам прокси ip:port


    :param returns: ``bool | dict[str, str | dict]``
        .. Если успешно - выдает протокол, прокси
           и расположение (результат ответа от ipinfo.io)
    """

    site = "ipinfo.io/json"

    # Генерируем 4 корутины для создания
    # 4х асинхронных запросов, которые определят
    # тип прокси
    tasks = [
        except_proxy(
            "socks4",
            proxy,
            f"{get_url_protocol('socks4')}://{site}"
        ),
        except_proxy(
            "socks5",
            proxy,
            f"{get_url_protocol('socks5')}://{site}"
        ),
        except_proxy(
            "http",
            proxy,
            f"{get_url_protocol('http')}://{site}"
        ),
        except_proxy(
            "https",
            proxy,
            f"{get_url_protocol('https')}://{site}"
        )
    ]

    # Запускаем 4 запроса и ожидаем ответа
    result: list[ExceptedProxy] = await asyncio.gather(*tasks)

    # Функция, которая конвертирует данные
    # для возврата из функции
    def get_result_data(protocol: Protocol,
                        proxy: ProxyString,
                        response: ClientResponse,
                        text: str):

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

    # CHECKING

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


@log("Check proxy (async)")
async def check_proxy(
        protocol: Protocol,
        proxy: ProxyString
) -> Union[bool, CheckedProxy]:
    """
    Проверить прокси;
    -----------------
    .. Проверяет прокси на работоспособность
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
    checked = await except_proxy(
        protocol,
        proxy,
        f"{get_url_protocol(protocol)}://ipinfo.io/json"
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


@log("Check many proxies and defining protocols (async)")
async def check_and_define_protocol_proxies(
        proxies: Proxies
) -> list[CheckedProxy]:
    """
    Проверить и определетьи протокол прокси;
    ----------------------------------------
    .. Проверяет список прокси и определяет
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
    DLOGGER = logging.getLogger("DLOGGER")

    result = []

    for proxy in proxies:
        if isinstance(proxy, str):
            defined = await check_proxy_and_define_protocol(proxy)
        elif isinstance(proxy, dict):
            defined = await check_proxy(proxy["protocol"], proxy["proxy"])

        if defined:
            proxy = proxy["proxy"] if "proxy" in proxy else proxy
            DLOGGER.info(f"Proxy '{proxy}' work")
            DLOGGER.debug(f"Proxy '{proxy}' work data: '{defined}")
            result.append(defined)
        else:
            DLOGGER.info(f"Proxy '{proxy}' dont work")

    return result


async def main():
    """
    Основная функция;
    -----------------
    .. Запускается, если
       программа была запущена
       через терминал (а не как модуль)

    """
    # Иницилизация colorama
    init()

    # Основные аргументы
    # Парсим входные аргументы
    parser = argparse.ArgumentParser(
        description="Check proxies on connection and define it protocol"
    )

    # Название файла, откуда получаем прокси
    parser.add_argument(
        "proxies",
        type=str,
        help="path to file with proxies or just proxies (delimiter is \\n)",
        nargs="?"
    )

    # Куда сохранять рабочие и
    # сортированные прокси
    parser.add_argument(
        "--out",
        "-o",
        type=str,
        help="path to file, where put script work result"
    )

    # Куда добавлять рабочие и
    # сортированные прокси
    parser.add_argument(
        "--append",
        "-a",
        type=str,
        help="path to a file, where append to end work result by line"
    )

    # Количество асинхронных запросов
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        help="count async tasks (workers); default - 200",
        default=200
    )

    # Какую страну выделять
    parser.add_argument(
        "--country",
        "-c",
        type=str,
        help="get by country (write locale: RU, US, UA, EN...); default - ALL",
        default="ALL"
    )

    # Файл с конфигом
    parser.add_argument(
        "--logconfig",
        "-lc",
        type=str,
        help="path to log config in json format",
        default="log.config.json"
    )

    # Директория куда сохранять логи
    parser.add_argument(
        "--logdir",
        "-ld",
        type=str,
        help="log dir (which to save .log files)"
    )

    # Уровень логироания
    parser.add_argument(
        "--loglevel",
        "-ll",
        type=str,
        help="log level (debug, critical, info e.t.c.) only stdout"
    )

    # Формат логов
    parser.add_argument(
        "--logformat",
        "-lf",
        type=str,
        help="log format"
    )

    # Получаем аргументы
    args = parser.parse_args()

    # Получаем возможный ввод из pipeline
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        getted_stdin = sys.stdin.read()
    else:
        getted_stdin = ""

    # Проверяем откуда был вывод
    if not args.proxies and getted_stdin:
        args.proxies = getted_stdin
    elif not args.proxies:
        parser.error("Argument 'proxies' is positional argument")

    # Получаем прокси из файла (если файл)
    if "\n" not in args.proxies:
        if os.path.exists(args.proxies):
            with open(args.proxies, "r", encoding="UTF-8") as proxies_file:
                proxies = proxies_file.read().strip().split("\n")
        else:
            raise "Undefined list proxy or file with list proxy is not exists"
    else:
        proxies = args.proxies.strip().split("\n")

    # Define log config
    logkwargs = {}
    if args.logdir:
        logkwargs["dir"] = args.logdir

    if args.loglevel:
        logkwargs["level"] = args.loglevel

    if args.logformat:
        logkwargs["format"] = args.logformat

    FLOGGER, DLOGGER = setting_logging(args.logconfig, **logkwargs)

    # Задачи
    tasks = []

    # Вычесляем колчиество сколько каждый отдельный
    # асинхронный запрос будет проверять прокси
    count_proxies: int = len(proxies)
    count_proxies_in_worker: int = round(count_proxies / args.workers)

    DLOGGER.info(f"Configuring workers: {args.workers}")
    try:
        remainder_proxies: int = count_proxies % count_proxies_in_worker
    except ZeroDivisionError:
        remainder_proxies = 0

    worker_proxy: Proxies = []

    # Создаем задачи (корутины)
    DLOGGER.info("Generating async workers")
    for proxy in proxies:
        worker_proxy.append(proxy)

        if len(worker_proxy) >= count_proxies_in_worker:
            if len(tasks) == args.workers - 1 and remainder_proxies:
                worker_proxy.append(proxy)

            tasks.append(check_and_define_protocol_proxies(worker_proxy))
            worker_proxy = []

    # Вызываем и ошидаем выполнения задач
    DLOGGER.info("Start checking proxies")
    results = await asyncio.gather(*tasks)

    # Сортировка и доп проверка
    expand_results = []

    for result in results:
        for expanded in result:
            expand_results.append(expanded)

    DLOGGER.info("Prepare and filter checked proxies")
    valid_proxies = []
    for proxy in expand_results:
        if proxy["status"] == 200:
            # Если ошибка при получаении данных м сервиса
            if proxy["text"]:
                try:
                    proxy_country = json.loads(proxy["text"])["country"]
                except Exception:
                    # То не добавляем в список
                    continue
            else:
                continue

            str_proxy = f"{proxy['protocol']}://{proxy['proxy']}"
            str_proxy += f" {proxy_country}"

            # Получать ли все страны
            if args.country == "ALL":
                valid_proxies.append(str_proxy)
            elif proxy_country == args.country:
                valid_proxies.append(str_proxy)

            # И выводим в консоль
            DLOGGER.info(str_proxy)

    # Сохраняем в файл
    if args.out:
        DLOGGER.info(f"Write result in '{args.out}'")
        with open(args.out, "w", encoding="uTF-8") as valid_proxy:
            valid_proxy.write("\n".join(valid_proxies))

    # Добавляем в файл
    if args.append:
        DLOGGER.info(f"Append to file end result; Filename is '{args.append}'")
        with open(args.append, "a", encoding="UTF-8") as valid_proxy:
            for proxy in valid_proxies:
                valid_proxy.write("\n" + proxy)

if __name__ == "__main__":
    asyncio.run(main())
