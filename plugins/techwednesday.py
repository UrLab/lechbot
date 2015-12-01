from .helpers import public_api, private_api, mkurl
from operator import itemgetter
from datetime import datetime


def load(bot):
    @bot.command(r'\!tw +([^ ].+)')
    def add_to_next_tw(msg):
        """Ajoute un point à l'ordre du jour de la prochaine réunion"""
        yield from private_api("/events/add_point_to_next_meeting", {
            'point': msg.args[0] + ' (' + msg.user.nick + ')'
        })
        msg.reply(
            'Point "' + msg.args[0] + '" ajouté à l\'ordre du jour',
            hilight=True)
        bot.log.info('Add "' + msg.args[0] + '" to next tw by ' + msg.user.nick)

    @bot.command(r'\!tw')
    def next_tw(msg):
        """Affiche l'ordre du jour de la prochaine réunion"""
        try:
            next_meeting = yield from public_api('/events/next_meeting')
            when = bot.naturaltime(next_meeting['event']['start'])
            msg.reply("Prochaine réunion " + when)
            for line in next_meeting['OJ'].split('\n'):
                msg.reply(line.strip())
            msg.reply(mkurl("meetings/" + str(next_meeting['id'])))
        except:
            msg.reply("Pas de prochain tw trouvé")
