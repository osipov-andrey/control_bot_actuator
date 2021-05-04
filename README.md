# Control bot actuator (cba)

Library for creating actuator modules for [Control bot](https://github.com/osipov-andrey/control_bot).

Example of a simple actuator:

```python
from cba import Actuator
from cba.commands import HumanCallableCommandWithArgs, arguments
from cba.dispatcher import CommandsDispatcher
from cba.consumers import SSEConsumer
from cba.publishers import HTTPPublisher


ACTUATOR_NAME = "echo"
DESCRIPTION = "Echo actuator"


dispatcher = CommandsDispatcher()
publisher = HTTPPublisher(url="http://localhost:8081/inbox")
consumer = SSEConsumer(sse_url=f"http://localhost:8081/sse/{ACTUATOR_NAME}/events")


@dispatcher.register_callable_command
class EchoCmd(HumanCallableCommandWithArgs):
    """ Echo command """
    CMD = "echo"
    ARGS = (
        arguments.String("text", "Input text"),
    )

    async def _execute(self):
        """ Your pretty business logic is here ! :) """
        await self.send_message(
            text=f"Your text is: '{self.text}'"
        )


if __name__ == '__main__':
    actuator = Actuator(
        name=ACTUATOR_NAME,
        dispatcher=dispatcher,
        publishers=publisher,
        consumer=consumer
    )
    actuator.run()

```

and in the bot we get the following logic:



![Alt-текст](https://github.com/osipov-andrey/control_bot_actuator/blob/master/docs/telegram_echo.png?raw=true "Echo dialog")

# Documentation

## Preparing the environment

The actuator must receive commands (from the bot or from the outside world), execute business logic,
and send messages to the bot with the result of the work.

- To receive commands, use[Consumer](https://github.com/osipov-andrey/control_bot_actuator/blob/master/docs/CONSUMER.md).

- To send messages [Publisher](https://github.com/osipov-andrey/control_bot_actuator/blob/master/docs/PUBLISHERS.md).

## Command description

Commands are the core of the library. It is in them that the business logic is described.
- Commands are described as [classes](https://github.com/osipov-andrey/control_bot_actuator/blob/master/docs/COMMANDS.md). 


## Starting the actuator

For the actuator to work, the following objects must be launched in conjunction: _Consumer, Publisher, Dispatcher_.
This can be done manually using the appropriate methods for each class.
Or you can use the special aggregate class _Actuator_ (see example above).
