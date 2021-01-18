## class BasePublisher(ABC), class HTTPPublisher(BasePublisher), class RabbitPublisher(BasePublisher)

Паблишеры отвечают за отправку сообщений в телеграм-бот.

Абстрактный класс _BasePublisher(ABC)_ определяет абстрактный метод
_publish_message_, который получает в качестве первого аргумента экземпляр класса 
_TelegramMessage_.

Паблишеры ничего не знаю о содержании и адресате сообщения(какой чат, какой пользователь и т.п.).
Они только отправляют сообщение в телеграм-бот по тому или иному каналу.


Инициализация:

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
