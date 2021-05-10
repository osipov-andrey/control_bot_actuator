import asyncio
import logging

from typing import List, Union

from cba.consumers import SSEConsumer
from cba.dispatcher import CommandsDispatcher
from cba.helpers import ClientInfo
from cba.publishers import BasePublisher


_LOGGER = logging.getLogger(__name__)


class Actuator:
    """Класс для связывания получаетеля команд и их диспетчера"""

    def __init__(
        self,
        name: str,
        *,
        consumer: SSEConsumer,
        dispatcher: CommandsDispatcher,
        publishers: Union[BasePublisher, List[BasePublisher], None] = None,
        verbose_name="",
        hide_name=False,
    ):
        self.client_info = ClientInfo(name, verbose_name, hide_name)
        self.consumer = consumer
        self.publishers = publishers
        self.dispatcher = dispatcher
        self._running = False

        self.dispatcher.introduce(self.client_info)
        if publishers:
            self.dispatcher.set_publishers(publishers)

    def run(self, loop=None):
        if not loop:
            loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.exception_handler)
        queue = asyncio.Queue()

        loop.create_task(self._set_running())
        loop.create_task(self.dispatcher.events_reader(events_queue=queue))
        loop.create_task(self.consumer.listen(events_queue=queue))

        loop.run_forever()

    def exception_handler(self, loop, context):
        if self._running:
            self._running = False
            exc = context["exception"]
            exc_info = (type(exc), exc, exc.__traceback__)
            _LOGGER.critical(exc, exc_info=exc_info)
            loop.stop()

    async def _set_running(self):
        self._running = True
        _LOGGER.info("Telegram lever started")
