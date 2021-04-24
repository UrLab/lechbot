"""
Largely inspired by https://gist.github.com/nathan-hoad/8966377
"""

import os
import asyncio
import sys
import unicodedata

from asyncio.streams import StreamWriter, FlowControlMixin
from .abstractbot import AbstractBot
from .text import make_style

reader, writer = None, None


@asyncio.coroutine
def stdio(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(reader)

    writer_transport, writer_protocol = yield from loop.connect_write_pipe(FlowControlMixin, os.fdopen(0, 'wb'))
    writer = StreamWriter(writer_transport, writer_protocol, None, loop)

    yield from loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    return reader, writer


@asyncio.coroutine
def async_input(message):
    if isinstance(message, str):
        message = message.encode('utf8')

    global reader, writer
    if (reader, writer) == (None, None):
        reader, writer = yield from stdio()

    writer.write(message)
    yield from writer.drain()

    line = yield from reader.readline()
    return line.decode('utf8').replace('\r', '').replace('\n', '')


is_printable = lambda c: unicodedata.category(c) != 'Cc'


class CLIBot(AbstractBot):
    class text:
        bold = staticmethod(make_style('\033[1m', '\033[0m'))
        red = staticmethod(make_style('\033[31m', '\033[0m'))
        green = staticmethod(make_style('\033[32m', '\033[0m'))
        yellow = staticmethod(make_style('\033[33m', '\033[0m'))
        blue = staticmethod(make_style('\033[34m', '\033[0m'))
        purple = staticmethod(make_style('\033[35m', '\033[0m'))
        cyan = staticmethod(make_style('\033[36m', '\033[0m'))
        grey = staticmethod(make_style('\033[37m', '\033[0m'))

    def stdin_mainloop(self):
        print("\033[1;31m>>> RUNNING IN COMMAND LINE MODE ONLY <<<\033[0m")
        user = "cli"
        map(self.joined, self.chanlist)
        while True:
            text = yield from async_input("")
            print("%s < \033[1;34mcli\033[0m> %s" % (self.main_chan, text))
            self.feed(user, self.main_chan, text)

    def _say(self, target, text):
        print("%s < \033[1;33m%s\033[0m> %s" % (target, self.nickname, text))

    def _topic(self, target, text):
        print("\033[1;36mSet topic of %s\033[0m %s" % (target, text))

    def _connect(self, **kwargs):
        asyncio.ensure_future(self.stdin_mainloop())
