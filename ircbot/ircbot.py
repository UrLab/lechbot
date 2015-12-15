from asyncirc import irc
from .text import IRCColors
from .abstractbot import AbstractBot


class IRCBot(AbstractBot):
    text = IRCColors

    def _connect(self, host, port):
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
