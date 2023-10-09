# Package

**Установка**

`pip install proxies-taster`

**Использование**

```python
# Подключаем модуль
from proxies_taster import ProxiesTaster
from proxies_taster import ProxyDict

# Список прокси
proxies = [
     '184.178.172.28:15294',
     '142.54.226.214:4145',
     '174.77.111.196:4145',
     '72.195.114.169:4145',
     '184.95.235.194:1080',
     ProxyDict(
         protocol = 'socks4',
         proxy = '125.141.139.112:5566'
     )
]

# Иницилизируем класс
taster = ProxiesTaster(proxies)

# Устанавливаем настройки
taster.set_protocols(['socks4', 'socks5', 'https'])
taster.set_workers(300)

# Также доступы установки
# обработчиков на разные события
taster.on('error', lambda event: print(event))
taster.on('check.error', lambda event: print(event))

taster.on(
    'check.success', lambda event: print(
        f"Proxy is working {event.proxy.proxy}"
    )
)
```

# Contents:

* [ProxiesTaster](package/ProxiesTaster.md)
  * [`ProxiesTaster`](package/ProxiesTaster.md#proxies_taster.ProxiesTaster)
* [Types](package/types.md)
  * [`Protocol`](package/types.md#proxies_taster.types.Protocol)
  * [`Proxies`](package/types.md#proxies_taster.types.Proxies)
  * [`ProxyDict`](package/types.md#proxies_taster.types.ProxyDict)
  * [`UrlProtocol`](package/types.md#proxies_taster.types.UrlProtocol)
  * [`WorkedProxy`](package/types.md#proxies_taster.types.WorkedProxy)
* [Events](package/events_data.md)
  * [`End`](package/events_data.md#proxies_taster.events_data.End)
  * [`Error`](package/events_data.md#proxies_taster.events_data.Error)
  * [`Event`](package/events_data.md#proxies_taster.events_data.Event)
  * [`Proxy`](package/events_data.md#proxies_taster.events_data.Proxy)
  * [`ProxyError`](package/events_data.md#proxies_taster.events_data.ProxyError)
  * [`ProxySuccess`](package/events_data.md#proxies_taster.events_data.ProxySuccess)
  * [`RunEnd`](package/events_data.md#proxies_taster.events_data.RunEnd)
  * [`RunStart`](package/events_data.md#proxies_taster.events_data.RunStart)
  * [`Start`](package/events_data.md#proxies_taster.events_data.Start)
  * [`Success`](package/events_data.md#proxies_taster.events_data.Success)
