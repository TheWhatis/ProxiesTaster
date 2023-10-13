Package
=======

**Установка**

``pip install proxies-taster``

**Использование**

.. code-block:: python

   # Подключаем модуль
   from proxies_taster import Protocol
   from proxies_taster import ProxyDict
   from proxies_taster import ProxiesTaster
   from proxies_taster.events_data import Events

   # Список прокси
   proxies = [
        # Простая передачи списка прокси
        '184.178.172.28:15294',
        '142.54.226.214:4145',
        '174.77.111.196:4145',
        '72.195.114.169:4145',

        # Установить проверяемый прокси
        # прямо в строке с самим прокси
        'socks5://184.95.235.194:1080',

        # Или за счет использования объекта
        # proxies_taster.ProxyDict
        ProxyDict(
            protocol = Protocol.SOCKS4,
            proxy = '125.141.139.112:5566'
        )
   ]

   # Иницилизируем класс
   taster = ProxiesTaster(proxies)

   # Установка настроек
   taster.set_workers(300)
   taster.set_protocols(
       [
           Protocol.SOCKS4,
           Protocol.SOCKS5,
           Protocol.HTTP
       ]
   )

   # Также доступны установки
   # обработчиков на разные события
   taster.on(Events.error, lambda event: print(event))
   taster.on(Events.check_error, lambda event: print(event))

   taster.on(
       Events.check_success, lambda event: print(
           f"Proxy is working {event.proxy.proxy}"
       )
   )

   # Запускаем проверку
   # и получаем результат
   proxies = await taster.run()

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   package/ProxiesTaster
   package/types
   package/events_data
