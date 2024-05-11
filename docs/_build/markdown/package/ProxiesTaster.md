# ProxiesTaster

### *class* proxies_taster.ProxiesTaster(proxies: list[str | [ProxyDict](types.md#proxies_taster.types.ProxyDict)])

Базовые классы: `object`

Класс который как-раз таки
и проверяет полученные прокси

Для начала необходимо просто при
иницилизации передать необходимые
прокси:

```python
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
```

Далее можете изменить некоторые
настройки (своё количество
«воркеров» - количество асинхронных
запросов, определяемые протоколы:

```python
from proxies_taster import Protocol

taster.set_workers(2000)
taster.set_protocols(
    [Protocol.SOCKS4, Protocol.SOCKS5]
)
```

* **Параметры:**
  **errors** (*tuple*) – Список ошибок, которые возникают
  при неправильной работе прокси (список
  пропускаемых ошибок)

#### *async* check(proxy: str, protocol: [Protocol](types.md#proxies_taster.types.Protocol) | False = False)

Проверяет прокси на роботоспособность
и определяет его сетевой протокол

Проверка производиться перебором
протоколов и попыткой подключения
к ним. Автоматически проверяется
работоспособность

* **Параметры:**
  * **proxy** (*str*) – Сам прокси ip:port
  * **protocol** (*Union* *[*[*Protocol*](types.md#proxies_taster.types.Protocol) *,* *False* *]*) – Протокол по которому проверять прокси
* **Результат:**
  Если успешно - выдает протокол, прокси
  и расположение (результат ответа от ipinfo.io)
* **Тип результата:**
  Union[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy), False]

**Пример работы**

```python
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
```

#### errors *= (<class 'aiohttp_proxy.errors.InvalidServerReply'>, <class 'aiohttp.client_exceptions.ClientConnectorError'>, <class 'aiohttp_proxy.errors.InvalidServerVersion'>, <class 'aiohttp.client_exceptions.ServerDisconnectedError'>, <class 'TimeoutError'>, <class 'TimeoutError'>, <class 'ConnectionResetError'>, <class 'aiohttp_proxy.errors.SocksConnectionError'>, <class 'aiohttp.client_exceptions.ClientHttpProxyError'>, <class 'aiohttp.client_exceptions.ClientOSError'>, <class 'aiohttp.client_exceptions.ClientResponseError'>, <class 'aiohttp.client_exceptions.ClientPayloadError'>, <class 'aiohttp_proxy.errors.NoAcceptableAuthMethods'>, <class 'aiohttp_proxy.errors.SocksError'>, <class 'aiohttp.client_exceptions.InvalidURL'>)*

#### *async* exc(protocol: [Protocol](types.md#proxies_taster.types.Protocol), proxy: str)

Делает запрос через aiohttp
и, с помощью exceptions, определяет
что прокси рабочий или нет

* **Параметры:**
  * **protocol** ([*Protocol*](types.md#proxies_taster.types.Protocol)) – Протокол, по которому обращаться к прокси
  * **proxy** (*str*) – Сам прокси
* **Результат:**
  Возвращает либо
  проверенный прокси, либо False
* **Тип результата:**
  Union[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy), False]

**Пример проверки прокси**

```python
from proxies_taster import Protocol

result = await taster.exc(
    Protocol.SOCKS4, '107.174.66.231:36626'
)
```

#### on(event: [Events](events_data.md#proxies_taster.events_data.Events), listener: Callable[[[Event](events_data.md#proxies_taster.events_data.Event)], Any])

Установить обработчик события

* **Параметры:**
  * **event** ([*Events*](events_data.md#proxies_taster.events_data.Events)) – Название события
  * **listener** (*Callable* *[* *[*[*Event*](events_data.md#proxies_taster.events_data.Event) *]* *,* *None* *]*) – Обработчик этого события
* **Результат:**
  Ничего не возвращает
* **Тип результата:**
  None

**Пример работы**

```python
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
```

#### *async* run()

Запускает весь процесс проверки
и возвращает уже рабочие прокси

* **Результат:**
  Рабочие прокси
* **Тип результата:**
  list[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy)]

**Пример работы**

```python
result = await taster.run()
```

#### set_protocols(protocols: [Protocol](types.md#proxies_taster.types.Protocol) | list[[Protocol](types.md#proxies_taster.types.Protocol)])

Установить определяемые
протоколы (что-то вроде фильтра)

* **Параметры:**
  **protocols** (*Union* *[**list* *[*[*Protocol*](types.md#proxies_taster.types.Protocol) *]* *]*) – Список определяемых протоколов:
  Protocol.HTTP, Protocol.HTTPS,
  Protocol.SOCKS4, Protocol.SOCKS5
* **Результат:**
  Ничего не возвращает
* **Тип результата:**
  None

**Пример работы**

```python
from proxies_taster import Protocol

taster.set_protocols(
    [Protocol.SOCKS4, Protocol.SOCKS5]
)
```

#### set_workers(workers: int)

Установить количество асинхронных
задач «воркеров»

* **Параметры:**
  **workers** (*int*) – Количество асинхронных задач
* **Результат:**
  Ничего не возвращает
* **Тип результата:**
  None

**Пример работы**

```python
taster.set_workers(300)
```
