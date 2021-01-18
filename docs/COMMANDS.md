## Описание команд

### Команда без аргументов
Вызывается из телеграм бота 1 нажатием

```python
from cba.commands import BaseCommand

class CallableCommand(BaseCommand):
    """ Вызываемая команда без аргументов """
    CMD = 'CallingServiceCommand'

    async def _execute(self):
        await self.send_message(
            text="Вызвана команда без аргументов!",
        )
```

- Строка документации и аргумент `CMD` обязательны к заполнению!
Они используются для создания пунктов меню в телеграм боте
  
- метод _send_message_ по-умолчанию отправит сообщение тому 
  пользователю, который вызвал команду в телеграм-боте.

### Команда с аргументами
При вызове из телеграм бота требуется дополнительно ввод аргументов

...

## Регистрация команд

Создаем диспетчер:
```python
from cba.dispatcher import CommandsDispatcher

dispatcher = CommandsDispatcher()
```

### Вызываемая пользователем команда
Может быть вызвана из телеграм бота

```python
@dispatcher.register_callable_command
class CallableCommand(BaseCommand):
    ...
```
### Служебная команда
Может быть вызвана через диспетчер изнутри 
актуатора, но не из телеграм бота

```python
@dispatcher.register_service_command
class CallableCommand(BaseCommand):
    ...
```

### Скрытая команда
Может быть вызвана из телеграм бота, но в меню не отображается
(может быть использована в инлайн-кнопках, например)

```python
from cba.commands import hide

@hide
@dispatcher.register_callable_command
class CallableCommand(BaseCommand):
    ...
```

## Разграничение доступа
По-умолчанию команда имеет одинаковый workflow для администратора бота и обычного пользователя.

Поведение команды можно дополнительно настроить следующим образом:

### Admin-only команда

```python
from cba.commands import admin_only

@admin_only
@dispatcher.register_callable_command
class CallableCommand(BaseCommand):
    ...
```

### Отдельный workflow для администратора
Для этого создадим новую команду, и зарегистрируем ее как админское поведение для имеющейся:

```python
from cba.commands import BaseCommand, HumanCallableCommandWithArgs, arguments

@dispatcher.register_callable_command
class TestDifferentBehavior(BaseCommand):
    """ Пользовательская команда """
    CMD = "behavior"

    async def _execute(self):
        await self.send_message(
            subject="Вы пользователь",
        )


@TestDifferentBehavior.admin_behavior
class TestDifferentBehaviorAdmin(HumanCallableCommandWithArgs):
    """ Админское поведение пользовательской команды """
    ARGS = (
        arguments.String("adminArg", "админский аргумент"),
    )

    async def _execute(self):
        await self.send_message(
            subject=f"Вы админ. Ваш аргумент: {self.adminArg}",
        )
```

## Вызов одной команды из другой
```python
from cba.commands import ServiceCommand, BaseCommand

class TestServiceCommand(ServiceCommand):
    """ Команда, вызываемая из другой команды """
    CMD = 'Service'

    async def _execute(self):
        await self.send_message(
            text="Вызвана сервисная команда!",
        )


@dispatcher.register_callable_command
class TestCallableCommandWithCallingServiceCommand(BaseCommand):
    """ Вызываемая команда, в ходе выполнения которой вызовется сервисная команда """
    CMD = 'CallingServiceCommand'

    async def _execute(self):
        service_command = self.create_subcommand(TestServiceCommand)
        await service_command.execute()


```