from typing import Any
from typing import Union
from typing import Literal

from dataclasses import dataclass

from .types import WorkedProxy

from .types import Proxies
from .types import Protocol


@dataclass
class Event:
    """
    Скелет данных всех событий

    :param name: Название события
    :type name: str

    :param additional: Доп аргументы для него
    :type additional: Any
    """
    name: str


@dataclass
class Start(Event):
    """
    Скелет данных события, которое
    вызывается при начале работы
    какого-либо действия

    :param args: Распакованный список аргументов,
        передаваемых в функцию, метод
    :type args: list

    :param kwargs: Распакованный список именованных
        аргументов, передаваемых в функцию, метод
    :type kwargs: dict
    """
    args: list
    kwargs: dict


@dataclass
class Success(Event):
    """
    Скелет данных события для
    завершенной задачи
    """
    pass


@dataclass
class Error(Event):
    """
    Скелет данных события
    для ошибок

    :param message: Сообщение ошибки
    :type message: str

    :param level: Уровень ошибки: если 'not work',
        то это уровень "не работы прокси", если 'error',
        то скорее всего это ошибка передачи параметров, либо
        не сильно критические непредвиденные ошибки, а 'critical'
        уже является ошибкой, которая не совместима с работой скрипта
    :type level: Literal['default', 'error', 'critical']
    """
    message: str
    level: Literal['not work', 'error', 'critical']


@dataclass
class End(Event):
    """
    Скенет данных события окончания
    его работы

    :param result: Любой резульатат конца
        работы события
    :type result: Any
    """
    result: Any


@dataclass
class Proxy(Event):
    """
    Скелет данных любого события, которое
    будет непосредственно работать
    с каким-либо прокси

    :param protocol: Протокол прокси: HTTP, SOCKS4 и т.д.
    :type protocol: Protocol

    :param proxy: Сама строка прокси или
        уже рабочий прокси
    :type proxy: str
    """
    protocol: Protocol
    proxy: Union[str, WorkedProxy]


@dataclass
class ProxyError(Proxy, Error):
    """
    Скелет данных события ошибки при
    работе с прокси

    :param protocol: В зависимости, был ли
        передан протокол при проверке или нет,
        может быть False или название протокола
    :type protocol: Union[Protocol, False]
    """
    protocol: Union[Protocol, False]


@dataclass
class ProxySuccess(Proxy, Success):
    """
    Скелет данных события, которое вызывается
    при успешной проверке или работе
    с прокси
    """
    pass


@dataclass
class RunStart(Event):
    """
    Данные события запуска проверки
    прокси

    :param proxies: Список прокси
    :type proxies: Proxies

    :param workers: Количество "воркеров" -
        асинхронных запросов
    :type workers: int
    """
    proxies: Proxies
    workers: int


@dataclass
class RunEnd(Event):
    """
    Данные события окончания
    работы проверки прокси

    :param proxies: Список рабочих прокси
    :type proxies: list[WorkedProxy]
    """
    proxies: list[WorkedProxy]
