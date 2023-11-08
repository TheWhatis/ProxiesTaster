# Events

### *class* proxies_taster.events_data.End(name: str, result: Any)

Базовые классы: [`Event`](#proxies_taster.events_data.Event)

Скенет данных события окончания
его работы

* **Параметры:**
  **result** (*Any*) – Любой резульатат конца
  работы события

#### result*: Any*

### *class* proxies_taster.events_data.Error(name: str, message: str, level: Literal['not work', 'error', 'critical', 'skipped'])

Базовые классы: [`Event`](#proxies_taster.events_data.Event)

Скелет данных события
для ошибок

* **Параметры:**
  * **message** (*str*) – Сообщение ошибки
  * **level** (*Literal**[**'default'**,* *'error'**,* *'critical'**,* *'skipped'**]*) – Уровень ошибки: если „not work“,
    то это уровень «не работы прокси», если „error“,
    то скорее всего это ошибка передачи параметров, либо
    не сильно критические непредвиденные ошибки, а „critical“
    уже является ошибкой, которая не совместима с работой
    скрипта. В тоже время „skipped“ - это ошибки, не влияющие
    на работоспособность или не работоспособность прокси.
    Это промежутночные ошибки, возникающие при работе проверки

#### exception*: any* *= False*

#### level*: Literal['not work', 'error', 'critical', 'skipped']*

#### message*: str*

### *class* proxies_taster.events_data.Event(name: str)

Базовые классы: `object`

Скелет данных всех событий

* **Параметры:**
  * **name** (*str*) – Название события
  * **additional** (*Any*) – Доп аргументы для него

#### name*: str*

### *class* proxies_taster.events_data.Events(value, names=None, \*, module=None, qualname=None, type=None, start=1, boundary=None)

Базовые классы: `Enum`

Набор констант с событиями,
которые имеются в ProxiesTaster

* **Параметры:**
  * **error** (*str*) – Общее событие ошибки,
    вызывается всегда когда возникает
    ошибка, во всех методах
  * **except** (*str*) – Начало работы метода taster.exc
  * **except_end** (*str*) – Окончание работы метода taster.exc
  * **except_success** (*str*) – Успешное завершение
    работы метода taster.exc (прокси
    был получен)
  * **except_error** (*str*) – Какая-либо ошибка при
    работе метода taster.exc
  * **except_error_skipped** (*str*) – Пропущенная ошибка при
    работе метода taster.exc
  * **check** (*str*) – Начало работы метода taster.check
  * **check_end** (*str*) – Конец работы метода taster.check
  * **check_success** – Успешное завершение
    работы метода taster.check (прокси
    был получен)
  * **check_error** (*str*) – Какая-либо ошибка при
    работе метода taster.check

#### check*: str* *= 'check.start'*

#### check_end*: str* *= 'check.end'*

#### check_error*: str* *= 'check.error'*

#### check_success*: str* *= 'check.success'*

#### error*: str* *= 'error'*

#### except_*: str* *= 'except.start'*

#### except_end*: str* *= 'except.end'*

#### except_error*: str* *= 'except.error'*

#### except_error_skipped *= 'except.error.skipped'*

#### except_success*: str* *= 'except.success'*

### *class* proxies_taster.events_data.Proxy(name: str, protocol: [Protocol](types.md#proxies_taster.types.Protocol) | False, proxy: str | [WorkedProxy](types.md#proxies_taster.types.WorkedProxy))

Базовые классы: [`Event`](#proxies_taster.events_data.Event)

Скелет данных любого события, которое
будет непосредственно работать
с каким-либо прокси

* **Параметры:**
  * **protocol** ([*Protocol*](types.md#proxies_taster.types.Protocol)) – Протокол прокси: HTTP, SOCKS4 и т.д.
  * **proxy** (*str*) – Сама строка прокси или
    уже рабочий прокси

#### protocol*: [Protocol](types.md#proxies_taster.types.Protocol) | False*

#### proxy*: str | [WorkedProxy](types.md#proxies_taster.types.WorkedProxy)*

### *class* proxies_taster.events_data.ProxyError(name: str, message: str, level: Literal['not work', 'error', 'critical', 'skipped'], protocol: [Protocol](types.md#proxies_taster.types.Protocol) | False, proxy: str | [WorkedProxy](types.md#proxies_taster.types.WorkedProxy))

Базовые классы: [`Proxy`](#proxies_taster.events_data.Proxy), [`Error`](#proxies_taster.events_data.Error)

Скелет данных события ошибки при
работе с прокси

### *class* proxies_taster.events_data.ProxySuccess(name: str, protocol: [Protocol](types.md#proxies_taster.types.Protocol) | False, proxy: str | [WorkedProxy](types.md#proxies_taster.types.WorkedProxy))

Базовые классы: [`Proxy`](#proxies_taster.events_data.Proxy), [`Success`](#proxies_taster.events_data.Success)

Скелет данных события, которое вызывается
при успешной проверке или работе
с прокси

### *class* proxies_taster.events_data.RunEnd(name: str, proxies: list[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy)])

Базовые классы: [`Event`](#proxies_taster.events_data.Event)

Данные события окончания
работы проверки прокси

* **Параметры:**
  **proxies** (*list**[*[*WorkedProxy*](types.md#proxies_taster.types.WorkedProxy)*]*) – Список рабочих прокси

#### proxies*: list[[WorkedProxy](types.md#proxies_taster.types.WorkedProxy)]*

### *class* proxies_taster.events_data.RunStart(name: str, proxies: list[str | [ProxyDict](types.md#proxies_taster.types.ProxyDict)], workers: int)

Базовые классы: [`Event`](#proxies_taster.events_data.Event)

Данные события запуска проверки
прокси

* **Параметры:**
  * **proxies** (*Proxies*) – Список прокси
  * **workers** (*int*) – Количество «воркеров» -
    асинхронных запросов

#### proxies*: list[str | [ProxyDict](types.md#proxies_taster.types.ProxyDict)]*

#### workers*: int*

### *class* proxies_taster.events_data.Start(name: str, args: list, kwargs: dict)

Базовые классы: [`Event`](#proxies_taster.events_data.Event)

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

Базовые классы: [`Event`](#proxies_taster.events_data.Event)

Скелет данных события для
завершенной задачи
