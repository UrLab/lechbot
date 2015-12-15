from asyncirc import irc
from .text import make_style
from .abstractbot import AbstractBot


class IRCBot(AbstractBot):
    class text:
        bold = staticmethod(make_style('\x02', '\x02'))
        red = staticmethod(make_style('\x035', '\x03'))
        green = staticmethod(make_style('\x033', '\x03'))
        yellow = staticmethod(make_style('\x037', '\x03'))
        blue = staticmethod(make_style('\x032', '\x03'))
        purple = staticmethod(make_style('\x036', '\x03'))
        grey = staticmethod(make_style('\x0315', '\x03'))

    def _connect(self, host, port, **kwargs):
        self.conn = irc.connect(host, port, use_ssl=True)\
                       .register(self.nickname, "ident", "LechBot")\
                       .join(self.chanlist)
        self.conn.queue_timer = 0.33

        @self.conn.on("join")
        def on_join(message, user, channel):
            self._on_join(channel)

        @self.conn.on("message")
        def on_message(message, user, target, text):
            self.feed(user.nick, target, text)

    def _say(self, target, text):
        self.conn.say(target, text)

    def _topic(self, topic, target):
        self.conn.writeln('TOPIC %s : %s' % (target, topic))
