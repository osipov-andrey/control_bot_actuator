import logging

from collections import namedtuple
from typing import Iterable, List, Optional, Union

from .messages_tools import build_message


logger = logging.getLogger(__name__)
MessageTarget = namedtuple(
    "MessageTarget", "target_type, target_name, message_id", defaults=(None,)
)


class Issue:
    def __init__(self, id_: str, status: str, prefix: str = ""):
        self.id_ = self._add_prefix(id_, prefix)
        self.resolved = self._is_resolved(status)

    @staticmethod
    def _add_prefix(issue_id: str, prefix: str):
        """Добавляет префикс для issue_id"""
        return prefix + issue_id

    @staticmethod
    def _is_resolved(zabbix_event_status: str):
        """Проверяют статус issue. Issue - событие в Zabbix"""
        return True if zabbix_event_status.upper() == "RESOLVED" else False


class TelegramMessage:
    def __init__(
        self,
        _id: str,
        cmd: str,
        sender_name: str,
        *,
        target: MessageTarget,
        subject: str = "",
        text: str = "",
        images: Optional[List[str]] = None,
        document: Optional[dict] = None,
        issue: Optional[Issue] = None,
        commands: Optional[Union[str, dict]] = None,
        replies: Optional[Iterable] = None,
        reply_markup: Optional[List[dict]] = None,
        inline_edit_button: bool = False,
    ):
        """
        :param _id:                 id команды, инициирующей отправку сообщения
        :param cmd:                 команда, инициирующая отправку сообщения
        :param subject:             Заголовок сообщения
        :param text:                Текст сообщения
        :param target:              Адресат ("service", "channel", "user")

        :param images:              Какие картинки прикрепить (Base64-string)
        :param document:            Какой документ прикрепить:
                        {
                            "content": Str (Содержимое документа),
                            "filename": Str (Имя файла)
                            "caption":  Str (Описание файла)
                        }
                        !!!
                        Если в caption используется HTML-разметка - необходимо
                        сообщить об этом телеграм-боту, передав в поле text любой тэг.
                        Markdown необходимо экранировать.
                        !!!
        :param issue:   Уведомление о проблеме
                issue.id_:           ID события (использутся в уведомлениях)
                issue.status:        Статсус события (PROBLEM/RESOLVED)
        :param commands:            Описание команд, поддерживаеиых клиентом
                        {
                            "cmd": {
                                "args": [ (Список со словарями. 1 словарь - 1 аргумент)
                                    {
                                        "name": Str,
                                        "description": Str,
                                        "arg_type": Str ("int", "str", "choose"),
                                        "options": ["option1", "option2"...]
                                    },
                                ],
                                "description": Str (описание команды),
                                "verbose": Str (краткое описание команды)'
                            },
                            "cmd2": ...
                        }
        :param replies:             Сообщения, которые выведутся в телеграме как ответы на основное
        :param reply_markup:        Описание inline-buttons под сообщением
        """
        self._id = _id
        self.cmd = cmd
        self.sender_name = sender_name
        # **kwargs:
        self._images = images
        self._document = document
        self._issue = issue
        self._commands = commands
        self._replies = replies
        self._reply_markup = reply_markup
        self._target = target
        self._inline_edit_button = inline_edit_button
        self._text = self._build_message(subject, text)

    @property
    def payload(self) -> dict:
        return self._build_message_payload()

    def _build_message_payload(self) -> dict:
        """
        Строит JSON-payload, в соотвествии с API телеграм-бота.
        :return: payload-словарь
        """
        payload = {
            "cmd": self.cmd,
            "id": self._id,
            "text": self._text,
        }

        if self._commands:
            # Introduce
            payload["commands"] = self._commands

        if self._images:
            if len(self._images) == 1:
                payload["image"] = self._images[0]
            else:
                # Если изображений много - шлем их отдельными сообщениями
                # со ссылкой на первое сообщение (с текстом)
                replies = [{"image": image} for image in self._images]
                payload["replies"] = replies
        elif self._replies:
            payload["replies"] = [{"text": text} for text in self._replies]

        if self._document:
            payload["document"] = self._document

        if self._issue:
            payload["issue"] = {
                "issue_id": self._issue.id_,
                "resolved": self._issue.resolved,
            }

        if self._reply_markup:
            payload["reply_markup"] = self._reply_markup

        target = self._target._asdict()
        if not self._inline_edit_button:
            # используется только при редактировании сообщений из inline_button
            target.pop("message_id")
        payload["target"] = target

        return payload

    def _build_message(self, subject: str, text: str):
        return build_message(subject, text, self.sender_name)
