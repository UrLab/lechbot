import asyncio
import logging
import re
from datetime import timedelta

import humanize

from .text import make_style, parse_time


def require_subclass(func):
    def wrapper(self, *args, **kwargs):
        raise NotImplementedError(
            "This method should be implemented by a concrete bot backend"
        )

    return wrapper


class Message:
    """
    Represent a text message, emitted by a certain user on a certain channel.
    The message also has args and kwargs, captured from a pattern match
    against the message text.
    """

    def __init__(self, bot, user, chan, text, args, kwargs):
        self.bot, self.user, self.chan, self.text = bot, user, chan, text
        self.args, self.kwargs = args, kwargs

    @property
    def is_private(self):
        """True if the message was sent in a private conversation"""
        return self.chan == self.bot.nickname.lower()

    def reply(self, text, private=False, hilight=False, strip_text=True):
        """
        Reply to a message

        :param text: The text to reply.
        :type text: str.
        :param private: If true, reply in private message to sender.
        :type private: bool.
        :param hilight: If true, prefix the message with the name of the sender.
        :type hilight: bool.
        :param strip_text: If true, strip  left and right padding characters
        :type strip_text: bool
        :returns:  None.
        """
        target = self.user if private or self.is_private else self.chan
        if hilight:
            text = self.user + ": " + text
        self.bot.say(text, target=target, strip_text=strip_text)


class AbstractBot:
    """
    Base class for all bots backends. Define the common behaviour for the bot,
    and specify interface to be implemented by backends. Backends endorse the
    role of connecting and talking to a real server or a mock.
    """

    class text:
        """
        Text formatter for a specific backend, override if necessary
        """

        bold = staticmethod(make_style("<bold>", "</bold>"))
        red = staticmethod(make_style("<red>", "</red>"))
        green = staticmethod(make_style("<green>", "</green>"))
        yellow = staticmethod(make_style("<yellow>", "</yellow>"))
        blue = staticmethod(make_style("<blue>", "</blue>"))
        purple = staticmethod(make_style("<purple>", "</purple>"))
        grey = staticmethod(make_style("<grey>", "</grey>"))

    def __init__(self, nickname, channels={}, main_chan=None, local_only=False):
        """
        Create a new bot.

        :param nickname: The public nickname of the bot.
        :type nickname: str.
        :param channels: The plugins to run in every channels the bot connects to.
        :type channels: dict.
        :param main_chan: The main channel of this bot. If None, use the first
                          found key of channels.
        :type main_chan: str.
        :param local_only: If the plugins should try or not to poll distant APIs
                           (usefull for local dev without any setup)
        :type local_only: bool

        :example:
            >>> Bot("Bot", {'#chan': AwesomePlugin()})
        """
        self.main_chan = main_chan
        self.nickname = nickname
        self.local_only = local_only
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
        """
        Asynchronously run argument if it is a coroutine.
        """
        self.log.debug("SPAWN " + repr(maybe_coroutine))
        if asyncio.iscoroutine(maybe_coroutine):
            asyncio.ensure_future(maybe_coroutine)

    def connect(self, **kwargs):
        """
        Connect the backend.

        :param kwargs: Backend specific
        """
        self._connect(**kwargs)
        self.connected = True
        self.log.info("Connected !")
        for chan, callbacks in self.channels.items():
            for callback in callbacks.get("on_connect", []):
                self.spawn(callback())
        return self

    def feed(self, user, target, text):
        """
        Feed a new message into the bot

        :param user: The author's nickname.
        :type user: str.
        :param target: The channel which delivered the message.
        :type target: str.
        :param text: The message content.
        :type text: str.
        """
        target = target.lower()
        is_query = target[0] == "#"
        if is_query:
            commands = self.channels.get(target, {}).get("commands", [])
        else:
            commands = self.channels.get("query", {}).get("commands", [])
        for (pattern, callback) in commands:
            match = pattern.match(text)
            if match:
                evt = user, target, text, match.groups(), match.groupdict()
                self.log.debug("Match for %s" % pattern)
                self.spawn(callback(Message(self, *evt)))
                break

    def joined(self, chan):
        """
        Invoke join callbacks for a channel. Should be called by concrete
        backends when the join is effective.

        :param chan: The chan that has been joined.
        :type chan: str.
        """
        callbacks = self.channels.get(chan, {})
        for callback in callbacks.get("on_join", []):
            self.spawn(callback())

    def say(self, text, target=None, strip_text=True):
        """
        Emit a message

        :param text: The message content.
        :type text: str.
        :param target: The channels to which the message belongs. If None,
                       use self.main_chan.
        :type target: str.
        :param strip_text: If true, strip  left and right padding characters
        :type strip_text: bool
        """
        if target is None:
            target = self.main_chan
        if not self.connected:
            self.log.warning("OFFLINE :: {} << {}".format(target, text))
        else:
            for line in text.split("\n"):
                if strip_text:
                    line = line.strip()
                if line:
                    self._say(target, line)

    def set_topic(self, text, chan=None):
        """
        Change the topic of a channel

        :param text: The new topic.
        :type text: str.
        :param chan: The channel to which the topic belongs. If None, defaults
                     to self.main_chan.
        :type chan: str.
        """
        if chan is None:
            chan = self.main_chan
        if not self.connected:
            self.log.warning("OFFLINE :: {} TOPIC {}".format(chan, text))
        else:
            self._topic(chan, text)

    def command(self, pattern):
        """
        Register a command for all channels

        :param pattern: A regexp to match against incoming text
        :type pattern: re.
        :note: The command will be added to the end of self's commands.
        """

        def wrapper(func):
            new = (re.compile(pattern), func)
            for (chan, callbacks) in self.channels.items():
                callbacks["commands"] = callbacks.get("commands", []) + [new]
            return func

        return wrapper

    def run(self, loop=None):
        """
        Run the bot.

        :param loop: an asyncio event loop. If None, grab the default loop first.
        :type loop: asyncio.BaseEventLoop.
        """
        if loop is None:
            loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_forever()

    @property
    def chanlist(self):
        """
        The list of channel names for this bot
        """
        return [x for x in self.channels.keys() if x.startswith("#")]

    @require_subclass
    def _connect(self, **kwargs):
        """
        Perform the backend-specific connection. Named arguments are
        backend specific. This function is synchronous. If the function returns
        without exception, the bot is connected to the backend.

        You probably would want to perform the following tasks here:

            * Establishing connection to server
            * Registering callbacks for incoming message and join confirmations
            * Joining channels
            * ...

        ..warning:: Must be implemented in subclass
        """
        pass

    @require_subclass
    def _say(self, target, text):
        """
        Perform the backend-specific message send.

        :param target: The chan to which the message should be delivered
        :type target: str.
        :param text: The text of the message
        :type text: str.

        ..warning:: Must be implemented in subclass
        """
        pass

    @require_subclass
    def _topic(self, chan, text):
        """
        Perform the backend-specific message send.

        :param target: The chan to which the message should be delivered
        :type target: str.
        :param text: The text of the message
        :type text: str.

        ..warning:: Must be implemented in subclass
        """
        pass

    def naturaltime(self, time):
        if isinstance(time, timedelta):
            return humanize.naturaldelta(time)
        if isinstance(time, str):
            time = parse_time(time)
        # Workaround for bug with timezone-aware datetime in humanize lib
        if time.tzinfo:
            time = time.replace(tzinfo=None)
        return humanize.naturaltime(time)

    def naturalunits(self, number, base=1000, units=("", "k", "M", "G", "T", "P")):
        for unit in units:
            if number < base:
                return f"{round(number, 2)}{unit}"
            number /= base
