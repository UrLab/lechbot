from .helpers import public_api, mkurl
from operator import itemgetter
from datetime import datetime


def load(bot):
    @bot.command(r'\!tw +([^ ].+)')
    def add_to_next_tw(msg):
        """Ajoute un point à l'ordre du jour de la prochaine réunion"""
        point = msg.args[0]
        msg.reply("Not implemented")
        bot.log.info('Add "' + point + '" to next tw by ' + msg.user.nick)

    @bot.command(r'\!tw')
    def next_tw(msg):
        """Affiche l'ordre du jour de la prochaine réunion"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        events = yield from public_api('/events')
        meetings = sorted(
            filter(lambda ev: ev['start'] > now and ev['meeting'] is not None,
                events['results']),
            key=itemgetter('start'))
        if not meetings:
            msg.reply("Pas de prochain tw trouvé")
        else:
            next_meeting = meetings[0]
            meeting = yield from public_api(next_meeting['meeting'])

            msg.reply("Prochaine réunion " + bot.naturaltime(next_meeting['start']))
            for line in meeting['OJ'].split('\n'):
                msg.reply(line.strip())
            msg.reply(mkurl("meetings/" + str(meeting['id'])))
