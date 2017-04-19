from ircbot.plugin import BotPlugin
from collections import OrderedDict
import asyncio

class Poll(BotPlugin):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.votes = [] # OrderedDict()

    def print_poll(self):
        return "\n".join("%i) %s -- %i" % (i, vote["name"], vote["count"]) for i, vote in enumerate(self.votes))

    def create_poll(self, args):
        if len(args) < 2:
            return "More args: " + str(args)

        for arg in args:#[:-1]:
            self.votes.append({
                "name": arg,
                "count": 0,
            })

        return "New poll created:\n" + self.print_poll()

    def clean_vote(self):
        self.votes = []

    @BotPlugin.command(r'\!poll (.+)')
    def poll(self, msg):
        poll = self.create_poll(msg.args[0].split(" "))
        msg.reply(poll)

    @BotPlugin.command(r'\!vote (\d+)')
    def vote(self, msg):
        index = int(msg.args[0])
        if not (0 <= index < len(self.votes)):
            return msg.reply("Invalid poll response.")

        self.votes[index]["count"] += 1

        msg.reply(self.print_poll())
