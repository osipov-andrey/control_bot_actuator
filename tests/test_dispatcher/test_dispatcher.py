import pytest
from typing import Type

from cba.commands import (
    WrongCommand,
    NotEnoughArguments,
    WrongArguments,
    BadJSONTemplateCommand,
    InternalError,
)
from cba.dispatcher import CommandsDispatcher, ClientInfo, BaseDispatcherEvent, Introduce
from cba.exceptions import BadCommandTemplateException
from conftest import *


class TestDispatcher:
    def test_set_publishers(self, test_publisher):
        d = CommandsDispatcher()
        d.set_publishers([test_publisher, test_publisher])
        assert d.publishers == [test_publisher, test_publisher]

    def test_set_publisher(self, test_publisher):
        d = CommandsDispatcher()
        d.set_publishers(test_publisher)
        assert d.publishers == [
            test_publisher,
        ]

    def test_introduce(self):
        d = CommandsDispatcher()
        d.introduce(ClientInfo(name="test"))
        assert d.client_info.name == "test"

    def test_register_callable_command(self):
        d = CommandsDispatcher()

        @d.register_callable_command
        class Cmd(BaseCommand):
            ...

        assert Cmd in d.callable_commands

    def test_register_service_command(self):
        d = CommandsDispatcher()

        @d.register_service_command
        class Cmd(BaseCommand):
            ...

        assert Cmd in d.service_commands

    @pytest.mark.parametrize("str_event, cmd_class", test_str_events)
    def test_get_command(self, str_event: str, cmd_class: Type[BaseCommand]):
        cmd_kwargs, event = get_event_and_cmd_kwargs(str_event)
        cmd = dispatcher._get_command(event.command, event.behavior, **cmd_kwargs)
        assert isinstance(cmd, cmd_class)

    def test_get_commands_wrong_command(self):
        cmd_kwargs, event = get_event_and_cmd_kwargs(event_with_wrong_cmd)
        cmd = dispatcher._get_command(event.command, event.behavior, **cmd_kwargs)
        assert isinstance(cmd, WrongCommand)

    def test_get_commands_not_enough_args(self):
        cmd_kwargs, event = get_event_and_cmd_kwargs(event_with_not_enough_args)
        cmd = dispatcher._get_command(event.command, event.behavior, **cmd_kwargs)
        assert isinstance(cmd, NotEnoughArguments)
        assert cmd.missing_args == [
            "arg2",
        ]

    def test_get_commands_not_valid(self):
        cmd_kwargs, event = get_event_and_cmd_kwargs(event_with_not_valid_args)
        cmd = dispatcher._get_command(event.command, event.behavior, **cmd_kwargs)
        assert isinstance(cmd, WrongArguments)
        assert cmd.wrong_arguments == ["qwerty", "321"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("event, cmd_class", test_events)
    async def test_dispatch(self, event: BaseDispatcherEvent, cmd_class: Type[BaseCommand], mocker):
        mocker.patch(f"{cmd_class.__module__}.{cmd_class.__name__}._execute")
        await dispatcher.dispatch(event)
        cmd_class._execute.assert_called()

    @pytest.mark.asyncio
    async def test_dispatch_bad_template(self, mocker):
        cls = BadJSONTemplateCommand
        mocker.patch(f"{cls.__module__}.{cls.__name__}._execute")
        with pytest.raises(BadCommandTemplateException):
            await dispatcher.dispatch(event_bad_template)
            cls._execute.assert_called()

    @pytest.mark.asyncio
    async def test_dispatch_internal_error(self, mocker):
        cls = InternalError
        mocker.patch(f"{cls.__module__}.{cls.__name__}._execute")
        with pytest.raises(BaseException):
            await dispatcher.dispatch(event_internal_error)
            cls._execute.assert_called()

    @pytest.mark.asyncio
    async def test_dispatch_introduce(self, mocker):
        spy = mocker.spy(CommandsDispatcher, "_get_command")
        mocker.patch(f"{Introduce.__module__}.{Introduce.__name__}._execute")
        await dispatcher.dispatch(event_introduce_cmd)
        assert spy.call_count == 1
        assert "commands_" in spy.call_args.kwargs.keys()
