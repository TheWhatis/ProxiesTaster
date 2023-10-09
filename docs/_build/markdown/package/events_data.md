# Events

### *class* proxies_taster.events_data.End(name: str, result: Any)

Скенет данных события окончания
его работы

* **Параметры:**
  **result** (*Any*) – Любой резульатат конца
  работы события

#### result*: Any*

### *class* proxies_taster.events_data.Error(name: str, message: str, level: Literal['not work', 'error', 'critical'])

Скелет данных события
для ошибок

* **Параметры:**
  * **message** (*str*) – Сообщение ошибки
  * **level** (*Literal**[**'default'**,* *'error'**,* *'critical'**]*) – Уровень ошибки: если „not work“,
    то это уровень «не работы прокси», если „error“,
    то скорее всего это ошибка передачи параметров, либо
    не сильно критические непредвиденные ошибки, а „critical“
    уже является ошибкой, которая не совместима с работой скрипта

#### level*: Literal['not work', 'error', 'critical']*

#### message*: str*

### *class* proxies_taster.events_data.Event(name: str)

Скелет данных всех событий

* **Параметры:**
  * **name** (*str*) – Название события
  * **additional** (*Any*) – Доп аргументы для него

#### name*: str*

### *class* proxies_taster.events_data.Proxy(name: str, protocol: Literal['http', 'https', 'socks4', 'socks5'], proxy: str | [WorkedProxy](types.md#proxies_taster.types.WorkedProxy))

Скелет данных любого события, которое
будет непосредственно работать
с каким-либо прокси

* **Параметры:**
  * **protocol** (*Protocol*) – Протокол прокси: HTTP, SOCKS4 и т.д.
  * **proxy** (*str*) – Сама строка прокси или
    уже рабочий прокси

#### protocol*: Literal['http', 'https', 'socks4', 'socks5']*

#### proxy*: str | [WorkedProxy](types.md#proxies_taster.types.WorkedProxy)*

### *class* proxies_taster.events_data.ProxyError(name: str, message: str, level: Literal['not work', 'error', 'critical'], protocol: Literal['http', 'https', 'socks4', 'socks5'] | False, proxy: str | [WorkedProxy](types.md#proxies_taster.types.WorkedProxy))

Скелет данных события ошибки при
работе с прокси

* **Параметры:**
  **protocol** (*Union**[**Protocol**,* *False**]*) – В зависимости, был ли
  передан протокол при проверке или нет,
  может быть False или название протокола

#### protocol*: Literal['http', 'https', 'socks4', 'socks5'] | False*

### *class* proxies_taster.events_data.ProxySuccess(name: str, protocol: Literal['http', 'https', 'socks4', 'socks5'], proxy: str | [WorkedProxy](types.md#proxies_taster.types.WorkedProxy))

Скелет данных события, которое вызывается
при успешной проверке или работе
с прокси

### *class* proxies_taster.events_data.RunEnd(name: str, proxies: list[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy)])

Данные события окончания
работы проверки прокси

* **Параметры:**
  **proxies** (*list**[*[*WorkedProxy*](types.md#proxies_taster.types.WorkedProxy)*]*) – Список рабочих прокси

#### proxies*: list[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy)]*

### *class* proxies_taster.events_data.RunStart(name: str, proxies: list[str | [ProxyDict](types.md#proxies_taster.types.ProxyDict)], workers: int)

Данные события запуска проверки
прокси

* **Параметры:**
  * **proxies** (*Proxies*) – Список прокси
  * **workers** (*int*) – Количество «воркеров» -
    асинхронных запросов

#### proxies*: list[str | [ProxyDict](types.md#proxies_taster.types.ProxyDict)]*

#### workers*: int*

### *class* proxies_taster.events_data.Start(name: str, args: list, kwargs: dict)

Скелет данных события, которое
вызывается при начале работы
какого-либо действия

* **Параметры:**
  * **args** (*list*) – Распакованный список аргументов,
    передаваемых в функцию, метод
  * **kwargs** (*dict*) – Распакованный список именованных
    аргументов, передаваемых в функцию, метод

#### args*: list*

#### kwargs*: dict*

### *class* proxies_taster.events_data.Success(name: str)

Скелет данных события для
завершенной задачи
