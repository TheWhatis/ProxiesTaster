Package
=======

**Установка**

``pip install proxies-taster``

**Использование**

.. code-block:: python

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
   
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   package/ProxiesTaster
   package/types
   package/events_data
