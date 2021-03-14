import asyncio
import base64
import random

from cba.dispatcher import CommandsDispatcher
from cba.commands import MessageTarget, arguments
from cba.commands.base_commands import (
    BaseCommand, HumanCallableCommandWithArgs, ServiceCommand, hide, admin_only
)
from cba.messages import Issue


dispatcher = CommandsDispatcher()


@dispatcher.register_callable_command
class TestDifferentBehavior(BaseCommand):
    """ Тестовая команда с разным поведением для админа и юзверя - вы юзер """
    CMD = "behavior"

    async def _execute(self):
        await self.send_message(
            subject="Вы не админ",
        )


@TestDifferentBehavior.admin_behavior
class TestDifferentBehaviorAdmin(HumanCallableCommandWithArgs):
    """ Тестовая команда с разным поведением для админа и юзверя - вы админ """
    ARGS = (
        arguments.String("adminArg", "админский аргумент"),
    )

    async def _execute(self):
        await self.send_message(
            subject=f"Вы админ. Ваш аргумент: {self.adminArg}",
        )


@dispatcher.register_callable_command
class TestHumanCallableCommandWithReplies(BaseCommand):
    """ Тестовая команда с ответами """
    CMD = 'replies'

    async def _execute(self):
        replies = [f"Replies №:{i}" for i in range(3)]
        await self.send_message(
            subject="Replies test",
            replies=replies,
        )


@dispatcher.register_callable_command
class TestHumanCallableCommandWithIssue(BaseCommand):
    """ Тестовая команда отправки уведомлений """
    CMD = 'issue'
    ISSUE_PREFIX = 'test-'

    async def _execute(self):
        issue_id = str(random.randint(0, 1000))

        problem_text = ">>Disaster<< We have a problem!"
        problem_issue = Issue(issue_id, 'PROBLEM', self.ISSUE_PREFIX)
        await self.send_message(
            subject=problem_text,
            issue=problem_issue,
        )

        await asyncio.sleep(2)

        resolved_issue = Issue(issue_id, 'RESOLVED', self.ISSUE_PREFIX)
        resolved_text = ">>OK<< The problem is not with us ))0"
        await self.send_message(
            subject=resolved_text,
            issue=resolved_issue,
        )


@dispatcher.register_callable_command
class TestHumanCallableCommandWithBadTemplate(BaseCommand):
    """ Тестовая команда с `плохим` JSON-шаблоном """
    CMD = 'badTemplate'
    JSON_TMPL_FILE = 'bad_template.json'
    PATH_TO_FILE = __file__

    async def _execute(self):
        ...


@dispatcher.register_callable_command
class TestHumanCallableCommandWithGoodTemplate(BaseCommand):
    """ тестовая команда с `хорошим` JSON-шаблоном """
    CMD = 'goodTemplate'
    JSON_TMPL_FILE = 'good_template.json'
    PATH_TO_FILE = __file__

    async def _execute(self):
        await self.send_message(
            subject='Good template',
            text=str(self.template),
        )


@dispatcher.register_callable_command
class TestHumanCallableCommandWithAliases(BaseCommand):
    """ Тестовая команда с алиасами (макросами) дргуих команд """
    CMD = 'Aliases'

    async def _execute(self):
        text = f"\n{self.reverse_command(TestHumanCallableCommandWithArgs, '321', 'qwerty')}" \
               f"\n{self.reverse_command(TestCommandToSendDocument)}" \
               f"\n{self.reverse_command(TestCommandToSendOneImage)}" \
               f"\n{self.reverse_command(TestHumanCallableCommandWithArgsChoose)}"
        await self.send_message(
            subject="Шаблоны других тестовых команд",
            text=text,
        )


@dispatcher.register_callable_command
class TestHumanCallableCommandWithArgsChoose(HumanCallableCommandWithArgs):
    """ Тестовая команда с выбором аргументов """
    CMD = 'HumanCallableChoose'
    ARGS = (
        arguments.String('test_arg', "Тестовый аргумент с возможностью выбора",
                         options=['val1', 'val2', 'val3']),
    )

    async def _execute(self):
        message = f"Вы выбрали test_arg = {self.test_arg}"
        await self.send_message(text=message)


@dispatcher.register_callable_command
class TestHumanCallableCommandWithInlineButtons(BaseCommand):
    """ Тестовая команда с inline-кнопками """
    CMD = 'InlineButtons'

    async def _execute(self):
        for i in range(3):
            self.add_inline_button(
                TestHumanCallableCommandWithArgs,
                f">>info<< {i}", i, "test")
        self.add_inline_button(
            InlineButtonForEdit, "Try me, change me"
        )
        await self.send_message(
            subject="Кнопки под сообщением, 3 штуки, вызываемые",
            reply_markup=self.inline_buttons,
        )


@dispatcher.register_callable_command
class TestHumanCallableCommand(BaseCommand):
    """ Тестовая вызываемая команда без аргументов """
    CMD = 'HumanCallable'

    async def _execute(self):
        await self.send_message(
            subject=">>info<< Test message without args",
        )


@TestHumanCallableCommand.admin_behavior
class TestHumanCallableCommandAdminBehaviour(BaseCommand):
    """ Тестовая вызываемая команда без аргументов для админа """
    async def _execute(self):
        await self.send_message(
            subject=">>info<< Admin",
        )


@dispatcher.register_callable_command
class TestHumanCallableCommandWithArgs(HumanCallableCommandWithArgs):
    """ Тестовая вызываемая команда с аргументами """
    CMD = 'HumanCallableArgs'
    ARGS = (
        arguments.Integer('arg1', 'Тестовый аргумент из чисел', example='123'),
        arguments.String('arg2', 'Тестовый аргумент из букв', example='abc'),
    )

    def _validate(self) -> list:
        wrong_commands = list()
        if not self.arg1.isdigit():
            wrong_commands.append(self.arg1)
        if not self.arg2.isalpha():
            wrong_commands.append(self.arg2)
        return wrong_commands

    async def _execute(self):
        await self.send_message(
            subject=">>info<< Test message with args",
            text=f"Arg with digits: {self.arg1}; Arg with words: {self.arg2}",
        )


@dispatcher.register_callable_command
class TestCommandToSendDocument(BaseCommand):
    """ Тестовая вызываемая команда для отправки аргумента """
    CMD = 'SendDoc'

    async def _execute(self):
        document = {
            "content": "Тестовое содержимое файла",
            "filename": "test_file_name.log",
            "caption": "Тестовое описание файла"
        }
        await self.send_message(
            document=document,
        )


@dispatcher.register_callable_command
class TestCommandToSendOneImage(BaseCommand):
    """ Тестовая вызываемая команда для отправки одного изображения """
    CMD = 'SendImage'

    async def _execute(self):
        with open('test_image.jpg', 'rb') as image:
            image_content = image.read()
        encoded_content = base64.b64encode(image_content).decode()
        await self.send_message(
            subject="Одно изображение",
            text="Этот текст и изображение должны быть в одном сообщении",
            images=[encoded_content, ],
        )


@dispatcher.register_callable_command
class TestCommandToSendManyImage(BaseCommand):
    """ Тестовая вызываемая команда для отправки нескольких изображений """
    CMD = 'SendManyImages'

    async def _execute(self):
        with open('test_image.jpg', 'rb') as image:
            image_content = image.read()
        encoded_content = base64.b64encode(image_content).decode()
        await self.send_message(
            subject="Много изображений",
            text="Сначала текст, потом изображения в реплаях на это сообщение",
            images=[encoded_content for _ in range(3)],
        )


class TestServiceCommand(ServiceCommand):
    """ Тестовая служебная команда """
    CMD = 'Service'

    async def _execute(self):
        await self.send_message(
            text="Вызвана сервисная команда!",
        )


@dispatcher.register_callable_command
class TestCallableCommandWithCallingServiceCommand(BaseCommand):
    """ Тестовая вызываемая команда, в ходе выполнения которой вызовется сервисная команда """
    CMD = 'CallingServiceCommand'

    async def _execute(self):
        service_command = self.create_subcommand(TestServiceCommand)
        await service_command.execute()


@dispatcher.register_callable_command
class TestCallableInternalError(BaseCommand):
    """ Тестовая вызываемая команда, проверяет возврат сообщений о внутренних ошибках """
    CMD = 'InternalError'

    async def _execute(self):
        raise ZeroDivisionError(" - так и задумано")


@dispatcher.register_callable_command
class TestHTMlSymbols(BaseCommand):
    """ Тестовая вызываемая команда, проверяет HTML разметку """
    CMD = 'HTMLmarkdown'

    async def _execute(self):
        message = """
<a href="https://www.google.com/">Ссылка</a>
<b>Жирная <a href="https://www.google.com/">Ссылка</a></b>
<i><b>Жирный курсив</i></b>
Эмоджи >>author<<
"Надпись в двойных кавычках"
`Надпись в обратных кавычках`
<b>``` Жирные обратные кавычки и амперсанды &&&&```</b>
2 < 3 но в цирке не выступает
<b>Жирный больше ></b>
Сейчас будет последовательно:
    <i> Курсив <b> жирный <a href="hhttps://www.google.com/">Ссылка</a></b></i>
Плохой тэг (должен отсуствовать): <https://www.google.com/>
<b>Плохой HTML-тэг внутри жирного <https://www.google.com/></b>
<kek><b>Жирный</b> тэг внутри плохого.
        """

        await self.send_message(
            subject="Лупа >>lupa<< Очки >>glasses<< "
                    "<a href=\"https://www.google.com\">Таблетка</a> >>drug<<",
            text=message,
        )


@hide
@dispatcher.register_callable_command
class TestHideCallableCommand(BaseCommand):
    """ Тестовая вызываемая команда, которую не должно быть видно """
    CMD = 'hide'

    async def _execute(self):
        await self.send_message(
            subject="Вы знаете некоторые тайны"
        )


@admin_only
@dispatcher.register_callable_command
class TestAdminCallableCommand(BaseCommand):
    """ Тестовая вызываемая команда, которую может вызывать только админ"""
    CMD = 'adminOnly'

    async def _execute(self):
        await self.send_message(
            subject="Админская команда"
        )


@dispatcher.register_callable_command
class TestTakeUserId(HumanCallableCommandWithArgs):
    """ Возвращает ID пользователя телеграм"""
    CMD = 'giveMeMyId'
    ARGS = (
        arguments.MyUser("user", "ID подписчика данного канала"),
        arguments.String("string", "какая-то строка"),
    )

    async def _execute(self):
        await self.send_message(
            subject=f"Получен ID {self.user}"
        )


@hide
@dispatcher.register_callable_command
class TakeListWithArg(HumanCallableCommandWithArgs):
    """ Получает обычный аргумент и список """
    CMD = "argAndList"
    ARGS = (
        arguments.String("string", "Какая-то строка"),
        arguments.ListArg("listarg", "Какой-то список"),
    )

    async def _execute(self):
        await self.send_message(
            text=f"Получили такой аргумент: {self.string}\nи такой список: {self.listarg}"
        )


@dispatcher.register_callable_command
class TakeList(HumanCallableCommandWithArgs):
    """ Получает список """
    CMD = "takeList"
    ARGS = (
        arguments.ListArg("listarg", "Какой-то список"),
    )

    async def _execute(self):
        hide_command = self.reverse_command(TakeListWithArg, 'kek', '1', '2', '3')
        await self.send_message(
            subject=f"Получили такой список: {self.listarg}",
            text=f"И вы можете попробовать вызвать такую команду:\n{hide_command}"
        )


@hide
@dispatcher.register_callable_command
class InlineButtonForEdit(BaseCommand):
    """ Инлайн-кнопка для редактирования сообщения """
    CMD = "inlineEdit"

    async def _execute(self):
        await self.send_message(
            subject=f"Сим-Салябим",
            inline_edit_button=True,
        )


@dispatcher.register_callable_command
class SendToChannel(BaseCommand):
    """ Отправить в канал """
    CMD = "channel"

    async def _execute(self):
        await self.send_message(
            subject="Рассылка по каналу",
            target=MessageTarget(target_type="channel", target_name="test")
        )
