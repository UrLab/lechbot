import asyncio
from typing import Tuple

from ircbot.abstractbot import AbstractBot


class PytestBot(AbstractBot):
    __test__ = False  # Mark this as not a pytest test

    output: list[Tuple[str, str, str]]
    queue: list

    def __init__(self, plugin=None, nickname="TestBot"):
        super().__init__(nickname, channels={"#testchan": [plugin]})
        self.output = []
        self.queue = []

    async def feed(self, *, user="TestUser", target="#testchan", text=""):
        super().feed(user, target, text)

        while self.queue:
            await self.queue.pop(0)

    def say(self, text, target=None, strip_text=True):
        self.output.append(("say", target, text))

    def set_topic(self, text, chan=None):
        self.output.append(("topic", chan, text))

    def spawn(self, maybe_coroutine):
        if asyncio.iscoroutine(maybe_coroutine):
            self.queue.append(maybe_coroutine)
