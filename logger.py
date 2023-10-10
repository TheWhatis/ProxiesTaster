# Standart
import json
import logging

from os import path
from sys import exc_info, stdout

from datetime import datetime
from pathlib import Path

# Colorama
from colorama import Fore, Style


# Настраиваем логирование
class ColorFormatter(logging.Formatter):
    """
    Цветной вывод логирования;
    --------------------------
    .. Форматтер для красивого вывода
       текста в консоль
    """

    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.WHITE,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.YELLOW + Style.BRIGHT,
        "NOTSET": Fore.WHITE
    }

    def format(self, record):
        if record.levelname in self.COLORS:
            # Добавляем цвет
            record.levelname = self.COLORS[record.levelname] + record.levelname

            # Убираем цвет для остального текста
            record.levelname += Fore.RESET + Style.RESET_ALL

        # Возвращаем значение
        return logging.Formatter.format(self, record)


def setting_logging(
        config_file: str,
        **kwargs: dict[str, str]
) -> tuple[logging.Logger, logging.Logger]:
    """
    Нестройка логирования;
    ----------------------
    .. Здесь вся настройка логирования
       Создается 2 логгера FLOGGER и DLOGGER в
       глобальном пространстве

       FLOGGER - логирование исключительно в файл
       DLOGGER - логирование и в файл и в терминал (stdout)

       Настраивать можно через log.config.json
       Директория для логов, уровень логирования и формат логов

    :param config_file: ``str``
        .. Путь до файла с конфигурацией логирования

    :param stdout: ``TextIOWrapper``
        .. Тип ввода-вывода для вывода логов в терминал

    :param kwargs: ``dict[str]``
        .. Параметры логирования - {
               dir: str,
               level: "notset | debug | info | warning | error | critical",
               format: str
           }, где:
           'dir' - папка с логами,
           'level' - уровень логирования, а
           'format' - формат вывода логов

    """
    FLOGGER = logging.getLogger("FLOGGER")
    DLOGGER = logging.getLogger("DLOGGER")

    # Получаем сегодняшнюю дату
    if path.isfile(config_file):
        with open(config_file, "r", encoding = "UTF-8") as open_config_file:
            config = json.load(open_config_file)

            # Если какие-то переменные не существуют
            if "dir" not in config:
                config["dir"] = "logs/"

            if "level" not in config:
                config["level"] = "debug"

            if "format" not in config:
                config["format"] = "%(asctime)s; %(levelname)s: %(message)s"
    else:
        config = {
            "dir": "logs/",
            "level": "debug",
            "format": "%(asctime)s; %(levelname)s: %(message)s"
        }

    if "dir" in kwargs:
        config["dir"] = kwargs["dir"]

    if "level" in kwargs:
        config["level"] = kwargs["level"]

    if "format" in kwargs:
        config["format"] = kwargs["format"]

    # Генерируем название файла с логами
    now = datetime.now().strftime("%d-%m-%Y")
    logfile = config["dir"] + now + ".log"

    # Генерируем файл, где храняться логи
    if not path.isfile(logfile):
        output_file = Path(logfile)
        output_file.parent.mkdir(exist_ok=True, parents=True)

    # Формат логирования
    formatter = logging.Formatter(config["format"])

    # В файле
    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.NOTSET)

    # В терминале
    stdout_handler = logging.StreamHandler(stdout)
    stdout_handler.setFormatter(ColorFormatter(config["format"]))

    DLOGGER.setLevel(logging.DEBUG)
    FLOGGER.setLevel(logging.DEBUG)

    # Устанавливаем уровень логирования
    if "critical" == config["level"]:
        stdout_handler.setLevel(logging.CRITICAL)
    elif "error" == config["level"]:
        stdout_handler.setLevel(logging.ERROR)
    elif "warning" == config["level"]:
        stdout_handler.setLevel(logging.WARNING)
    elif "info" == config["level"]:
        stdout_handler.setLevel(logging.INFO)
    elif "notset" == config["level"]:
        stdout_handler.setLevel(logging.NOTSET)
    else:
        stdout_handler.setLevel(logging.DEBUG)

    FLOGGER.addHandler(file_handler)
    DLOGGER.addHandler(file_handler)
    DLOGGER.addHandler(stdout_handler)

    return FLOGGER, DLOGGER


# Классы исключений для логирования
class LogException(Exception):
    """
    Исключение для логирования (logging);
    -------------------------------------
    .. Это исключение можно перехватывать из функции,
       в которой нужно что-то залогировать (при этом raise
       этого исключения не будет)
    """
    def __init__(self, message):
        super().__init__(message)


# Декораторы
def log(info: str = "", show: bool = False) -> any:
    """
    Декоратор для логирования;
    --------------------------
    .. Декоратор для логирования
       работы функций, возможно методов и
       классов
       Логирует начало работы функции и исключения


    :param info: ``str``
        .. Что будет писать в логах при запуске функции

    :param show: ``bool``
        .. Показывать ли логи в терминал


    :param returns: ``any``
        .. Возвращает обертку функции, как и все декораторы;
    """
    DLOGGER = logging.getLogger("DLOGGER")
    FLOGGER = logging.getLogger("FLOGGER")

    def log_decorator(func):
        def _wrapper(*args, **kwargs):
            if info and isinstance(info, str):
                if show:
                    DLOGGER.info(info)
                else:
                    FLOGGER.info(info)

            result = False
            # Запускаем функцию
            try:
                result = func(*args, **kwargs)
                # Логируем ошибку
            except Exception as error:
                exc_type, exc_tb = exc_info()
                filename = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                message = "Type - " + str(exc_type) + "; "
                message += "Message - " + str(error) + "; "
                message += "Filename - " + filename + "; "
                message += "on line: " + str(exc_tb.tb_lineno)

                FLOGGER.critical(message)
                raise error

            return result
        return _wrapper
    return log_decorator
