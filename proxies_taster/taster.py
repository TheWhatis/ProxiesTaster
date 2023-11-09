# Json
import json

# Union type
from typing import Any
from typing import Union
from typing import Callable

# Functools
import functools

# Asyncio
import asyncio

# Events
from event_emitter import EventEmitter

# UserAgent
from fake_useragent import UserAgent

# Aiohttp
import aiohttp
from aiohttp_proxy import ProxyConnector

# Exceptoins
# Aiohttp
from aiohttp.client_exceptions import ServerDisconnectedError
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.client_exceptions import ClientHttpProxyError
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.client_exceptions import ClientPayloadError
from aiohttp.client_exceptions import ClientOSError
from aiohttp.client_exceptions import InvalidURL

# Proxy
from aiohttp_proxy.errors import InvalidServerReply
from aiohttp_proxy.errors import InvalidServerVersion
from aiohttp_proxy.errors import SocksConnectionError
from aiohttp_proxy.errors import NoAcceptableAuthMethods
from aiohttp_proxy.errors import SocksError

# Types
from .types import Protocol
from .types import Proxies

# Dataclasses
from .types import WorkedProxy

# Events
from .events_data import Events
from .events_data import Event

from .events_data import Start
from .events_data import End
from .events_data import ProxySuccess
from .events_data import ProxyError

from .events_data import RunStart
from .events_data import RunEnd

# Exceptions
from .exceptions import TooManyOpenFilesError

def events_wrap(
        event: str,
        protocol: int,
        proxy: int,
):
    """
    Декоратор для методов ProxiesTaster
    который позволяет добавить события
    начала вызова метода, конец его работы
    и на основе ответа от него можно установить
    вызов соответстующей ошибки

    :param event: Название события, от него
        уже будут вызываться события start и end,
        например: `myevent -> myevent.start`,
        `myevent -> myevent.end` и т.д.
    :type event: str

    :param protocol: Индекс в *args аргумента,
        под которым находится протокол прокси
    :type protocol: int

    :param proxy: Индекс в *args аргумента,
        под которым находится строка прокси
    :type proxy: int

    **Пример работы**

    .. code-block:: python

        @events_wrap('myfunc')
        async def myfunc(self, protocol, proxy):
            pass

        # Или
        @events_wrap('myfunc', 1, 2)
        async def myfunc(self, protocol, proxy):
            pass
    """
    def _wrapped(func):
        def start(*args, **kwargs):
            name = event + '.start'
            args[0].emitter.emit(
                name, Start(
                    name=name,
                    args=args,
                    kwargs=kwargs
                )
            )

        def end(result, *args, **kwargs):
            end_name = event + '.end'

            if result:
                name = event + '.success'
                args[0].emitter.emit(
                    name, ProxySuccess(
                        name=name,
                        protocol=result.protocol,
                        proxy=result
                    )
                )
            else:
                name = event + '.error'
                error = ProxyError.create(
                    name=name,
                    protocol=args[protocol] if len(args) - 1 >= protocol
                    else kwargs['protocol'] if 'protocol' in kwargs
                    else False,
                    proxy=args[proxy] or kwargs['proxy'],
                    level='not work',
                    message=None
                )
                args[0].emitter.emit('error', error)
                args[0].emitter.emit(name, error)

            args[0].emitter.emit(
                end_name, End(
                    name=end_name,
                    result=result
                )
            )

        @functools.wraps(func)
        async def _async_wrapper(*args, **kwargs):
            start(*args, **kwargs)
            result = await func(*args, **kwargs)
            end(result, *args, **kwargs)
            return result

        return _async_wrapper
    return _wrapped


class ProxiesTaster:
    """
    Класс который как-раз таки
    и проверяет полученные прокси

    Для начала необходимо просто при
    иницилизации передать необходимые
    прокси:

    .. code-block:: python

        from proxies_taster import Protocol

        taster = ProxiesTaster(
            [
                '194.163.132.76:41212',
                'socks5://91.121.52.213:55348',
                ProxyDict(
                    Protocol.SOCKS4,
                    '172.104.136.161:39104'
                )
            ]
        )

    Далее можете изменить некоторые
    настройки (своё количество
    "воркеров" - количество асинхронных
    запросов, определяемые протоколы:

    .. code-block:: python

        from proxies_taster import Protocol

        taster.set_workers(2000)
        taster.set_protocols(
            [Protocol.SOCKS4, Protocol.SOCKS5]
        )

    :param errors: Список ошибок, которые возникают
        при неправильной работе прокси (список
        пропускаемых ошибок)
    :type errors: tuple
    """
    errors = (
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

        :param proxies: Список прокси
        :type proxies: Proxies
        """
        # Список прокси
        self.proxies = proxies

        # Количество асинхронных задач
        self.workers = 200
        self.semaphore = asyncio.Semaphore(self.workers)

        # Провряемые протоколы
        self.protocols: list[Protocol] = [protocol for protocol in Protocol]

        # Устанавливаем на каждый прокси
        # рандомные заголовки
        self.headers = {
            proxy: {
                "User-Agent": UserAgent().random,
                "Accept": "*/*",
                "Proxy-Connection": "Keep-Alive"
            } for proxy in proxies
        }

        # Events
        self.emitter = EventEmitter()

    def set_workers(self, workers: int):
        """
        Установить количество асинхронных
        задач "воркеров"

        :param workers: Количество асинхронных задач
        :type workers: int

        :return: Ничего не возвращает
        :rtype: None

        **Пример работы**

        .. code-block:: python

            taster.set_workers(300)
        """
        self.workers = workers if workers > 0 else 1
        self.semaphore = asyncio.Semaphore(self.workers)

    def set_protocols(
            self, protocols: Union[Protocol, list[Protocol]]
    ):
        """
        Установить определяемые
        протоколы (что-то вроде фильтра)

        :param protocols: Список определяемых протоколов:
            Protocol.HTTP, Protocol.HTTPS,
            Protocol.SOCKS4, Protocol.SOCKS5
        :type protocols: Union[list[Protocol]]

        :return: Ничего не возвращает
        :rtype: None

        **Пример работы**

        .. code-block:: python

            from proxies_taster import Protocol

            taster.set_protocols(
                [Protocol.SOCKS4, Protocol.SOCKS5]
            )
        """
        self.protocols = protocols if isinstance(
            protocols, list
        ) else [protocols]

    def on(
            self,
            event: Events,
            listener: Callable[[Event], Any]
    ):
        """
        Установить обработчик события

        :param event: Название события
        :type event: Events

        :param listener: Обработчик этого события
        :type listener: Callable[[Event], None]

        :return: Ничего не возвращает
        :rtype: None

        **Пример работы**

        .. code-block:: python

            # Подключаем enum с константами событий
            from proxies_taster.events_data import Events

            def print_data(data):
                print(data.name, data)

            # Можно установить лямбду
            taster.on(
                Events.error,
                lambda event: logger.error(event.message)
            )

            # Или функцию
            taster.on(Events.check, print_data)
        """
        self.emitter.on(event.value, listener)

    @events_wrap('except', 1, 2)
    async def exc(
            self,
            protocol: Protocol,
            proxy: str,
    ) -> Union[WorkedProxy, False]:
        """
        Делает запрос через aiohttp
        и, с помощью exceptions, определяет
        что прокси рабочий или нет

        :param protocol: Протокол, по которому обращаться к прокси
        :type protocol: Protocol

        :param proxy: Сам прокси
        :type proxy: str

        :return: Возвращает либо
            проверенный прокси, либо False
        :rtype: Union[WorkedProxy, False]

        **Пример проверки прокси**

        .. code-block:: python

            from proxies_taster import Protocol

            result = await taster.exc(
                Protocol.SOCKS4, '107.174.66.231:36626'
            )
        """
        # Обрабатываем переданный прокси
        proxy = next(iter(proxy.split('://')), 1) or proxy

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
            error = ProxyError.create(
                name='except.error',
                protocol=protocol,
                proxy=proxy,
                level='error',
                message=f"Invalid format proxy '{proxy}'"
            )
            self.emitter.emit('error', error)
            self.emitter.emit('except.error', error)

            return False

        # Если порт неправильный, то возвращаем ошибку
        try:
            port = int(port)
        except Exception:
            error = ProxyError.create(
                name='except.error',
                protocol=protocol,
                proxy=proxy,
                level='error',
                message=' '.join(
                    [
                        'Error converted proxy port from string to',
                        f"integer value. Port: '{port}'"
                    ]
                )
            )
            self.emitter.emit('error', error)
            self.emitter.emit('except.error', error)
            return False

        # Если порт не входит в диапазон поддерживаемых
        if port >= 65535:
            error = ProxyError.create(
                name='except.error',
                protocol=protocol,
                proxy=proxy,
                level='error',
                message=f"Port value '{port}' must be in range 0-65535"
            )
            self.emitter.emit('error', error)
            self.emitter.emit('except.error', error)
            return False

        # Продолжаем проверку прокси
        async with aiohttp.ClientSession(
                # В зависимости от протокола, разные способ
                # использования прокси
                **{} if protocol == Protocol.HTTP else {
                    "connector": ProxyConnector.from_url(
                        f"{protocol.value}://{proxy}"
                    )
                }
        ) as session:
            try:
                # Общие параметры для прокси
                kwargs = {
                    "headers": self.headers[proxy],
                    "timeout": 10
                }

                # Получаем ответ от сервера
                url = protocol.value
                url = 'https' if 'socks' in url else url
                url = f"{url}://ipinfo.io/json"
                response = await session.get(
                    *[url],
                    # В зависимости от протокола, разные способ
                    # использования прокси
                    **kwargs if protocol != Protocol.HTTP else {
                        **kwargs, **{
                            "proxy": f"{protocol.value}://{proxy}"
                        }
                    }
                )
            except ProxiesTaster.errors as err:
                message = str(err)
                if 'Too many open files' in message:
                    message = f"Proxy: {proxy}, " \
                        + f"Protocol: {protocol} " \
                        + '[Too many open files]'
                    raise TooManyOpenFilesError(message, err);
                error = ProxyError.create(
                    name='except.error.skipped',
                    protocol=protocol,
                    proxy=proxy,
                    level='skipped',
                    message=message,
                    exception=err
                );
                self.emitter.emit('error', error)
                self.emitter.emit('except.error', error)
                self.emitter.emit('except.error.skipped', error)
            except AttributeError as err:
                # Выделяем определенную ошибку, которая возникает
                # при неправильной работе прокси (AttributeError) и
                # блокируем вывод исключеыния для него
                if str(err) == "'NoneType' object has no attribute 'get_extra_info'":
                    error = ProxyError.create(
                        name='except.error',
                        protocol=protocol,
                        proxy=proxy,
                        level='error',
                        message=str(err),
                        exception=err
                    )
                    self.emitter.emit('error', error)
                    self.emitter.emit('except.error', error)
                    return False

                # Иначе просто выводим исключыение
                raise err
            else:
                try:
                    body = await response.text()
                except ProxiesTaster.errors:
                    pass
                else:
                    try:
                        body = json.loads(body)
                    except ValueError:
                        pass
                    finally:
                        worked = WorkedProxy(
                            url=f"{protocol.value}://{proxy}",
                            protocol=protocol,
                            proxy=proxy,
                            response=response,
                            status=response.status,
                            body=body,
                            country=body['country'] if "country" in body
                            else False
                        )
                        self.emitter.emit(
                            'except.success', ProxySuccess(
                                name='except.success',
                                protocol=protocol,
                                proxy=worked,
                            )
                        )
                        return worked
        return False

    @events_wrap('check', 2, 1)
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

        :param proxy: Сам прокси ip:port
        :type proxy: str

        :param protocol: Протокол по которому проверять прокси
        :type protocol: Union[Protocol, False]

        :return: Если успешно - выдает протокол, прокси
         и расположение (результат ответа от ipinfo.io)
        :rtype: Union[WorkedProxy, False]

        **Пример работы**

        .. code-block:: python

            from proxies_taster import Protocol

            # Обычной передачей прокси
            result = await taster.check('107.174.66.231:36626')

            # Или с указанием определенного протокола
            result = await taster.check(
                '107.174.66.231:36626', Protocol.HTTP
            )

            # Или также можно указать протокол
            # в самой строке прокси
            result = await taster.check('socks4://107.174.66.231:36626')
        """
        async with self.semaphore:
            # Если был передан протокол
            if protocol and protocol in self.protocols:
                return await self.exc(protocol, proxy)

            # Если протокол был передан в строке
            if (protocol := proxy.split('://'))[0] in [
                protocol.value for
                protocol in self.protocols
            ]:
                return await self.exc(Protocol(protocol), proxy)

            # Перебираем доступные прокси
            for protocol in self.protocols:
                if result := await self.exc(protocol, proxy):
                    return result

            # Если прокси не работает
            return False

    async def run(self) -> list[WorkedProxy]:
        """
        Запускает весь процесс проверки
        и возвращает уже рабочие прокси

        :return: Рабочие прокси
        :rtype: list[WorkedProxy]

        **Пример работы**

        .. code-block:: python

            result = await taster.run()
        """
        self.emitter.emit(
            'run.start', RunStart(
                name='run.start',
                proxies=self.proxies,
                workers=self.workers
            )
        )
        # Фильтруем и получаем
        # только рабочие прокси
        result = filter(
            None, await asyncio.gather(
                *[asyncio.ensure_future(
                    self.check(proxy)
                ) for proxy in self.proxies]
            )
        )
        self.emitter.emit(
            'run.end', RunEnd(
                name='run.end',
                proxies=result
            )
        )
        return result
