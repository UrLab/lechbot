import re
import logging
import asyncio
from collections import namedtuple

from asyncirc import irc

logger = logging.getLogger(__name__)


class Message:
    def __init__(self, user, chan, text, args, bot):
        self.user, self.chan, self.text, self.args = user, chan, text, args
        self.bot = bot

    def reply(self, text, private=False, hilight=False):
        target = self.user.nick if private else self.chan
        if hilight:
            text = self.user.nick + ': ' + text
        self.bot.say(text, target=target)


class IRCBot:
    def __init__(self, nickname, channels):
        self.commands = []
        self.nickname = nickname
        self.channels = channels

    def connect(self):
        self.conn = irc.connect("chat.freenode.net", 6697, use_ssl=True)\
                       .register(self.nickname, "ident", "LechBot")\
                       .join(self.channels)

        @self.conn.on("join")
        def on_join(message, user, channel):
            logger.info("Joining " + channel)

        self.conn.on("message")(self.dispatch_message)

    def run(self):
        self.connect()
        asyncio.get_event_loop().run_forever()

    def command(self, pattern):
        def wrapper(func):
            self.commands.append((re.compile(pattern), func))
            return func
        return wrapper

    def dispatch_message(self, message, user, target, text):
        for (pattern, callback) in self.commands:
            match = pattern.match(text)
            if match:
                msg = Message(user, target, text, match.groups(), self)
                logger.debug("Match for %s" % pattern)
                r = callback(msg)
                if asyncio.iscoroutine(r):
                    asyncio.async(r)
                break

    def say(self, text, target=None):
        if target is None:
            target = self.channels[0]
        if getattr(self, 'conn', None):
            self.conn.say(target, text)
        else:
            logger.warning("%s << %s [NOT CONNECTED]" % (target, text))

    def help(self, msg):
        """Affiche l'aide"""
        msg.reply("Je te réponds en privé ;)", hilight=True)
        for (pat, callb) in self.commands:
            if callb.__doc__:
                pattern = ''.join(filter(lambda x: x != '\\', pat.pattern))
                doc = "\x02%s\x02: %s" % (pattern, callb.__doc__.strip())
                msg.reply(doc, private=True)
