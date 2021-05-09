## class SSEConsumer

SSE client that receives events from a telegram bot.
The SSE library is [httpx](https://github.com/encode/httpx).

Initialization:

```python
from cba.consumers import SSEConsumer

SSE_URL = "http://localhost:8081/sse/ACTUATOR_NAME/events"
consumer = SSEConsumer(sse_url=SSE_URL)
```

manual launch (not in Actuator):

```python
import asyncio

events_queue = asyncio.Queue()
loop = asyncio.get_event_loop()
loop.create_task(consumer.listen(events_queue))
loop.run_forever()
```
