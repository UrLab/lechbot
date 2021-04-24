from ircbot.plugin import BotPlugin

from .helpers import mkurl, private_api, public_api


class TechWednesday(BotPlugin):
    @BotPlugin.command(r"\!tw +([^ ].+)")
    async def add_to_next_tw(self, msg):
        """Ajoute un point à l'ordre du jour de la prochaine réunion"""
        await private_api(
            "/events/add_point_to_next_meeting",
            {"point": msg.args[0] + " (" + msg.user + ")"},
        )
        msg.reply(
            'Point "' + self.bot.text.bold(msg.args[0]) + "\" ajouté à l'ordre du jour",
            hilight=True,
        )
        self.bot.log.info('Add "' + msg.args[0] + '" to next tw by ' + msg.user)

    @BotPlugin.command(r"\!tw")
    async def next_tw(self, msg):
        """Affiche l'ordre du jour de la prochaine réunion"""
        try:
            next_meeting = await public_api("/events/next_meeting")
            when = self.bot.naturaltime(next_meeting["event"]["start"])
            msg.reply(self.bot.text.bold("Prochaine réunion " + when))
            for line in next_meeting["OJ"].split("\n"):
                line = line.strip()
                if line:
                    msg.reply(line)
            msg.reply(
                self.bot.text.blue(mkurl("events/" + str(next_meeting["event"]["id"])))
            )
        except:
            msg.reply("Pas de prochain tw trouvé")
