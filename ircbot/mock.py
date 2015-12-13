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
from .text import CLIColors

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


class CLIBot(IRCBot):
    text = CLIColors

    def say(self, text, target):
        print("%s < \033[1;33m%s\033[0m> %s" % (target, self.nickname, text))

    def set_topic(self, text, target=None):
        if target is None:
            target = self.channels[0]
        print("\033[1;36mSet topic of %s\033[0m %s" % (target, text))

    def stdin_mainloop(self):
        print("\033[1;31m>>> RUNNING IN COMMAND LINE MODE ONLY <<<\033[0m")
        user = namedtuple('User', ['nick'])("cli")
        chan = list(self.channels.keys())[0]
        while True:
            text = yield from async_input("")
            print("%s < \033[1;34mcli\033[0m> %s" % (chan, text))
            self.dispatch_message(None, user, chan, text)

    def connect(self):
        self._invoke_connect_callbacks()
        for chan in self.channels:
            self._invoke_join_callbacks(chan)

        asyncio.async(self.stdin_mainloop())
