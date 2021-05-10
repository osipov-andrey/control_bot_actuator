from collections import namedtuple


ClientInfo = namedtuple("ClientInfo", "name, verbose_name, hide_name", defaults=(False, ""))
