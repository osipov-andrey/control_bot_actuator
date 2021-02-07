from typing import Tuple

import pytest
from cba.consumers import SSEEventParser
from cba.dispatcher import BaseDispatcherEvent, Introduce
from cba.helpers import ClientInfo
from cba.publishers import HTTPPublisher

from testing.test_service.test_commands import *


dispatcher.set_publishers(HTTPPublisher(url="", headers={}))
dispatcher.introduce(ClientInfo("test"))

__all__ = [
    'dispatcher',
    'BaseCommand',
    'test_publisher',
    'test_str_events',
    'test_events',
    'get_event_and_cmd_kwargs',
    'event_with_wrong_cmd',
    'event_with_not_enough_args',
    'event_with_not_valid_args',
    'event_bad_template',
    'event_internal_error',
    'event_introduce_cmd',
]


raw_event_introduce_cmd = 'event: start\r\ndata: {"command": "getAvailableMethods", "target": {"target_type": "service", "target_name": "hentest"}, "behavior": "service"}'
event_introduce_cmd = SSEEventParser(raw_event_introduce_cmd)()
event_with_wrong_cmd = 'event: slave\r\ndata: {"command": "kek", "target": {"target_type": "user", "target_name": "172698654"}, "behavior": "user", "args": {"adminArg": "qwerty"}}'
event_with_not_enough_args = 'event: slave\r\ndata: {"command": "HumanCallableArgs", "target": {"target_type": "user", "target_name": "172698654"}, "behavior": "user", "args": {"arg1": "321"}}'
event_with_not_valid_args = 'event: slave\r\ndata: {"command": "HumanCallableArgs", "target": {"target_type": "user", "target_name": "172698654"}, "behavior": "user", "args": {"arg2": "321", "arg1": "qwerty"}}'
event_bad_template = 'event: slave\r\ndata: {"command": "badTemplate", "target": {"target_type": "user", "target_name": "172698654"}, "behavior": "user", "args": {}}'
event_bad_template = SSEEventParser(event_bad_template)()
event_internal_error = 'event: slave\r\ndata: {"command": "InternalError", "target": {"target_type": "user", "target_name": "172698654"}, "behavior": "user", "args": {}}'
event_internal_error = SSEEventParser(event_internal_error)()

test_str_events = [
    (
        'event: slave\r\ndata: {"command": "behavior", "target": {"target_type": "user", "target_name": "172698654"}, "behavior": "admin", "args": {"adminArg": "qwerty"}}',
        TestDifferentBehaviorAdmin
    ),
    (
        'event: slave\r\ndata: {"command": "behavior", "target": {"target_type": "user", "target_name": "172698654"}, "behavior": "user", "args": {"adminArg": "qwerty"}}',
        TestDifferentBehavior
    ),
    (
        raw_event_introduce_cmd,
        Introduce
    )
]

test_events = [
    (
        SSEEventParser(record[0])(),
        record[1]
    ) for record in test_str_events
]


@pytest.fixture
def test_publisher():
    yield HTTPPublisher(url="", headers={})


def get_event_and_cmd_kwargs(str_event: str) -> Tuple[dict, BaseDispatcherEvent]:
    raw_event = SSEEventParser(str_event)
    event = raw_event()
    cmd_kwargs = {
        "command_args": event.args,
        "target": event.target,
        "client_info": ClientInfo("test"),
        "publishers": HTTPPublisher(url="", headers={}),
        "commands_": []  # For Introduce
    }
    return cmd_kwargs, event
