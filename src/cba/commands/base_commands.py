"""
Модуль с классами команд.

Иерархия базовых классов команд:
                     >>>BaseCommand
                      /           \
                     /             \
                    /               \
                   /                 \
                  /                   \
>>>HumanCallableCommandWithArgs     >>>ServiceCommand

Команды инстанцируются не вызовами конструкторов классов, а через класс-диспетчер:
CommandsDispatcher
методом dispatch(), в который передается SSE-Event в качестве аргумента.

Аргументы команд определются в классах соответствующих
команд инстанцированием класса Arg
"""

import datetime
import logging
import uuid

from abc import ABC, abstractmethod
from typing import List, Tuple, Type, Optional

from cba import exceptions
from cba.commands.commands_tools import load_json_template
from cba.messages import TelegramMessage, MessageTarget, parse_and_paste_emoji
from cba.publishers import BasePublisher
from cba.helpers import ClientInfo

from . import arguments


logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """
    Базовый класс команд обратной связи.
    Для создания новой команды просто отпределите класс-наследник.
    """

    EMOJI = ">>Not_classified<<"  # Эмоджи команды
    ARGS = tuple()  # Описание аргументво команды
    JSON_TMPL_FILE: str = None  # Файл с шаблоном JSON-запроса к API
    PATH_TO_FILE: str = None  # Путь к файлу с пользовательскими командами
    CMD: str  # Команда в telegram
    HUMAN_CALLABLE: bool  # Могут ли вызывать пользователи?
    hidden = False
    admin_only = False
    behavior__admin: Optional[Type["BaseCommand"]] = None

    @classmethod
    def hide(cls):
        cls.hidden = True

    @classmethod
    def show(cls):
        cls.hidden = False

    @classmethod
    def mark_as_admin_only(cls):
        if cls.behavior__admin is not None:
            raise AttributeError("The command is already has admin behaviour!")
        cls.admin_only = True
        cls.behavior__admin = cls

    @classmethod
    def admin_behavior(cls, command: Type["BaseCommand"]):
        """Class decorator"""
        if cls.admin_only:
            raise AttributeError("The command is already only for the admin!")
        command.CMD = cls.CMD
        cls.behavior__admin = command
        return command

    def __init__(
        self,
        *args,
        target: MessageTarget,
        client_info: ClientInfo,
        publishers: List[BasePublisher],
        parent_id: Optional[str] = None,
        command_args: Optional[dict] = None,
        **kwargs,
    ):
        """
        :param args: используются для передачи аргументов команд.
        :param kwargs: используется для передачи аргументов методов классов команд.
        """
        self.inline_buttons = list()
        if self.JSON_TMPL_FILE:
            self.template: dict = load_json_template(self.JSON_TMPL_FILE, self.PATH_TO_FILE)
        self.target: MessageTarget = target
        self.client_info = client_info
        self.publishers = publishers
        self.id = self._generate_id()
        self.parent_id = parent_id
        self.command_args = command_args
        log_marker = f"{'='*20} {client_info.name} {'='*20}"
        logger.info(
            "\n%s\nCreated command-instance [%s]\n"
            "Args: %s\ntarget: %s\nkwargs: %s\nid: %s\nparent_id: %s\n%s\n",
            log_marker,
            self.CMD,
            args,
            target,
            kwargs,
            self.id,
            self.parent_id,
            log_marker,
        )

    def create_subcommand(
        self,
        cmd_type: Type["BaseCommand"],
        *args,
        target: Optional[MessageTarget] = None,
        client_info: Optional[ClientInfo] = None,
        publishers: Optional[List[BasePublisher]] = None,
        command_args: Optional[dict] = None,
        **kwargs,
    ) -> "BaseCommand":

        if not target:
            target = self.target
        if not client_info:
            client_info = self.client_info
        if not publishers:
            publishers = self.publishers
        if not command_args:
            command_args = dict()

        return cmd_type(
            *args,
            target=target,
            client_info=client_info,
            publishers=publishers,
            command_args=command_args,
            parent_id=self.id,
            **kwargs,
        )

    async def send_message(self, target: MessageTarget = None, **kwargs):
        if not self.publishers:
            raise AttributeError("Can't send message without publishers!")
        if not target:
            target = self.target

        sender_name = self._check_sender_name()
        message = TelegramMessage(str(self.id), self.CMD, sender_name, target=target, **kwargs)

        for publisher in self.publishers:
            await publisher.publish_message(message)

    def _check_sender_name(self):
        if self.client_info.hide_name:
            sender_name = ""
        elif self.client_info.verbose_name:
            sender_name = self.client_info.verbose_name
        else:
            sender_name = self.client_info.name
        return sender_name

    def add_inline_button(self, command_type: Type["BaseCommand"], text: str, *args):
        """Добавляет информацию о необходимых кнопках в чатботе после сообщения"""
        button_info = {
            "text": parse_and_paste_emoji(text),
            "callback_data": self.reverse_command(command_type, *args),
        }
        self.inline_buttons.append(button_info)

    def reverse_command(self, command: Type["BaseCommand"], *args):
        """Создает строковую команду"""
        # TODO проверку команд
        cmd = command.CMD
        reversed_cmd = f"/{self.client_info.name}_{cmd}_{'_'.join(str(arg) for arg in args)}"
        if reversed_cmd.endswith("_"):
            reversed_cmd = reversed_cmd[:-1]
        return reversed_cmd

    @abstractmethod
    async def _execute(self):
        """Бизнес-логика"""
        ...

    async def execute(self):
        """
        Обертка-интерфейс над бизнес-логикой.
        В пользовтаельских классах-командах тут можно определять
        обработку пользовательских исключений.
        Пользовательский исключения должны быть подклассом exceptions.UserException
        """
        return await self._execute()

    @classmethod
    def description(cls, client_name):
        """Описание команды"""
        return (
            f"{cls.EMOJI} {'<b>(admin)</b>' if cls.admin_only else ''} "
            f"/{client_name}_{cls.CMD} - {cls.__doc__.strip()}"
        )

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        for arg in self.__dict__.keys():
            try:
                if self.__dict__[arg] != other.__dict__[arg]:
                    return False
            except KeyError:
                return False
        return True

    @staticmethod
    def from_ts(ts):
        return str(datetime.datetime.fromtimestamp(int(ts)))

    @staticmethod
    def _generate_id():
        return uuid.uuid4()


class HumanCallableCommandWithArgs(BaseCommand, ABC):
    """Подкласс для определения команд, которые вызываются с аргументами"""

    HUMAN_CALLABLE = True
    ARGS: Tuple[arguments.Arg] = tuple()

    def __init__(self, *args, command_args, **kwargs):
        super().__init__(*args, **kwargs)

        current_args = self._set_args(command_args)
        for arg_name, arg_value in current_args.items():
            # Устанавливаю полученные атрибуты команды в атрибуты экземпляра класса
            setattr(self, arg_name, arg_value)

    def validate(self):
        """
        Валидация аргументов.
        В случае неудачной валидации возвращает соответствующую служебную команду.
        """
        wrong_arguments = self._validate()
        if wrong_arguments:
            return self.create_subcommand(WrongArguments, wrong_arguments)
        return self

    @classmethod
    def args_description(cls) -> dict:
        return {arg.name: arg.arg_info for arg in cls.ARGS}

    def _set_args(self, args: dict) -> dict:
        """Заменить дефолтные аргументы на полученные при вызове команды"""
        default_args = {arg.name: arg.default for arg in self.ARGS}

        for arg_name, arg_value in args.items():
            if arg_name not in default_args:
                # TODO: какой-нибудь свой эксепшн
                raise ValueError("Unexpected Argument!")
            default_args[arg_name] = arg_value

        missing_args = []

        for arg_name, arg_value in default_args.items():
            if not arg_value:
                missing_args.append(arg_name)
        if missing_args:
            raise exceptions.NotEnoughArgumentsError(missing_args)

        return default_args

    def _validate(self) -> list:
        """
        Конкретная логика валидации аргументов для каждой команды.
        Валидация аргументов осуществляется в боте. Нам нужно только передать
        боту описание аргументов в виде схемы в соотвествии с библиотекой Cerberus.
        Однако, если какие-то параметры невозможно валидировать на стороне бота -
        можно описать валидацию переопределив данный метод в классе команды.
        """
        pass

    def __getattr__(self, item):
        """Чтобы PyCharm не ругался на отсутствие атрибутов"""
        return self.__dict__[item]


class ServiceCommand(BaseCommand, ABC):
    """Подкласс для определения служебных команд"""

    HUMAN_CALLABLE = False

    async def execute(self, *args, **kwargs):
        """Служебной команде не к чему вызывать другие служебные"""
        return await self._execute()


class WrongArguments(ServiceCommand):
    """Вызывается автоматически при отправке невалидных аргументов.\n"""

    EMOJI = ">>WARNING<<"
    CMD = "WrongArguments"

    def __init__(self, wrong_arguments: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrong_arguments = wrong_arguments

    async def _execute(self):
        await self.send_message(
            subject=f"{self.EMOJI} Wrong arguments",
            text=", ".join(self.wrong_arguments),
        )


class NotEnoughArguments(ServiceCommand):
    """Вызывается автоматически при нехватке аргументов.\n"""

    EMOJI = ">>WARNING<<"
    CMD = "NotEnoughArguments"

    def __init__(self, missing_args: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.missing_args = missing_args

    async def _execute(self):
        await self.send_message(
            subject=f"{self.EMOJI} Not Enough arguments",
            text=", ".join(self.missing_args),
        )


class WrongCommand(ServiceCommand):
    """Вызывается автоматически при отправке невалидных аргументов.\n"""

    EMOJI = ">>WARNING<<"
    CMD = "WrongCommand"

    async def _execute(self):
        await self.send_message(
            subject=f"{self.EMOJI} Wrong command!",
            text="Try again!",
        )


class InternalError(ServiceCommand):
    """Вызывается автоматически при нехватке аргументов.\n"""

    EMOJI = ">>Disaster<<"
    CMD = "InternalError"

    def __init__(self, exception_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception_info = exception_info

    async def _execute(self):
        subject = f"{self.EMOJI} Telegram lever get in self in trouble! Please, tell to your admin."
        text = str(self.exception_info.__class__.__name__) + " " + str(self.exception_info)
        await self.send_message(
            subject=subject,
            text=text,
        )


class BadJSONTemplateCommand(ServiceCommand):
    """
    Некоторые JSON-шаблоны допускается редактировать во время работы программы.
    Данная команда вызывается автоматически при ошибке в JSON-шаблоне.
    """

    EMOJI = ">>DISASTER<<"
    CMD = "BadJSONError"

    def __init__(self, *args, template="", **kwargs):
        super().__init__(*args, **kwargs)
        self.template = template

    async def _execute(self):
        await self.send_message(
            subject=f"{self.EMOJI} Bad JSON-Template!",
            text=f"{self.template}",
        )


def admin_only(cls: "BaseCommand"):
    """
    Отметить команду как доступную только админу.
    Т.е. чат-бот будет добавлять ее в главное меню киента только для админов.
    """
    cls.mark_as_admin_only()
    return cls


def hide(cls: "BaseCommand"):
    """
    Отметить команду как "спрятанную".
    Т.е. чат-бот о ней знает, но в главное меню клиента не будет ее добавлять.
    """
    cls.hide()
    return cls
