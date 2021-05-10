import asyncio
import httpx
import json
import logging

from asyncio import Queue

from cba.dispatcher import BaseDispatcherEvent
from cba.messages import MessageTarget


__all__ = ["SSEConsumer", "SSEEventParser"]

_LOGGER = logging.getLogger("SSE Consumer")


class SSEEventParser:
    """
    Класс для приведения разных библиотечных
    SSE-эвентов к единому виду.
    """

    def __init__(self, raw_text_command: str):

        raw_data = raw_text_command.rstrip("\r\n\r\n")
        fields = raw_data.split("\r\n")

        for field in fields:
            if not field:  # пустая строка
                continue
            field_name, field_data = map(lambda x: x.strip(), field.split(":", maxsplit=1))
            if field_name == "data":
                field_data = self._parse_data(field_data)
            setattr(self, field_name, field_data)

    def __call__(self, *args, **kwargs) -> BaseDispatcherEvent:
        if self.data and self.event:
            command = self.data["command"]
            target = MessageTarget(**self.data["target"])
            try:
                args = self.data["args"]
            except KeyError:
                args = {}
            behavior = self.data.get("behavior")
            return BaseDispatcherEvent(command, target, args, behavior)

    def __getattr__(self, item):
        return self.__dict__.get(item)

    @staticmethod
    def _parse_data(data: str) -> [dict, str]:
        try:
            dict_data = json.loads(data)
        except json.JSONDecodeError:
            return data
        return dict_data


class SSEConsumer:

    """
    Клиент SSE.
    Вызывает команды обратной связи.
    """

    def __init__(self, sse_url: str):
        self.url = sse_url

    @staticmethod
    async def callback(command: str, queue: Queue):
        """Парсит эвент и кладет в очерель в случае успеха"""
        raw_event = SSEEventParser(command)

        if raw_event.event in ("start", "slave"):
            _LOGGER.info("Get Event: %s %s", raw_event.event, raw_event.data)
            await queue.put(raw_event())  # Put BaseDispatcherEvent into queue

    async def listen(self, events_queue: Queue):

        while 1:
            try:
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        method="GET", url=self.url, timeout=35
                    ) as stream:  # heartbeat every 30s
                        stream.raise_for_status()
                        _LOGGER.info("Connected to SSE on %s", self.url)

                        async for message in stream.aiter_text():
                            _LOGGER.debug("Get data from stream: %s", message)
                            events = message.split("\r\n\r\n")
                            for event in events:
                                if event:
                                    await self.callback(event, events_queue)
            except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadError) as err:
                # I can't connect or the bot fell off
                _LOGGER.error(*err.args)
                await asyncio.sleep(20)
            except httpx.TimeoutException:
                _LOGGER.warning("Heartbeat waiting timeout!")
            finally:
                _LOGGER.info("Reconnecting...")
