# App

Простой прокси-чекер, написанный
на языке python с использованием
asyncio

Приложение позволяет быстро проверить
переданный список прокси

**Установка**

Для установки необходимо скопировать репозиторий
на ваш компьютер `git clone https://www.github.com/ThwWhatis/ProxiesTaster`,
далее перейти в директорию, куда установлен скрипт и запустить `make install`

Для удаления достаточно запустить `make uninstall`

**Список аргументов:**

```default
usage: proxies-taster [-h] [--out OUT] [--append APPEND] [--workers WORKERS]
                       [--protocols PROTOCOLS [PROTOCOLS ...]] [--countries COUNTRIES [COUNTRIES ...]]
                       [--status-codes STATUS_CODES [STATUS_CODES ...]] [--logconfig LOGCONFIG]
                       [--logdir LOGDIR] [--loglevel LOGLEVEL] [--logformat LOGFORMAT] [--verbose]
                       [proxies]

 Скрипт, позволяющий проверить все переданные прокси

 positional arguments:
   proxies               Путь до файла со списком прокси, либо просто список прокси (разделенные
                         переводом строки или пробелом)

 options:
   -h, --help            show this help message and exit
   --out OUT, -o OUT     Путь до файла, в который необходимо записать результат
   --append APPEND, -a APPEND
                         Добавить полученный результат в конец переданного файла
   --workers WORKERS, -w WORKERS
                         Количество "воркеров" - асинхронных запросов
   --protocols PROTOCOLS [PROTOCOLS ...], -p PROTOCOLS [PROTOCOLS ...]
                         Фильтр по протоколам прокси (socks4, socks4 и т.д.)
   --countries COUNTRIES [COUNTRIES ...], -c COUNTRIES [COUNTRIES ...]
                         Фильтр по странам (необходимо вводить локаль: RU, EN, US и т.д.)
   --status-codes STATUS_CODES [STATUS_CODES ...], -sc STATUS_CODES [STATUS_CODES ...]
                         Фильтр по HTTP кодам ответов от прокси (по-умолчанию все)
   --logconfig LOGCONFIG, -lc LOGCONFIG
                         Путь до конфига для вывода логов
   --logdir LOGDIR, -ld LOGDIR
                         В какую директорию сохранять файлы логов
   --loglevel LOGLEVEL, -ll LOGLEVEL
                         Уровень вывода логов (debug, critical, info и т.д.) только для вывода в
                         терминал (stdout)
   --logformat LOGFORMAT, -lf LOGFORMAT
                         log format
   --verbose, -v         Расширенный вывод информации о работе скрипта
```

**Пример использования**

Для начана необходимо сделать скрипт
исполняемым `sudo chmod ugo+x proxies-taster`
(если на linux)

Далее вы можете создат alias для запуска
скрипта из любого расположения `alias proxies-taster=/path/to/proxies-taster`
(если на linux)

С простой передачей прокси:

```default
proxies-taster '72.195.34.59:4145 43.248.27.8:4646' --verbose --out valid.txt
proxies-taster 72.195.34.59:4145,43.248.27.8:4646 --verbose --out valid.txt
```

Прокси из файла .txt:

```default
proxies-taster proxies.txt --verbose --append valid.txt
```

Или с помощью pipe:

```default
cat proxies.txt | proxies-taster --verbose --append valid.txt
```
