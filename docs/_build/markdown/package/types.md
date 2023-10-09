# Types

### proxies_taster.types.Protocol

Доступные протоколы для Прокси

alias of `Literal`[„http“, „https“, „socks4“, „socks5“]

### proxies_taster.types.Proxies

Тип данных обозначающий в каком формате
передавать прокси для их проверки и обработки

alias of `list`[`Union`[`str`, [`ProxyDict`](#proxies_taster.types.ProxyDict)]]

### *class* proxies_taster.types.ProxyDict(protocol: Literal['http', 'https', 'socks4', 'socks5'], proxy: str)

Базовые классы: `object`

Датакласс для прокси, когда
передается вместе с протоклом

* **Параметры:**
  * **protocol** (*Protocol*) – Протокол, по которому подключаться
  * **proxy** (*str*) – Сам прокси ip:port

#### protocol*: Literal['http', 'https', 'socks4', 'socks5']*

#### proxy*: str*

### proxies_taster.types.UrlProtocol

Доступные протоколы HTTP

alias of `Literal`[„http“, „https“]

### *class* proxies_taster.types.WorkedProxy(protocol: Literal['http', 'https', 'socks4', 'socks5'], proxy: str, response: ClientResponse, status: int, body: dict | str, country: str | False)

Базовые классы: [`ProxyDict`](#proxies_taster.types.ProxyDict)

Класс для прокси которые
были проверены

* **Параметры:**
  * **response** (*ClientResponse*) – Объект ответа от сервера
  * **status** (*int*) – Http код ответа
  * **body** (*Union**[**dict**,* *str**]*) – Тело ответа
  * **country** (*Union**[**str**,* *False**]*) – Страна прокси

#### body*: dict | str*

#### country*: str | False*

#### response*: ClientResponse*

#### status*: int*
