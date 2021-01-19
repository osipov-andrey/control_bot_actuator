## Команды с аргументами

Чтобы создать команду с аргументами отнаследуйтесь от соответствующего класса 
и определите аргумент `ARGS` класса вашей команды в виде кортежа с аргументами:

```python
from cba.commands import HumanCallableCommandWithArgs, arguments


class CommandWithArgs(HumanCallableCommandWithArgs):
    """ Команда с аргументами """
    CMD = 'CmdWithArgs'
    ARGS = (
        arguments.Integer('arg1', 'Аргумент из чисел', example='123'),
        arguments.String('arg2', 'Аргумент из букв', example='abc'),
    )

    async def _execute(self):
        await self.send_message(
            text=f"Arg with digits: {self.arg1}; Arg with words: {self.arg2}",
        )
```

После инстанцирования через диспетчер экземпляр команды 
будет иметь одноименные с аргументами атрибуты со значениями, 
введенными пользователем в телеграм боте.

### Аргументы

Библиотека поддерживает 4 типа аргументов:

- `arguments.String` - любое строковое значение;

- `arguments.Integer`- целочисленной значение;

- `arguments.ListArg` - список любых значений;

- `arguments.MyUser` - пользователь, имеющий доступ к актутатору в телеграм боте.

`arguments.Arg` - базовый класс, от которого наследуются все аргументы.

#### Параметры, поддерживаемые всеми аргументами:

- `name` - имя аргумента. Оно станет атрибутом экземпляра команды.
- `description` - описание аргумента.
- `default` - значение по-умолчанию
- `example` - пример значений. Подставляется в описание аргумента.
- `options` - варианты для выбора. Отобразятся кнопками под сообщением в телеграм боте.
- `allowed` - допустимые варианты для валидации на стороне телеграм-бота.
- `allow_options` - сделать допустимыми те, что перечислены в options.

#### Дополнительные параметры `arguments.String`:

- `regex` - Регулярное выражение, которому должно соответствовать значение аргумента.

#### Дополнительные параметры `arguments.Integer`:

- `minimum` - минимальное значение аргумента.
- `maximum` - максимальное значение аргумента.

### Валидация

Валидация ограничений, указанных в параметрах аргументов, 
а так же аргумента типа `arguments.MyUser` происходит на стороне телеграм бота.
Указанные ограничения передаются в бот в виде схемы из библиотеки 
[Cerberus](https://github.com/pyeve/cerberus).

Вы можете определить дополнительно валидацию на стороне актуатора переопределив 
метод `_validate`:

```python
from cba.commands import HumanCallableCommandWithArgs, arguments


class CommandWithArgs(HumanCallableCommandWithArgs):
    """ Команда с аргументами """
    CMD = 'CmdWithArgs'
    ARGS = (
        arguments.Integer('arg1', 'Аргумент из чисел', example='123'),
        arguments.String('arg2', 'Аргумент из букв', example='abc'),
    )

    async def _execute(self):
        await self.send_message(
            text=f"Arg with digits: {self.arg1}; Arg with words: {self.arg2}",
        )

    def _validate(self) -> list:
        wrong_arguments = list()
        if self.arg2 != "Valid value":
            wrong_arguments.append(self.arg1)
        return wrong_arguments
```
