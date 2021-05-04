## Commands with arguments

To create a command with arguments, inherit from the corresponding class
and define the argument `ARGS` for your command class as a tuple of arguments:

```python
from cba.commands import HumanCallableCommandWithArgs, arguments


class CommandWithArgs(HumanCallableCommandWithArgs):
    """ Command with arguments """
    CMD = "CmdWithArgs"
    ARGS = (
        arguments.Integer("arg1", "Argument with words", example="123"),
        arguments.String("arg2", "Argument with digits", example="abc"),
    )

    async def _execute(self):
        await self.send_message(
            text=f"Arg with digits: {self.arg1}; Arg with words: {self.arg2}",
        )
```


### Arguments

The library supports 4 types of arguments:

- `arguments.String` - any string value;

- `arguments.Integer`- integer value;

- `arguments.ListArg` - list of any values;

- `arguments.MyUser` - user who has grant to the actuator in the telegram bot.

`arguments.Arg` - base class from which all arguments inherit.

#### Parameters supported by all arguments:

- `name` - the name of the argument. It will become an attribute of the command instance.
- `description` - description of the argument.
- `default` - default value.
- `example` - example values. Substituted into the argument description.
- `options` - options to choose from. Displayed by buttons under the message in the telegram bot.
- `allowed` - acceptable options (for validation on the telegram bot side).
- `allow_options` - make allowed the ones specified in the options.

#### Extra options `arguments.String`:

- `regex` - Regular expression that the argument value must match (for validation on the telegram bot side).

#### Extra options `arguments.Integer`:

- `minimum` - the minimum value of the argument.
- `maximum` - the maximum value of the argument.

### Validation

Validation according to the specified parameters occurs on the side of the telegram bot.
The specified restrictions are transferred to the bot in the form of a scheme from the library
[Cerberus](https://github.com/pyeve/cerberus).

You can define additional validation on the actuator side by overriding `_validate` method:

```python
from cba.commands import HumanCallableCommandWithArgs, arguments


class CommandWithArgs(HumanCallableCommandWithArgs):
    """ Command with arguments """
    CMD = "CmdWithArgs"
    ARGS = (
        arguments.Integer("arg1", "Argument with words", example="123"),
        arguments.String("arg2", "Argument with digits", example="abc"),
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
