## class SSEConsumer

SSE-клиент, получающий эвенты от телеграм-бота.
В качестве SSE-библиотеки используется [httpx](https://github.com/encode/httpx).

Инициализация:

```python
from cba.consumers import SSEConsumer

SSE_URL = "http://localhost:8081/sse/ACTUATOR_NAME/events"
consumer = SSEConsumer(sse_url=SSE_URL)
```

ручной запуск:

```python
import asyncio

events_queue = asyncio.Queue()
loop = asyncio.get_event_loop()
loop.create_task(consumer.listen(events_queue))
loop.run_forever()
```

на каждое полученное Event-сообщение от сервера SSEConsumer
будет создавать экземпляр класса _BaseDispatcherEvent_ и класть его в очередь.