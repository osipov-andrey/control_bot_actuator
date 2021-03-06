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
    """Echo command"""

    CMD = "echo"
    ARGS = (arguments.String("text", "Input text"),)

    async def _execute(self):
        """Your pretty business logic is here ! :)"""
        await self.send_message(text=f"Your text is: '{self.text}'")


if __name__ == "__main__":
    actuator = Actuator(
        name=ACTUATOR_NAME, dispatcher=dispatcher, publishers=publisher, consumer=consumer
    )
    actuator.run()
