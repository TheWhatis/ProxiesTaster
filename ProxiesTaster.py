#!/usr/bin/env python

# Standarts
import os
import sys
import json
import select

# Asyncio
import asyncio

# args
import argparse

# Colorama
from colorama import init

# ProxiesTaster
from src.taster import ProxiesTaster
from src.taster import WorkedProxy

# My logger
from src.logger import setting_logging


def country_filter(countries: list[str]):
    """
    Фильтр по стране для прокси

    :param countries: ``list[str]`` - default: []
        .. Список доступных стран (по-умолчанию все)

    :param returns: ``Callable[WorkedProxy, bool]``
        .. Возвращает функцию, которая
           будет фильтровать
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

    :param codes: ``list[int]``
        .. Список допустимых кодов

    :param returns: ``Callable[WorkedProxy, bool]``
        .. Функция-фильтр;
    """
    def filt(proxy: WorkedProxy):
        return True if not codes else proxy.status in codes

    return filt


def string_cast(proxy: WorkedProxy) -> str:
    """
    Преобразовывает рабочий прокси
    в строку

    :param proxy: ``WorkedProxy``
        .. Рабочий прокси

    :param returns: ``str``
        .. Преобразованный в
           строку прокси
    """
    return f"{proxy.status} {proxy.protocol}://{proxy.proxy} {proxy.country}"


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

    # По каким протоколам фильтровать
    parser.add_argument(
        "--protocols",
        "-p",
        nargs='+',
        type=str,
        help="get by protocol (default - (ALL))",
        default=[
            'socks5',
            'socks4',
            'https',
            'http'
        ]
    )

    # По какой стране фильтровать
    parser.add_argument(
        "--countries",
        "-c",
        nargs='+',
        type=str,
        help="filter by countries (write locale: RU, US...) (default - (ALL))",
        default=[]
    )

    # По каким кодам ответов
    # HTTP фильтровать
    parser.add_argument(
        "--status-codes",
        '-sc',
        nargs='+',
        type=int,
        help="filter by HTTP status codes (default = (ALL))",
        default=[]
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

    # Выводить ли расширенную
    # информацию
    parser.add_argument(
        '--verbose',
        '-v',
        help='Do should show extended work info',
        action='store_true',
        default=False
    )

    # Получаем аргументы
    args = parser.parse_args()

    # Получаем возможный ввод из pipeline
    getted_stdin = "" if not select.select(
        [sys.stdin, ], [], [], 0.0
    )[0] else sys.stdin.read()

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

    # Объект проверяльщика прокси
    taster = ProxiesTaster(proxies)

    # Его настройки
    taster.set_workers(args.workers)
    taster.set_protocols(args.protocols)
    if args.verbose:
        FLOGGER, DLOGGER = setting_logging(args.logconfig, **logkwargs)
        taster.set_logger(DLOGGER)


    # Получаем прокси, фильтруем их
    # и преобразуем в строки
    results = map(
        string_cast, filter(
            status_codes_filter(args.status_codes), filter(
                country_filter(args.countries),
                await taster.run()
            )
        )
    )


    # Сохраняем в файл
    if args.out:
        if args.verbose:
            DLOGGER.info(f"Write result in '{args.out}'")
        with open(args.out, "w", encoding="uTF-8") as valid_proxy:
            valid_proxy.write("\n".join(results))

    # Добавляем в файл
    if args.append:
        if args.verbose:
            DLOGGER.info(
                f"Append to file end result; Filename is '{args.append}'"
            )

        with open(args.append, "a", encoding="UTF-8") as valid_proxy:
            for proxy in results:
                valid_proxy.write("\n" + proxy)

if __name__ == "__main__":
    asyncio.run(main())
