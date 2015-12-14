from .helpers import public_api, private_api, mkurl
from ircbot.plugin import BotPlugin


class TechWednesday(BotPlugin):
    @BotPlugin.command(r'\!tw +([^ ].+)')
    def add_to_next_tw(self, msg):
        """Ajoute un point à l'ordre du jour de la prochaine réunion"""
        yield from private_api("/events/add_point_to_next_meeting", {
            'point': msg.args[0] + ' (' + msg.user.nick + ')'
        })
        msg.reply(
            'Point "' + self.bot.text.bold(msg.args[0]) + '" ajouté à l\'ordre du jour',
            hilight=True)
        self.bot.log.info('Add "' + msg.args[0] + '" to next tw by ' + msg.user.nick)

    @BotPlugin.command(r'\!tw')
    def next_tw(self, msg):
        """Affiche l'ordre du jour de la prochaine réunion"""
        try:
            next_meeting = yield from public_api('/events/next_meeting')
            when = self.bot.naturaltime(next_meeting['event']['start'])
            msg.reply(self.bot.text.bold("Prochaine réunion " + when))
            for line in next_meeting['OJ'].split('\n'):
                line = line.strip()
                if line:
                    msg.reply(line)
            msg.reply(self.bot.text.blue(mkurl("events/" + str(next_meeting['event']['id']))))
        except:
            msg.reply("Pas de prochain tw trouvé")
