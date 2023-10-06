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
from include.taster import ProxiesTaster

# My logger
from include.logger import setting_logging


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
        nargs='+',
        type=str,
        help="get by country (write locale: RU, US, UA, EN...) (default - [] (ALL))",
        default=[]
    )

    # Какую страну выделять
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

    if args.verbose:
        FLOGGER, DLOGGER = setting_logging(args.logconfig, **logkwargs)

    # Объект проверяльщика прокси
    taster = ProxiesTaster(proxies)

    # Добавляем настройки и фильтры
    taster.set_workers(args.workers)
    taster.set_country(args.country)
    taster.set_protocols(args.protocols)
    if args.verbose:
        taster.set_logger(DLOGGER)

    # Конвертируем все элементы в строки
    results = ProxiesTaster.cast_to_string(
        # Получаем результат проверки
        await taster.run()
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
