"""Module allowing for ``python -m proxies-taster ...``."""

# Standarts
import os
import sys

# Asyncio
import asyncio

# Aiohttp
from aiohttp.client_exceptions import ClientProxyConnectionError

# args
import argparse

# Colorama
from colorama import init

# Tqdm
from tqdm import tqdm

# ProxiesTaster
from .types import Protocol
from .types import WorkedProxy
from .types import ProxiesTaster
from .events_data import Events
from .exceptions import TooManyOpenFilesError

# My logger
from proxies_parser_logger import setting_logging


args = []
bars: dict = {}
worked_proxies: list = []


def country_filter(countries: list[str]):
    """
    Фильтр по стране для прокси

    :param countries: Список доступных стран (по-умолчанию все)
    :type countries: list[str] - default: []

    :return: Возвращает функцию,
        которая будет фильтровать
    :rtype: Callable[WorkedProxy, bool]
    """
    def filt(proxy: WorkedProxy):
        if not countries:
            return True

        if not proxy.country:
            return False

        return proxy.country in countries

    return filt


def status_codes_filter(codes: list[int]):
    """
    Фильтр по кодам ответов HTTP

    :param codes: Список допустимых кодов
    :type codes: list[int]

    :return: Функция-фильтр
    :rtype: Callable[WorkedProxy, bool]
    """
    def filt(proxy: WorkedProxy):
        return True if not codes else proxy.status in codes

    return filt


def string_cast(proxy: WorkedProxy) -> str:
    """
    Преобразовывает рабочий прокси
    в строку

    :param proxy: Рабочий прокси
    :type proxy: WorkedProxy

    :return: Преобразованный в
        строку прокси
    :rtype: str
    """
    return f"{proxy.status} {proxy.url} {proxy.country}"


def parse_proxies(proxies: str) -> list[str]:
    """
    Парсим список прокси

    :param proxies: Получаем прокси, разделенные
        переводом строки или пробелом
    :type proxies: str

    :return: Возвращает распаршенный
        список прокси
    :rtype: list[str]

    **Пример работы**

    .. code-block:: python

        proxies = parse_proxies('72.195.34.59:4145 43.248.27.8:4646')
    """
    proxies = proxies.strip().split("\n")
    return list(
        set(
            sum(
                [proxy.split(
                    ',' if ',' in proxy else ' '
                ) for proxy in proxies], []
            )
        )
    )


def init_parser():
    """
    Иницилизация парсера

    :return: Возвращает иницилизированный парсер
    """
        # Основные аргументы
    # Парсим входные аргументы
    parser = argparse.ArgumentParser(
        description="Скрипт, позволяющий проверить все переданные прокси"
    )


    # Название файла, откуда получаем прокси
    parser.add_argument(
        "proxies",
        type=str,
        help="Путь до файла со списком прокси, либо просто список прокси (разделенные переводом строки или пробелом)",
        nargs='?'
    )

    # Куда сохранять рабочие и
    # сортированные прокси
    parser.add_argument(
        "--out",
        "-o",
        type=str,
        help="Путь до файла, в который необходимо записать результат"
    )

    # Куда добавлять рабочие и
    # сортированные прокси
    parser.add_argument(
        "--append",
        "-a",
        type=str,
        help="Добавить полученный результат в конец переданного файла"
    )

    # Количество асинхронных запросов
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        help="Количество \"воркеров\" - асинхронных запросов",
        default=200
    )

    # По каким протоколам фильтровать
    parser.add_argument(
        "--protocols",
        "-p",
        nargs='+',
        type=str,
        help="Фильтр по протоколам прокси (socks4, socks5 и т.д.)",
        default=[protocol.value for protocol in Protocol]
    )

    # По какой стране фильтровать
    parser.add_argument(
        "--countries",
        "-c",
        nargs='+',
        type=str,
        help="Фильтр по странам (необходимо вводить локаль: RU, EN, US и т.д.)",
        default=[]
    )

    # По каким кодам ответов
    # HTTP фильтровать
    parser.add_argument(
        "--status-codes",
        '-sc',
        nargs='+',
        type=int,
        help="Фильтр по HTTP кодам ответов от прокси (по-умолчанию все)",
        default=[]
    )

    # Файл с конфигом
    parser.add_argument(
        "--logconfig",
        "-lc",
        type=str,
        help="Путь до конфига для вывода логов",
        default="log.config.json"
    )

    # Директория куда сохранять логи
    parser.add_argument(
        "--logdir",
        "-ld",
        type=str,
        help="В какую директорию сохранять файлы логов"
    )

    # Уровень логироания
    parser.add_argument(
        "--loglevel",
        "-ll",
        type=str,
        help="Уровень вывода логов (debug, critical, info и т.д.) только для вывода в терминал (stdout)"
    )

    # Формат логов
    parser.add_argument(
        "--logformat",
        "-lf",
        type=str,
        help="log format"
    )

    # Выводить ли расширенную
    # информацию
    parser.add_argument(
        '--verbose',
        '-v',
        help='Расширенный вывод информации о работе скрипта',
        action='store_true',
        default=False
    )

    return parser


def query_yes_no(question: str, default: str|None = "yes") -> bool:
    """
    Ask a yes/no question via raw_input()
    and return their answer.

    :param question" is a string that is presented to the user.
    :type question: str

    :param default: is the presumed answer if the
        user just hits <Enter>. It must be "yes"
        (the default), "no" or None (meaning
        an answer is required of the user).
    :type default: str|None

    :return: The "answer" return value is True
        for "yes" or False for "no".
    :rtype: bool
    """
    valid = {
        "yes": True,
        "y": True,
        "ye": True,
        "да": True,
        "д": True,
        "no": False,
        "n": False,
        "нет": False,
        "не": False,
        "н": False
    }
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        try:
            choice = input(question + prompt)
        except EOFError:
            sys.stdin = open(
                'CONIN$' if sys.platform == 'win32'
                else os.ttyname(sys.stdout.fileno()), 'r'
            )

            try:
                choice = input('\r' + question + prompt)
            except EOFError:
                return False

        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please response yes/no/y/n")


def save_proxies(
        args,
        worked_proxies: list,
        interrupt: bool = False
) -> list[str]:
    """
    Получить обработанные прокси

    :return: Обработанные строки прокси
    :rtype: list[str]
    """
    proxies = list(
        map(
            string_cast, filter(
                status_codes_filter(args.status_codes), filter(
                    country_filter(args.countries), worked_proxies
                )
            )
        )
    );

    # Выводим список полученных прокси
    for proxy in proxies:
        print(proxy)

    # Сохраняем в файл
    if args.out:
        if not interrupt or query_yes_no(
            f"Save proxies into file {args.out}?"
        ):
            with open(args.out, "w", encoding="utf-8") as out:
                out.write("\n".join(proxies))

    # Добавляем в файл
    if args.append:
        if not interrupt or query_yes_no(
            f"Append passed proxies into file {args.append}?"
        ):
            with open(args.append, "a", encoding="UTF-8") as append:
                for proxy in proxies:
                    append.write("\n" + proxy)


async def main():
    """
    Основная функция;

    Запускается, если
    программа была запущена
    через терминал (а не как модуль)
    """
    # Получение глобальной переменной
    # со списком прокси
    global args
    global bars
    global worked_proxies

    # Иницилизация colorama
    init()

    # Иницилизация парсера
    parser = init_parser()

    # Получаем аргументы
    args = parser.parse_args()

    # Получаем возможный ввод из pipeline
    args.proxies = args.proxies if sys.stdin.isatty() \
        else ' '.join(sys.stdin.read().splitlines()).strip()

    if not args.proxies:
        parser.error("Argument 'proxies' is positional argument")

    # Получаем прокси из файла (если файл)
    if os.path.exists(args.proxies):
        with open(args.proxies, "r", encoding="UTF-8") as proxies_file:
            proxies = parse_proxies(proxies_file.read())
    else:
        proxies = parse_proxies(args.proxies)

    # Define log config
    logkwargs = {}
    if args.logdir:
        logkwargs["dir"] = args.logdir

    if args.loglevel:
        logkwargs["level"] = args.loglevel

    if args.logformat:
        logkwargs["format"] = args.logformat

    FLOGGER, DLOGGER = setting_logging(args.logconfig, **logkwargs)
    DLOGGER.debug(f"Parsed args: {args}")

    bars = {
        'success': tqdm(
            dynamic_ncols=True,
            desc='Success'
        ),
        'process': tqdm(
            total=len(proxies),
            dynamic_ncols=True,
            desc='Process'
        ),
    }

    DLOGGER.info('Initialization taster')
    # Объект проверяльщика прокси
    taster = ProxiesTaster(proxies)

    # Его настройки
    taster.set_workers(args.workers)
    taster.set_protocols(
        [
            Protocol(protocol)
            for protocol in args.protocols
        ]
    )

    # Установка обработчиков
    taster.on(
        Events.error, lambda event: event.message
        and not event.level == 'skipped'
        and DLOGGER.error(event.message)
    )
    taster.on(
        Events.check_error, lambda event: event.level == 'not work'
        and DLOGGER.info(f"Proxy dont work {event.proxy}"),
    )
    taster.on(
        Events.check_success, lambda event: [
            DLOGGER.info(f"Proxy work {event.proxy.proxy}"),
            DLOGGER.debug(f"Work proxy data {event.proxy}"),
            worked_proxies.append(event.proxy),
            bars['success'].update()
        ]
    )

    taster.on(
        Events.error, lambda event: event.message
        and isinstance(event.exception, ClientProxyConnectionError)
        and 'Too many open files' in event.message
        and DLOGGER.critical(
            f"{type(event.exception)} - {event.message}"
        )
    )

    taster.on(
        Events.check_end, lambda event: bars['process'].update()
    )

    # Получаем прокси, фильтруем их
    # и преобразуем в строки
    try:
        await taster.run()
    except TooManyOpenFilesError:
        for bar in bars.values():
            bar.close()
        parser.error(
            '\nThere are not enough file descriptors ' \
            + '(too many open files). The number of file ' \
            + 'descriptors should be slightly larger than ' \
            + 'the quantity of "Workers"; ' \
            + f"installed workers: {args.workers}"
        )

    for bar in bars.values():
        bar.close()


if __name__ == "__main__":
    # required_packages = {
    #     "aiohttp": find_spec('aiohttp'),
    #     "aiohttp-proxy": find_spec('aiohttp-proxy'),
    #     "fake-useragent": find_spec('fake-useragent'),
    #     "PyEventEmitter": find_spec('PyEventEmitter'),
    #     "proxes-taster": find_spec('proxies-taster')
    # }

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        for bar in bars.values():
            bar.close()

        if args and worked_proxies:
            try:
                save_proxies(args, worked_proxies, True)
            except KeyboardInterrupt:
                pass
        exit('Work is suspended. Bye-bye')

    save_proxies(args, worked_proxies)
