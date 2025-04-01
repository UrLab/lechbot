import re
from enum import Enum

class ECommandType(Enum):
    CONNECT = 1
    DISCONNECT = 2
    COMMAND = 3
    SUDO_COMMAND = 4
    JOIN = 5

class Command:
    def __init__(self, callback, id=-1, regex=None, sudo=False, public=True):
        self.regex = re.compile(regex) if regex else None
        self.callback = callback
        self.public = public
        self.need_sudo = sudo
        self.id = id

    def __call__(self, *args, **kwds):
        self.callback(*args, **kwds)
