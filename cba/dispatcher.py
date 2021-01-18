import asyncio
import logging
from enum import Enum
from typing import Iterable, List, Type, Union

from cba import commands, exceptions
from cba.commands import BaseCommand, hide
from cba.messages import MessageTarget
from cba.publishers import BasePublisher
from cba.helpers import ClientInfo


__all__ = [
    "BaseDispatcherEvent",
    "CommandsDispatcher"
]

_INTRO_COMMAND = 'getAvailableMethods'
_LOGGER = logging.getLogger(__name__)


class Behaviors(Enum):
    USER = "user"
    ADMIN = "admin"


class BaseDispatcherEvent:
    """
    Все попадающие в диспетчер эвенты должны
    соответствовать протоколу данного класса
    """
    def __init__(self,
                 command: str,
                 target: MessageTarget,
                 args: dict,
                 behavior: str
                 ):
        assert target.target_type in ("user", "channel", "service")
        self._command = command
        self._target = target
        self._args = args
        self._behavior = behavior

    @property
    def command(self) -> str:
        return self._command

    @property
    def target(self) -> MessageTarget:
        return self._target

    @property
    def args(self) -> dict:
        return self._args

    @property
    def behavior(self) -> str:
        return self._behavior


class CommandsDispatcher:
    """ После получения команды из telegram возвращает соотвествующий инстанс """

    def __init__(self):
        self.client_info = None
        self.callable_commands = list()
        self.service_commands = [Introduce, ]
        self.publishers = list()

    def set_publishers(self, publishers: Union[BasePublisher, List[BasePublisher]]):
        """ Установить паблишеры. через которые будут отправляться сообщения """
        if isinstance(publishers, Iterable):
            self.publishers.extend(publishers)
        else:
            self.publishers.append(publishers)

    def introduce(self, client_info: ClientInfo):
        """
        Установить от какого имени будет работать диспетчер
        и будут отправляться сообщения
        """
        self.client_info = client_info

    async def events_reader(self, events_queue: asyncio.Queue):
        while 1:
            event = await events_queue.get()
            asyncio.ensure_future(self.dispatch(event))
            events_queue.task_done()

    def register_callable_command(self, cmd: Type[commands.BaseCommand]):
        """
        Зарегистрировать команду, которую можно будет вызывать через диспетчер из телеграм
        (она попадет в Introduce)
        """
        self.callable_commands.append(cmd)
        return cmd

    def register_service_command(self, cmd: Type[commands.BaseCommand]):
        """
        Зарегистрировать команду, которую можно будет вызывать через диспетчер,
        но чат-бот не будет о ней знать
        (она НЕ попадет в Introduce)
        """
        self.service_commands.append(cmd)
        return cmd

    async def dispatch(self, event: BaseDispatcherEvent):
        command = event.command
        cmd_kwargs = {
            "command_args": event.args,
            "target": event.target,
            "client_info": self.client_info,
            "publishers": self.publishers,
        }

        if command == _INTRO_COMMAND:
            cmd_kwargs["commands_"] = self.callable_commands

        try:
            all_commands = self.callable_commands + self.service_commands
            cmd_type = list(filter(lambda x: x.CMD == command, all_commands))[0]
            if event.behavior == Behaviors.ADMIN.value:
                cmd_type = cmd_type.behavior__admin
            cmd = cmd_type(**cmd_kwargs)
            if cmd.ARGS:
                cmd = cmd.validate()
            return await cmd.execute()
        except IndexError:
            _LOGGER.warning("Get wrong command!", exc_info=True)
            return await commands.WrongCommand(**cmd_kwargs).execute()
        except exceptions.NotEnoughArgumentsError as err:
            # Переданы не все обязательные аргументы
            _LOGGER.warning("Not enough arguments!", exc_info=True)
            return await commands.NotEnoughArguments(err.missing_args, **cmd_kwargs).execute()
        except exceptions.BadCommandTemplateException as err:
            # Загрузка шаблонов происходит и до вызова метода execute() у команд
            await commands.BadJSONTemplateCommand(
                template=err.file_name, **cmd_kwargs
            ).execute()
            raise
        except BaseException as err:
            await commands.InternalError(err, **cmd_kwargs).execute()
            raise


@hide
class Introduce(commands.BaseCommand):
    """ Передает информацию о поддерживаемых командах. Вызывается сервером автоматически.\n """
    EMOJI = '>>WARNING<<'
    CMD = _INTRO_COMMAND
    #TODO: send service description
    def __init__(self, *args, commands_: list, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = commands_

    def collect_commands_to_json(self) -> dict:

        commands_dict = {
            cmd.CMD: self._get_cmd_full_description(cmd)
            for cmd in self.commands
        }

        return commands_dict

    def _get_cmd_full_description(self, cmd: Type['BaseCommand']) -> dict:
        description = {
            "hidden": cmd.hidden
        }

        if cmd.admin_only:
            description["behavior__admin"] = self._get_cmd_behavior(cmd)
        elif cmd.behavior__admin:
            description["behavior__admin"] = self._get_cmd_behavior(cmd.behavior__admin)
            description["behavior__user"] = self._get_cmd_behavior(cmd)
        else:
            description["behavior__user"] = self._get_cmd_behavior(cmd)
        return description

    def _get_cmd_behavior(self, cmd: Type['BaseCommand']) -> dict:
        # noinspection PyUnresolvedReferences
        return {
                'args': cmd.args_description() if cmd.ARGS else {},
                'description': commands.parse_and_paste_emoji(
                    cmd.description(self.client_info.name)
                ),
            }

    async def _execute(self):
        client_commands = self.collect_commands_to_json()
        await self.send_message(
            subject='Introducing commands',
            commands=client_commands,
        )

