# ProxiesTaster

### *class* proxies_taster.ProxiesTaster(proxies: list[str | [ProxyDict](types.md#proxies_taster.types.ProxyDict)])

Базовые классы: `object`

Класс который как-раз таки
и проверяет полученные прокси

Для начала необходимо просто при
иницилизации передать необходимые
прокси:

```python
taster = ProxiesTaster(
    [
        '194.163.132.76:41212',
        '91.121.52.213:55348',
        ProxyDict(
            'socks4',
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
taster.set_workers(200)
taster.set_protocols(['socks4', 'socks5'])
```

* **Параметры:**
  **errors** (*tuple*) – Список ошибок, которые возникают
  при неправильной работе прокси (список
  пропускаемых ошибок)

#### *async* check(proxy: str, protocol: Literal['http', 'https', 'socks4', 'socks5'] | False = False)

Проверяет прокси на роботоспособность
и определяет его сетевой протокол

Проверка производиться перебором
протоколов и попыткой подключения
к ним. Автоматически проверяется
работоспособность

* **Параметры:**
  * **proxy** (*str*) – Сам прокси ip:port
  * **protocol** (*Union**[**Protocol**,* *False**]*) – Протокол по которому проверять прокси
* **Результат:**
  Если успешно - выдает протокол, прокси
  и расположение (результат ответа от ipinfo.io)
* **Тип результата:**
  Union[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy), False]

**Пример работы**

```python
result = await taster.check('107.174.66.231:36626')
# Или
result = await taster.check('107.174.66.231:36626', 'https')
```

#### errors *= (<class 'aiohttp_proxy.errors.InvalidServerReply'>, <class 'aiohttp.client_exceptions.ClientConnectorError'>, <class 'aiohttp_proxy.errors.InvalidServerVersion'>, <class 'aiohttp.client_exceptions.ServerDisconnectedError'>, <class 'TimeoutError'>, <class 'TimeoutError'>, <class 'ConnectionResetError'>, <class 'aiohttp_proxy.errors.SocksConnectionError'>, <class 'aiohttp.client_exceptions.ClientHttpProxyError'>, <class 'aiohttp.client_exceptions.ClientOSError'>, <class 'aiohttp.client_exceptions.ClientResponseError'>, <class 'aiohttp.client_exceptions.ClientPayloadError'>, <class 'aiohttp_proxy.errors.NoAcceptableAuthMethods'>, <class 'aiohttp_proxy.errors.SocksError'>, <class 'aiohttp.client_exceptions.InvalidURL'>)*

#### *async* exc(protocol: Literal['http', 'https', 'socks4', 'socks5'], proxy: str)

Делает запрос через aiohttp
и, с помощью exceptions, определяет
что прокси рабочий или нет

* **Параметры:**
  * **protocol** (*Protocol*) – Протокол, по которому обращаться к прокси
  * **proxy** (*str*) – Сам прокси
* **Результат:**
  Возвращает либо
  проверенный прокси, либо False
* **Тип результата:**
  Union[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy), False]

**Пример проверки прокси**

```python
result = await taster.exc('socks4', '107.174.66.231:36626')
```

#### on(event: str, listener: Callable[[[Event](events_data.md#proxies_taster.events_data.Event)], Any])

Установить обработчик события

* **Параметры:**
  * **event** (*str*) – Название события
  * **listener** (*Callable**[**[*[*Event*](events_data.md#proxies_taster.events_data.Event)*]**,* *None**]*) – Обработчик этого события
* **Результат:**
  Ничего не возвращает
* **Тип результата:**
  None

**Пример работы**

```python
def print_data(data):
    print(data.name, data)

# Можно установить лямбду
taster.on('error', lambda event: logger.error(event.message))

# Или функцию
taster.on('check.start', print_data)
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

#### set_protocols(protocols: list[Literal['http', 'https', 'socks4', 'socks5']])

Установить определяемые
протоколы (что-то вроде фильтра)

* **Параметры:**
  **protocols** (*list**[**Protocol**]*) – Список определяемых протоколов:
  http, https, socks4, socks5
* **Результат:**
  Ничего не возвращает
* **Тип результата:**
  None

**Пример работы**

```python
taster.set_protocols(['socks4', 'socks5'])
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
