import asyncio
import re

from .abstractbot import AbstractBot


class RunTestBot(AbstractBot):
    """
    A backend that performs file-based functional test. "Connect" to input
    files, that look a bit like IRC logs. If the author of a message is not
    the bot's nickname, feed the message to the bot, otherwise assert that
    the bot has replied the expected text.
    """

    input_regexp = re.compile(r"(#?[^ ]+) +<([^>]+)> *(.*)")

    async def mainloop(self):
        """
        Main coroutine for the test backend.
        """
        for line in open(self.filename):
            match = self.input_regexp.match(line.strip())
            if match:
                target, user, text = match.groups()
                if user == self.nickname:
                    print("EXPECTING", match.groups())
                    assert self.output[0] == ("say", target, text)
                    self.output = self.output[1:]
                else:
                    print("FEEDING", match.groups())
                    self.feed(user, target, text)
                    yield
        assert len(self.output) == 0

    def run(self, loop=None):
        """
        Run the test (for instance, use this method in pytest) until it is
        finished.

        :example:
        >>> chans = {'#chan': [MyPlugin()]}
        >>> TestBot('Bot', chans).connect(filename="file")
                                 .run()
        """
        if loop is None:
            loop = asyncio.get_event_loop()
        loop.run_until_complete(self.mainloop())

    def _connect(self, filename, **kwargs):
        """
        Connect to the input test file

        :param filename: The input test filename.
        :type filename: str.
        """
        self.filename = filename
        self.output = []

    def _say(self, target, text):
        self.output.append(("say", target, text))

    def _topic(self, chan, text):
        self.output.append(("topic", chan, text))
