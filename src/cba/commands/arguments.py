from abc import ABC, abstractmethod
from typing import Optional, List, Union


__all__ = [
    "String",
    "Integer",
    "ListArg",
    "MyUser",
]


class Arg(ABC):
    """Определяет один аргумент команды"""

    BOT_ARG_TYPE: str

    def __init__(
        self,
        name: str,
        description: str,
        *,
        default: Optional[Union[str, int]] = None,
        example: Optional[str] = None,
        options: Optional[List[Union[str, int]]] = None,
        allowed: Optional[List[Union[str, int]]] = None,
        allow_options=False,
    ):
        """

        :param name: имя аргумента. Оно станет атрибутом экземпляра команды.
        :param description: описание аргумента.
        :param default: значение по-умолчанию
        :param example: пример значений. Подставляется в описание аргумента.
        :param options: варианты для выбора. Отобразятся кнопками под сообщением в телеграм боте.
        :param allowed: допустимые варианты для валидации на стороне телеграм-бота.
        :param allow_options: сделать допустимыми те, что перечислены в options.
        """

        self.default = default
        self.name = name
        self._description = description
        self._example = example

        self._options = options
        self._allowed = allowed
        if allow_options:
            self._allowed = options

    @property
    def arg_info(self) -> dict:
        arg_info = {
            "description": self._build_description(),
            "schema": self._build_schema(),
        }
        if self._options:
            arg_info["options"] = self._options
        return arg_info

    def _build_description(self) -> str:
        description = self._description
        if self._example:
            description += f" <i>[{self._example}]</i>"

        return description

    def _build_schema(self) -> dict:
        schema = self._create_schema()
        if self._allowed:
            schema["allowed"] = self._allowed
        return schema

    @abstractmethod
    def _create_schema(self) -> dict:
        ...

    def __repr__(self):
        return f'Arg(name="{self.name}", description="{self._build_description()}")'


class Integer(Arg):
    BOT_ARG_TYPE = "integer"

    def __init__(self, *args, minimum=None, maximum=None, **kwargs):
        """
        :param minimum: минимальное значение аргумента.
        :param maximum: максимальное значение аргумента.
        """
        super().__init__(*args, **kwargs)
        self.minimum = minimum
        self.maximum = maximum

    def _create_schema(self) -> dict:
        schema = {
            "type": self.BOT_ARG_TYPE,
        }
        if self.maximum:
            schema["max"] = self.maximum
        if self.minimum:
            schema["min"] = self.minimum
        return schema


class String(Arg):
    BOT_ARG_TYPE = "string"

    def __init__(self, *args, regex=None, **kwargs):
        """
        :param regex: Регулярное выражение, которому должно соответствовать значение аргумента
        """
        super().__init__(*args, **kwargs)
        self.regex = regex

    def _create_schema(self) -> dict:
        schema = {
            "type": self.BOT_ARG_TYPE,
        }
        if self.regex:
            schema["regex"] = self.regex
        return schema


class ListArg(Arg):
    BOT_ARG_TYPE = "list"

    def _create_schema(self) -> dict:
        return {"type": "list"}


class MyUser(Integer):
    """ID пользователя телеграм, у которого есть доступ к командам клиента"""

    def _create_schema(self) -> dict:
        schema = super(MyUser, self)._create_schema()
        schema["is_client"] = True
        return schema
