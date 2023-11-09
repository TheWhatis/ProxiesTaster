# Types

### *class* proxies_taster.types.Protocol(value, names=None, \*, module=None, qualname=None, type=None, start=1, boundary=None)

Базовые классы: `Enum`

Доступные протоколы прокси

* **Параметры:**
  * **SOCKS5** (*str*) – SOCKS5 прокси
  * **SOCKS4** (*str*) – SOCKS4 прокси
  * **HTTPS** (*str*) – HTTPS прокси
  * **HTTP** (*str*) – HTTP прокси

#### HTTP *= 'http'*

#### HTTPS *= 'https'*

#### SOCKS4 *= 'socks4'*

#### SOCKS5 *= 'socks5'*

### proxies_taster.types.Proxies

Тип данных обозначающий в каком формате
передавать прокси для их проверки и обработки

alias of `list`[`Union`[`str`, [`ProxyDict`](#proxies_taster.types.ProxyDict)]]

### *class* proxies_taster.types.ProxyDict(protocol: [Protocol](#proxies_taster.types.Protocol), proxy: str)

Базовые классы: `object`

Датакласс для прокси, когда
передается вместе с протоклом

* **Параметры:**
  * **protocol** ([*Protocol*](#proxies_taster.types.Protocol)) – Протокол, по которому подключаться
  * **proxy** (*str*) – Сам прокси ip:port

#### protocol*: [Protocol](#proxies_taster.types.Protocol)*

#### proxy*: str*

### *class* proxies_taster.types.WorkedProxy(protocol: [Protocol](#proxies_taster.types.Protocol), proxy: str, url: str, response: ClientResponse, status: int, body: dict | str, country: str | False)

Базовые классы: [`ProxyDict`](#proxies_taster.types.ProxyDict)

Класс для прокси которые
были проверены

* **Параметры:**
  * **url** (*str*) – Ссылка на прокси
  * **response** (*ClientResponse*) – Объект ответа от сервера
  * **status** (*int*) – Http код ответа
  * **body** (*Union**[**dict**,* *str**]*) – Тело ответа
  * **country** (*Union**[**str**,* *False**]*) – Страна прокси

#### body*: dict | str*

#### country*: str | False*

#### response*: ClientResponse*

#### status*: int*

#### url*: str*
