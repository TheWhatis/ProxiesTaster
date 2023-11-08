# Typing
from typing import Any
from typing import Union
from typing import Literal

# Dataclass
from dataclasses import dataclass, field, InitVar

# Enum
from enum import Enum

# Types
from .types import WorkedProxy

from .types import Proxies
from .types import Protocol


class Events(Enum):
    """
    Набор констант с событиями,
    которые имеются в ProxiesTaster

    :param error: Общее событие ошибки,
        вызывается всегда когда возникает
        ошибка, во всех методах
    :type error: str

    :param except_: Начало работы метода `taster.exc`
    :type except_: str

    :param except_end: Окончание работы метода `taster.exc`
    :type except_end: str

    :param except_success: Успешное завершение
        работы метода `taster.exc` (прокси
        был получен)
    :type except_success: str

    :param except_error: Какая-либо ошибка при
        работе метода `taster.exc`
    :type except_error: str

    :param except_error_skipped: Пропущенная ошибка при
        работе метода `taster.exc`
    :type except_error_skipped: str

    :param check: Начало работы метода `taster.check`
    :type check: str

    :param check_end: Конец работы метода `taster.check`
    :type check_end: str

    :param check_success: Успешное завершение
        работы метода `taster.check` (прокси
        был получен)
    :type success: str

    :param check_error: Какая-либо ошибка при
        работе метода `taster.check`
    :type check_error: str
    """
    error: str          = 'error'
    except_: str        = 'except.start'
    except_end: str     = 'except.end'
    except_success: str = 'except.success'
    except_error: str   = 'except.error'
    except_error_skipped = 'except.error.skipped'
    check: str          = 'check.start'
    check_end: str      = 'check.end'
    check_success: str  = 'check.success'
    check_error: str    = 'check.error'

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
        уже является ошибкой, которая не совместима с работой
        скрипта. В тоже время 'skipped' - это ошибки, не влияющие
        на работоспособность или не работоспособность прокси.
        Это промежутночные ошибки, возникающие при работе проверки
    :type level: Literal['default', 'error', 'critical', 'skipped']
    """
    message: str
    level: Literal['not work', 'error', 'critical', 'skipped']
    exception: any

    @classmethod
    def create(cls, exception=False, **kwargs):
        return cls(exception=exception, **kwargs)

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
    protocol: Union[Protocol, False]
    proxy: Union[str, WorkedProxy]


@dataclass
class ProxyError(Proxy, Error):
    """
    Скелет данных события ошибки при
    работе с прокси
    """


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
