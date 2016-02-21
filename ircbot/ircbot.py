from asyncirc import irc
from .text import make_style
from .abstractbot import AbstractBot
from time import time


class IRCBot(AbstractBot):
    TIMER = 0.33

    class text:
        bold = staticmethod(make_style('\x02', '\x02'))
        red = staticmethod(make_style('\x035', '\x03'))
        green = staticmethod(make_style('\x033', '\x03'))
        yellow = staticmethod(make_style('\x037', '\x03'))
        blue = staticmethod(make_style('\x032', '\x03'))
        purple = staticmethod(make_style('\x036', '\x03'))
        grey = staticmethod(make_style('\x0315', '\x03'))

    def _on_irc_message(self, msg, user, target, text):
        self.feed(user.nick, target, text)

    def _on_irc_join(self, msg, user, channel):
        self.joined(channel)

    def _connect(self, host, port, **kwargs):
        self.last_say = time()
        self.conn = irc.connect(host, port, use_ssl=True)\
                       .register(self.nickname, "ident", "LechBot")\
                       .join(self.chanlist)
        self.conn.queue_timer = self.TIMER
        self.conn.on('message')(self._on_irc_message)
        self.conn.on('join')(self._on_irc_join)
        self.log.info("Connected to {}".format(host))

    def _say(self, target, text):
        now = time()
        if now - self.last_say < 5:
            if self.conn.queue_timer < 5:
                self.conn.queue_timer *= 1.1
        else:
            self.conn.queue_timer = self.TIMER
        self.last_say = now
        self.conn.say(target, text)

    def _topic(self, topic, target):
        self.conn.writeln('TOPIC %s : %s' % (target, topic))
