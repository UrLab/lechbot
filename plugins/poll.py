from ircbot.plugin import BotPlugin
import asyncio


class Poll(BotPlugin):
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.votes = []

    def print_poll(self):
        t = self.bot.text
        c = lambda x: self.bot.text.blue(self.bot.text.bold(x))
        return "\n".join(
            "%s) %s -- %s" % (t.bold(i), t.blue(t.bold(vote["name"])),
                              ", ".join(vote["voters"]))
            for i, vote in enumerate(self.votes)
        )

    def create_poll(self, args, msg, time=10):
        if len(self.votes):
            return "Il y a déjà un sondage en cours"

        loop = asyncio.get_event_loop()
        loop.call_later(60 * time, self.end_poll, msg)

        if len(args) < 2:
            return "Il manque des arguments: " + str(args)

        for arg in args:  # [:-1]:
            self.votes.append({
                "name": arg,
                "voters": [],
            })

        return "\n".join([
            "Nouveau sondage:\n",
            self.print_poll(),
            "Votez avec " + self.bot.text.bold("!vote <numero du choix>"),
            self.bot.text.yellow("(fin dans %d minutes)") % time
        ])

    def end_poll(self, msg):
        msg.reply("Le sondage est terminé\n" + self.print_poll())
        self.votes = []

    @BotPlugin.command(r'\!poll (.+) (time=\d+)')
    def poll_with_time(self, msg):
        """
        Crée un sondage pour lequel les gens peuvent voter.

        @param Une liste de nom à ajouter au sondage.
        @param Le temps en minute avant de cloturer le sondage.
        """
        msg.reply(self.create_poll(msg.args[0].split(" "),
                                   msg,
                                   int(msg.args[1].replace("time=", ""))))

    @BotPlugin.command(r'\!poll (.+)')
    def poll(self, msg):
        """
        Crée un sondage pour lequel les gens peuvent voter.

        @param Une liste de nom à ajouter au sondage.
        """
        msg.reply(self.create_poll(msg.args[0].split(" "), msg))

    @BotPlugin.command(r'\!poll')
    def show_poll(self, msg):
        """
        Montre le sondage en cours.
        """
        msg.reply(self.print_poll())

    @BotPlugin.command(r'\!vote (\d+)')
    def vote(self, msg):
        """
        Voter pour le sondage.

        @param L'index de l'élement pour lequel on veut voter.
        """
        index = int(msg.args[0])
        if not len(self.votes):
            return msg.reply("Il n'y a pas de poll en cours")
        elif not 0 <= index < len(self.votes):
            return msg.reply("Choix invalide", hilight=True)

        if msg.user not in self.votes[index]["voters"]:
            self.votes[index]["voters"].append(msg.user)
        else:
            return msg.reply("Tu as déjà voté", hilight=True)

        msg.reply(self.print_poll())
