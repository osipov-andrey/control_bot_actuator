import logging
import yaml

from cba import Actuator
from cba.publishers import HTTPPublisher
from cba.consumers import SSEConsumer

import test_commands


with open("test_config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# noinspection PyArgumentList
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(), ])
NAME = config["NAME"]
VERBOSE_NAME = config["VERBOSE_NAME"]
SSE_URL = config["SSE_URL"].format(NAME)


# publisher = RabbitPublisher(**config["rabbit"])
publisher = HTTPPublisher(**config["http"], headers={})

consumer = SSEConsumer(SSE_URL)

if __name__ == '__main__':
    client = Actuator(
        NAME,
        consumer=consumer,
        dispatcher=test_commands.dispatcher,
        publishers=publisher,
        verbose_name=VERBOSE_NAME
    )
    client.run()
