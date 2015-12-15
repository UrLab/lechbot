import re
import asyncio
import logging
import humanize
from datetime import timedelta
from .text import parse_time


def require_subclass(func):
    def wrapper(self, *args, **kwargs):
        raise NotImplementedError(
            "This method should be implemented by a concrete bot backend")
    return wrapper


class Message:
    def __init__(self, bot, user, chan, text, args, kwargs):
        self.bot, self.user, self.chan, self.text = bot, user, chan, text
        self.args, self.kwargs = args, kwargs

    @property
    def is_private(self):
        return self.chan == self.bot.nickname

    def reply(self, text, private=False, hilight=False):
        target = self.user if private or self.is_private else self.chan
        if hilight:
            text = self.user + ': ' + text
        self.bot.say(text, target=target)


class AbstractBot:
    def __init__(self, nickname, channels={}, main_chan=None):
        self.main_chan = main_chan
        self.nickname = nickname
        self.connected = False
        chans = {}
        # {chan: [Plugin]} ->
        #    {chan: {'on_join': [func], 'commands': [(regexp, func)], ...}}
        for chan, plugins in channels.items():
            chan = chan.lower()
            chans[chan] = {}
            for plugin in plugins:
                callbacks = plugin.load(self, chan)
                for k, v in callbacks.items():
                    chans[chan][k] = chans[chan].get(k, []) + list(v)
        self.channels = chans
        self.log = logging.getLogger(__name__)

    def spawn(self, maybe_coroutine):
        self.log.debug("SPAWN " + repr(maybe_coroutine))
        if asyncio.iscoroutine(maybe_coroutine):
            asyncio.async(maybe_coroutine)

    def connect(self, host, port):
        self._connect(host, port)
        self.connected = True
        self.log.info("Connected !")
        for chan, callbacks in self.channels.items():
            for callback in callbacks.get('on_connect', []):
                self.spawn(callback())

    def feed(self, user, target, text):
        target = target.lower()
        if target[0] == '#':
            commands = self.channels.get(target, {}).get('commands', [])
        else:
            commands = self.channels.get('query', {}).get('commands', [])
        for (pattern, callback) in commands:
            match = pattern.match(text)
            if match:
                evt = user, target, text, match.group(), match.groupdict()
                self.log.debug("Match for %s" % pattern)
                self.spawn(callback(Message(self, *evt)))
                break

    def joined(self, chan):
        callbacks = self.channels.get(chan, {})
        for callback in callbacks.get('on_join', []):
            self.spawn(callback())

    def say(self, text, target=None):
        if target is None:
            target = self.main_chan
        if not self.connected:
            self.log.warning("OFFLINE :: {} << {}".format(target, text))
        else:
            for line in text.split('\n'):
                line = line.strip()
                if line:
                    self._say(target, line)

    def set_topic(self, text, target=None):
        if target is None:
            target = self.main_chan
        if not self.connected:
            self.log.warning("OFFLINE :: {} TOPIC {}".format(target, text))
        else:
            self._topic(target, text)

    def command(self, pattern):
        def wrapper(func):
            new = (re.compile(pattern), func)
            for (chan, callbacks) in self.channels.items():
                callbacks['commands'] = callbacks.get('commands', []) + [new]
            return func
        return wrapper

    @property
    def chanlist(self):
        return [x for x in self.channels.keys() if x.startswith('#')]

    @require_subclass
    def _connect(self, host, port):
        pass

    @require_subclass
    def _say(self, target, text):
        pass

    @require_subclass
    def _topic(self, chan, text):
        pass

    def naturaltime(self, time):
        if isinstance(time, timedelta):
            return humanize.naturaldelta(time)
        return humanize.naturaltime(parse_time(time))
