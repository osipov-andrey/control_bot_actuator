## Commands description

### Command with no arguments
Called from telegram bot 1 by pressing

```python
from cba.commands import BaseCommand

class CallableCommand(BaseCommand):
    """ Callable command with no arguments """
    CMD = 'CallingServiceCommand'

    async def _execute(self):
        await self.send_message(
            text="Command with no arguments called!",
        )
```

- The docstring and the `CMD` argument are required!
They are used to creating menu items in a telegram bot.
  

    ⚠️ WARNING!! Do not use snake_case or kebab-case! 
    This will break the command syntax in telegram.
    The same goes for argument names.
  
  
- The _send_message_ method will by default send a message 
  to the user who called the command in the telegram bot.

### Command with arguments
When calling from a telegram bot, additional input of arguments is required.

Learn more about [Commands with arguments.](https://github.com/osipov-andrey/control_bot_actuator/blob/master/docs/CMD_WITH_ARGS.md)

## Registering commands

Create a dispatcher:
```python
from cba.dispatcher import CommandsDispatcher

dispatcher = CommandsDispatcher()
```

### User-called command
Can be called from the telegram bot

```python
@dispatcher.register_callable_command
class CallableCommand(BaseCommand):
    ...
```
### Service command
Can be called from within the dispatcher, but not from the telegram bot

```python
@dispatcher.register_service_command
class CallableCommand(BaseCommand):
    ...
```

### Hidden command
Can be called from the telegram bot, but is not displayed in the menu
(can be used in inline button callbacks like)

```python
from cba.commands import hide

@hide
@dispatcher.register_callable_command
class CallableCommand(BaseCommand):
    ...
```

## Access control
By default, the command has the same workflow for the bot administrator and the regular user.

Command behavior can be further customized as follows:

### Admin-only command

```python
from cba.commands import admin_only

@admin_only
@dispatcher.register_callable_command
class CallableCommand(BaseCommand):
    ...
```

### Separate workflow for admin
To do this, create a new command, and register it as admin behavior for the existing one:

```python
from cba.commands import BaseCommand, HumanCallableCommandWithArgs, arguments

@dispatcher.register_callable_command
class TestDifferentBehavior(BaseCommand):
    """ Command for regular user """
    CMD = "behavior"

    async def _execute(self):
        await self.send_message(
            subject="You are a user",
        )


@TestDifferentBehavior.admin_behavior
class TestDifferentBehaviorAdmin(HumanCallableCommandWithArgs):
    """ Admin behaviour for user command """
    ARGS = (
        arguments.String("adminArg", "admin argument"),
    )

    async def _execute(self):
        await self.send_message(
            subject=f"You are a admin. Your argument: {self.adminArg}",
        )
```

## Calling one command from another
```python
from cba.commands import ServiceCommand, BaseCommand

class TestServiceCommand(ServiceCommand):
    """ Command called from another command """
    CMD = 'Service'

    async def _execute(self):
        await self.send_message(
            text="Service command called!",
        )


@dispatcher.register_callable_command
class TestCallableCommandWithCallingServiceCommand(BaseCommand):
    """ Called command, during the execution of which the service command will be called """
    CMD = 'CallingServiceCommand'

    async def _execute(self):
        service_command = self.create_subcommand(TestServiceCommand)
        await service_command.execute()


```

## Sending messages to telegram from commands
To send messages use the `send_message` method.

The method accepts the following keyword parameters:

- subject - the headline of the message
- text - main text of the message
- target - the "addressee" of the message. Instance of the `Messagetarget` class. 
  By default, the message will be sent to the user who called the command.
- images - List with images (Base64-string).
- document - A text document in the form of a python-dict with the following content:
  
            {
                "content": Str (Content of the document - text),
                "filename": Str (File name)
                "caption":  Str (File description in message with file)
            }

- issue - problem notification. Instance of the `Issue` class.
- replies - List of text messages that will be displayed 
  in the telegram bot as replies to the main one.
- buttons - inline-keyboard.

### Creating an inline-keyboard:
```python
class CmdWithInline(BaseCommand):
    """ Command with inline-button """
    CMD = 'InlineButtons'

    async def _execute(self):
        self.add_inline_button(
            InlineButtonForEdit, "Press me"
        )
        await self.send_message(
            subject="Message with Inline-keyboard",
            buttons=self.inline_buttons,
        )
```

The `add_inline_button` method takes as the first argument the class of the command 
that will be called when the button is pressed. The second is the inscription on the button.