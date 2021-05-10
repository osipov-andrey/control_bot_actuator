import asyncio
import pytest

from cba.consumers import *
from cba.dispatcher import BaseDispatcherEvent
from cba.messages import MessageTarget


class TestSseEventParser:
    @pytest.mark.parametrize(
        "raw_cmd, attrs",
        [
            (
                "event: start\r\n"
                'data: {"command": "getAvailableMethods", '
                '"target": {"target_type": "service", "target_name": "hentest"}, '
                '"behavior": "service"}',
                {
                    "event": "start",
                    "data": {
                        "command": "getAvailableMethods",
                        "target": {"target_type": "service", "target_name": "hentest"},
                        "behavior": "service",
                    },
                },
            ),
            ('data: {"client_name": "hentest"}', {"data": {"client_name": "hentest"}}),
            ('data: "client_name": "hentest"}', {"data": '"client_name": "hentest"}'}),
        ],
    )
    def test_init(self, raw_cmd: str, attrs: dict):
        raw_event = SSEEventParser(raw_cmd)
        for key, value in attrs.items():
            assert raw_event.__getattr__(key) == value

    @pytest.mark.parametrize(
        "raw_cmd, event",
        [
            (
                "event: slave\r\n"
                'data: {"command": "adminOnly", '
                '"target": {"target_type": "user", "target_name": "172698654"}, '
                '"behavior": "admin", "args": {}}',
                BaseDispatcherEvent(
                    command="adminOnly",
                    target=MessageTarget(**{"target_type": "user", "target_name": "172698654"}),
                    args={},
                    behavior="admin",
                ),
            ),
            (
                "event: slave\r\n"
                'data: {"command": "HumanCallableArgs", '
                '"target": {"target_type": "user", "target_name": "172698654"}, '
                '"behavior": "user", "args": {"arg1": "321", "arg2": "qwerty"}}',
                BaseDispatcherEvent(
                    command="HumanCallableArgs",
                    target=MessageTarget(**{"target_type": "user", "target_name": "172698654"}),
                    args={"arg1": "321", "arg2": "qwerty"},
                    behavior="user",
                ),
            ),
        ],
    )
    def test_call(self, raw_cmd: str, event: BaseDispatcherEvent):
        raw_event = SSEEventParser(raw_cmd)
        roast_event = raw_event()
        assert roast_event.command == event.command
        assert roast_event.target == event.target
        assert roast_event.args == event.args
        assert roast_event.behavior == event.behavior


class TestSseConsumer:

    test_event = (
        "event: slave\r\n"
        'data: {"command": "HumanCallableArgs", '
        '"target": {"target_type": "user", "target_name": "172698654"}, '
        '"behavior": "user", "args": {"arg1": "321", "arg2": "qwerty"}}'
    )

    @pytest.fixture
    def get_events(self):
        events_queue = asyncio.Queue()

        def _get_events(events=1):
            raw_events_text = "\r\n\r\n".join(self.test_event for _ in range(events))
            events_queue.put_nowait(raw_events_text)
            return events_queue

        yield _get_events
