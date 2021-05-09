## class BasePublisher(ABC), class HTTPPublisher(BasePublisher), class RabbitPublisher(BasePublisher)

Publishers are responsible for sending messages to the control bot.

The abstract class _BasePublisher(ABC)_ defines an abstract 
method _publish_message_ that receives an instance of 
the _TelegramMessage_ class as its first argument.

Publishers do not know anything about the content and recipient 
of the message (which chat, which user, etc.).
They only send a message to the control bot over one channel or another.


Initialization:

```python
from cba.publishers import HTTPPublisher, RabbitPublisher


http_publisher = HTTPPublisher(url="http://localhost:8081/inbox")

rabbit_publisher = RabbitPublisher(
    host="localhost",
    port=5672,
    login="login",
    pwd="pwd",
    queue="telegram"
)
```
