"""
Largely inspired by https://gist.github.com/nathan-hoad/8966377
"""

import os
import asyncio
import sys
import unicodedata

from asyncio.streams import StreamWriter, FlowControlMixin
from collections import namedtuple
from .ircbot import IRCBot

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


class MockIRCBot(IRCBot):
    def say(self, text, target=None):
        if target is None:
            target = self.channels[0]
        text = ''.join(filter(is_printable, text))
        print("%s < \033[1;33m%s\033[0m> %s" % (target, self.nickname, text))

    def set_topic(self, text, target=None):
        if target is None:
            target = self.channels[0]
        print("\033[1;36mSet topic of %s\033[0m %s" % (target, text))

    def stdin_mainloop(self):
        print("\033[1;31m>>> RUNNING IN COMMAND LINE MODE ONLY <<<\033[0m")
        user = namedtuple('User', ['nick'])("cli")
        while True:
            text = yield from async_input("")
            print("%s < \033[1;34mcli\033[0m> %s" % (self.channels[0], text))
            self.dispatch_message(None, user, self.channels[0], text)

    def run(self):
        for callback in self.connect_callbacks:
            self.spawn(callback())
        asyncio.get_event_loop().run_until_complete(self.stdin_mainloop())
