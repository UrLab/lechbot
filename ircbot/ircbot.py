import re
import logging
import asyncio
import humanize
from datetime import timedelta
from asyncirc import irc
from .text import IRCColors, parse_time


class Message:
    def __init__(self, user, chan, text, args, bot):
        self.user, self.chan, self.text, self.args = user, chan, text, args
        self.bot = bot

    is_private = property(lambda self: self.chan == self.bot.nickname)

    def reply(self, text, private=False, hilight=False):
        target = self.user.nick if private or self.is_private else self.chan
        if hilight:
            text = self.user.nick + ': ' + text
        self.bot.say(text, target=target)


class IRCBot:
    text = IRCColors

    def __init__(self, nickname, channels={}):
        self.commands, self.join_callbacks, self.connect_callbacks = [], [], []
        self.nickname = nickname
        chans = {}
        for chan, plugins in channels.items():
            chans[chan] = {}
            for plugin in plugins:
                callbacks = plugin.load(self, chan)
                for k, v in callbacks.items():
                    chans[chan][k] = chans[chan].get(k, []) + list(v)
        self.channels = chans
        self.log = logging.getLogger(__name__)

    def naturaltime(self, time):
        if isinstance(time, timedelta):
            return humanize.naturaldelta(time)
        return humanize.naturaltime(parse_time(time))

    def spawn(self, maybe_coroutine):
        if asyncio.iscoroutine(maybe_coroutine):
            asyncio.async(maybe_coroutine)

    def _invoke_connect_callbacks(self):
        for chan, callbacks in self.channels.items():
            for callback in callbacks.get('on_connect', []):
                self.spawn(callback())

    def _invoke_join_callbacks(self, chan):
        callbacks = self.channels.get(chan, {})
        for callback in callbacks.get('on_join', []):
            self.spawn(callback())

    def connect(self):
        chans = list(filter(lambda k: k != "QUERY", self.channels.keys()))
        self.conn = irc.connect("chat.freenode.net", 6697, use_ssl=True)\
                       .register(self.nickname, "ident", "LechBot")\
                       .join(chans)
        self.conn.queue_timer = 0.25

        @self.conn.on("join")
        def on_join(message, user, channel):
            self._invoke_join_callbacks(channel)
        self._invoke_connect_callbacks()
        self.conn.on("message")(self.dispatch_message)

    def run(self):
        self.connect()
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_forever()
            self.log.info("LechBot starts event loop !")

    def dispatch_message(self, message, user, target, text):
        if target[0] == '#':
            commands = self.channels.get(target, {}).get('commands', [])
        else:
            commands = self.channels.get('QUERY', {}).get('commands', [])
        for (pattern, callback) in commands:
            match = pattern.match(text)
            if match:
                msg = Message(user, target, text, match.groups(), self)
                self.log.debug("Match for %s" % pattern)
                self.spawn(callback(msg))
                break

    def command(self, pattern):
        def wrapper(func):
            new = (re.compile(pattern), func)
            for (chan, callbacks) in self.channels.items():
                callbacks['commands'] = callbacks.get('commands', []) + [new]
            return func
        return wrapper

    def say(self, text, target):
        """
        Private method which actually performs the say.
        Overwritten by other backends.
        """
        if getattr(self, 'conn', None):
            for line in text.split('\n'):
                line = line.strip()
                if line:
                    self.conn.say(target, line)
        else:
            self.log.warning("%s << %s [NOT CONNECTED]" % (target, text))

    def set_topic(self, topic, target):
        if getattr(self, 'conn', None):
            self.conn.writeln('TOPIC %s : %s' % (target, topic))
        else:
            self.log.warning("%s :: %s [NOT CONNECTED]" % (target, topic))
