import aioamqp
import logging
import httpx
import json

from abc import ABC, abstractmethod

from cba import exceptions
from cba.messages import TelegramMessage


__all__ = ["BasePublisher", "HTTPPublisher", "RabbitPublisher"]

_LOGGER = logging.getLogger(__name__)


class BasePublisher(ABC):
    @abstractmethod
    async def publish_message(self, message: TelegramMessage):
        """
        Этот метод должен инкапуслировать отправку готового сообщения
        со всеми полями payload в телеграм
        """
        ...


class HTTPPublisher(BasePublisher):
    """HTTP-клиент"""

    def __init__(self, url: str, headers: dict = None, *args, **kwargs):
        """
        :param url: Куда будет отправлять POST-запросы
        :param headers: С какими заголовками
        """
        super().__init__(*args, **kwargs)
        self.url = url
        self.headers = headers if headers else {}

    async def publish_message(self, message: TelegramMessage, queue: str = "telegram"):
        json_message = {
            "queue": queue,
            "payload": message.payload,
        }
        _LOGGER.debug("TO Telegram via HTTP-client: %s", json_message)
        await self._post_http(self.url, json_=json_message, headers=self.headers)

    @staticmethod
    async def _post_http(
        url: str,
        data: str = None,
        json_: dict = None,
        headers: dict = None,
    ):
        try:
            async with httpx.AsyncClient() as client:
                request = await client.post(url, data=data, json=json_, headers=headers)
            return request.status_code, request.text
        except (httpx.ConnectTimeout, httpx.ConnectError):
            raise exceptions.HTTPClientConnectException


class RabbitPublisher(BasePublisher):
    """Для теста. Пишет сразу в RabbitMQ"""

    def __init__(self, host, port, *args, login, pwd, queue, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.login = login
        self.password = pwd
        self.queue = queue

    @staticmethod
    def save_json(payload: dict):
        with open("message.json", "w") as f:
            json.dump(payload, f)

    async def publish_message(self, message: TelegramMessage, queue=None):

        payload = message.payload

        if not queue:
            queue = self.queue

        transport, protocol = await aioamqp.connect(
            self.host, self.port, login=self.login, password=self.password, login_method="PLAIN"
        )
        try:
            channel = await protocol.channel()
            _LOGGER.debug(
                "Send message to RabbitMQ:\n%s",
                "\n".join(f"{key}: {value}" for key, value in payload.items()),
            )
            payload = json.dumps(payload)
            await channel.publish(payload, "", queue)
            _LOGGER.debug("Send message - OK")
        finally:
            await protocol.close()
            transport.close()
