from ircbot.plugin import BotPlugin
from collections import OrderedDict
import asyncio

class Poll(BotPlugin):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.votes = [] # OrderedDict()

    def print_poll(self):
        return "\n".join("%i) %s -- %s" % (i, vote["name"], str(vote["voters"])) for i, vote in enumerate(self.votes))

    def create_poll(self, args):
        if len(args) < 2:
            return "More args: " + str(args)

        for arg in args:#[:-1]:
            self.votes.append({
                "name": arg,
                "voters": [],
            })

        return "New poll created:\n" + self.print_poll()

    def end_poll(self, msg):
        msg.reply("Poll has ended\n" + self.print_poll())
        self.votes = []

    @BotPlugin.command(r'\!poll (.+) (\d+)')
    def poll(self, msg):
        """
        Crée un sondage pour lequel les gens peuvent voter.

        @param Une liste de nom à ajouter au sondage.
        @param Le temps en minute avant de cloturer le sondage.
        """
        args = msg.args[0].split(" ")
        poll = self.create_poll(args)
        loop = asyncio.get_event_loop()
        loop.call_later(60 * int(msg.args[1]), self.end_poll, msg)
        msg.reply(poll)

    @BotPlugin.command(r'\!vote (\d+)')
    def vote(self, msg):
        """
        Voter pour le sondage.

        @param L'index de l'élement pour lequel on veut voter.
        """
        index = int(msg.args[0])
        if not len(self.votes):
            return msg.reply("No poll currently")
        elif not 0 <= index < len(self.votes):
            return msg.reply("Invalid poll response.")

        if msg.user not in self.votes[index]["voters"]:
            self.votes[index]["voters"].append(msg.user)
        else:
            return msg.reply("Already voted")

        msg.reply(self.print_poll())
