import asyncio
import random
from ircbot.persist import Persistent
from .helpers import public_api, spaceapi, mkurl, lechbot_notif
from datetime import datetime
from time import time
from operator import itemgetter

from logging import getLogger
logger = getLogger(__name__)

minutes = 60
hours = 60*minutes
days = 24*hours

PERIOD = 15 * minutes
REMINDERS = [
    (7, 0),
    (3, 0),
    (1, 0),
    (0, 15),
    (0, 5),
]

# Liste des corvées de UrLab
JANITOR_TASKS = {
    'white_trash': {
        'timeout': 5*days,
        'action': 'vider la poubelle non triée'
    },
    'blue_trash': {
        'timeout': 5*days,
        'action': 'vider la poubelle PMC'
    },
    'clean': {
        'timeout': 10*days,
        'action': 'passer un coup de balais dans le hackerspace'
    }
}


def protect(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger.exception("Error in {}".format(func.__name__))
    return wrapper


def load(bot):
    @protect
    def remind_events():
        """
        Rappelle les évènements proches
        """
        events = yield from public_api("/events/")
        now = datetime.utcnow()

        for event in events['results']:
            if not event.get('start', None):
                continue
            when = datetime.strptime(event['start'], '%Y-%m-%dT%H:%M:%SZ')
            from_now = when - now
            for (days, periods) in REMINDERS:
                smin, smax = periods*PERIOD, (periods + 1)*PERIOD
                if from_now.days == days and smin < from_now.seconds < smax:
                    event['when'] = bot.naturaltime(when)
                    event['url'] = mkurl('/events/{}'.format(event['id']))
                    bot.say("{title} a lieu {when} {url}".format(**event))
                    bot.log.info("Reminding Ev#{id} {title}".format(**event))
                    break

    @protect
    def janitor():
        """
        Désigne des gens pour faire les corvées de UrLab quand c'est ouvert
        """
        # Récupération de l'état actuel du HS
        space = yield from spaceapi()
        people = set(space['sensors']['people_now_present'][0]['names'])
        if space['state']['open']:
            now = time()
            # Récupération du cache
            with Persistent('janitor.json') as janitor:
                # On ne prend que les personnes qui n'étaient pas choisies
                # précédemment
                already_choosed = set(map(itemgetter('who'), janitor.values()))
                people = list(people - already_choosed)

                # Pour chaque tâche, si elle n'a pas été faite depuis assez
                # longtemps, on sélectionne qqun au hasard pour la faire
                for name, task in JANITOR_TASKS.items():
                    cache = janitor.setdefault(name, {'time': 0, 'who': None})
                    last = cache['time']
                    if now - last > task['timeout'] and people:
                        who = random.choice(people)
                        people.remove(who)
                        fmt = "Salut {who} ! Tu pourrais {action} stp ?"
                        bot.say(fmt.format(who=who, action=task['action']))

                        # Envoi d'une notification sonore au hackerspace
                        yield from lechbot_notif('trash')

                        # On enregitre dans le cache
                        janitor[name] = {'time': now, 'who': who}
                        bot.log.info("%s designated for %s" % (who, name))

    @bot.on_connect
    def reminder():
        while True:
            yield from remind_events()
            yield from janitor()
            yield from asyncio.sleep(PERIOD)
