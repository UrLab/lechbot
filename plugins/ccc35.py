from .helpers import public_api
from ircbot.persist import Persistent
from ircbot.plugin import BotPlugin
from datetime import datetime, timedelta
import pytz
import dateutil
from collections import Counter


class CCC35(BotPlugin):
    end_url = r'(?:$|\s|\)|\]|\})'
    TZ = pytz.timezone('Europe/Berlin')
    DAY0 = datetime(2018, 12, 26, tzinfo=TZ)
    FAHRPLAN_CACHE = None

    def format_talk(self, talk):
        talk['start_time_dt'] = dateutil.parser.parse(talk['start_time'])
        talk['end_time_dt'] = dateutil.parser.parse(talk['end_time'])
        talk['relative_day'] = self.get_day(talk['start_time_dt'])
        fmt = "«{title}» [Day {relative_day}, {start_time_dt:%H:%M}] dans {room[name]}"
        return fmt.format(**talk)

    def get_day(self, dt=None):
        if dt is None:
            dt = datetime.now(self.TZ)
        return (dt - self.DAY0).days

    def get_fahrplan(self, force=False):
            with Persistent('fahrplan.json') as fahrplan:
                if not fahrplan or force:
                    x = yield from public_api("https://fahrplan.events.ccc.de/congress/2018/Fahrplan/events.json")
                    x['update_time'] = datetime.now(self.TZ).isoformat()
                    fahrplan.update(x)
            return fahrplan

    @BotPlugin.command(r'.*https?://fahrplan\.events\.ccc\.de/congress/2018/Fahrplan/events/(\d+).html' + end_url)
    def ccc_fahrplan(self, msg):
        fahrplan = yield from self.get_fahrplan()
        events = fahrplan['conference_events']['events']
        event_id = int(msg.args[0])
        for event in events:
            if event['id'] == event_id:
                msg.reply(self.format_talk(event))
                break

    @BotPlugin.command(r'\!day$')
    def day(self, msg):
        """Quel jour du congrès sommes nous ? Day0 étant le 26/12/2018"""
        day = self.get_day()
        fmt = "We are Day{day}"
        msg.reply(fmt.format(day=day))

    @BotPlugin.command(r'\!talks$')
    def talks(self, msg):
        """Liste les talks en cours et les 5 suivants"""
        fahrplan = yield from self.get_fahrplan()
        events = fahrplan['conference_events']['events']
        events = sorted(events, key=lambda x: (dateutil.parser.parse(x['start_time']), dateutil.parser.parse(x['end_time'])))

        now = datetime.now(self.TZ)
        now_events = []
        next_events = []
        for event in events:
            if dateutil.parser.parse(event['start_time']) < now < dateutil.parser.parse(event['end_time']):
                now_events.append(event)
            elif now < dateutil.parser.parse(event['start_time']):
                next_events.append(event)

        if now_events:
            msg.reply("Talks en cours :")
            for event in now_events:
                msg.reply(" * " + self.format_talk(event), strip_text=False)

        if next_events:
            msg.reply("Prochains talks :")
            for event in next_events[:5]:
                msg.reply(" * " + self.format_talk(event), strip_text=False)

    @BotPlugin.command(r'\!fahrplan$')
    def last_update(self, msg):
        """Affiche le temps écoulé depuis la dernière mise à jour du Fahrplan"""
        fahrplan = yield from self.get_fahrplan()
        uptime = dateutil.parser.parse(fahrplan["update_time"])
        delta = datetime.now(self.TZ) - uptime
        msg.reply("Fahrplan a été mis à jour il y a %i minutes" % (delta.total_seconds() // 60))

    @BotPlugin.command(r'\!update_fahrplan$')
    def update(self, msg):
        """Mettre à jour le Fahrplan"""
        msg.reply("Mise à jour...")
        fahrplan = yield from self.get_fahrplan(force=True)
        msg.reply("Fahrplan mis à jour")

    @BotPlugin.command(r'\!salle (\w+)$')
    def room(self, msg):
        """Liste les 5 prochains talks de la salle passée en paramètre
        (voir !salles pour une liste des salles)"""
        fahrplan = yield from self.get_fahrplan()
        events = fahrplan['conference_events']['events']
        events = sorted(events, key=lambda x: (dateutil.parser.parse(x['start_time']), dateutil.parser.parse(x['end_time'])))

        now = datetime.now(self.TZ)
        kept = []
        for event in events:
            if dateutil.parser.parse(event['end_time']) > now and event["room"]["name"].lower() == msg.args[0].lower():
                kept.append(event)

        if kept:
            for event in kept[:5]:
                msg.reply(self.format_talk(event))
        else:
            msg.reply("Salle introuvable")

    @BotPlugin.command(r'\!salles$')
    def rooms(self, msg):
        """Liste les salles de conférence"""
        fahrplan = yield from self.get_fahrplan()
        events = fahrplan['conference_events']['events']

        counter = Counter([e['room']['name'] for e in events])

        important_rooms = [name for name, count in counter.most_common(10) if count > 5]
        msg.reply("Salles : " + ", ".join(important_rooms))

    @BotPlugin.command(r'\!35c3music$')
    def music(self, msg):
        """ Liste les artistes dans chaque salle """
        schedule = yield from public_api("https://fahrplan.events.ccc.de/congress/2018/Lineup/schedule.json")
        all_performances = {}

        for day in schedule['schedule']['conference']['days']:
            for room, performances in day['rooms'].items():
                if room not in all_performances:
                    all_performances[room] = []
                all_performances[room].extend(performances)

        all_performances = {
            room: sorted(performances, key=lambda x: x['date'])
            for room, performances in all_performances.items()
        }

        TZ = pytz.timezone('Europe/Berlin')
        now = datetime.now().replace(tzinfo=TZ)

        for room, performances in all_performances.items():
            current = None
            for perf in performances:
                date = dateutil.parser.parse(perf['date']).astimezone(TZ)
                if date > now:
                    break
                current = perf
            if current is not None:
                msg.reply("%s: %s à %s pendant %s" % (room, current['title'], current['start'], current['duration']))
