import asyncio
import random
from datetime import datetime
from operator import itemgetter
from time import time

from ircbot.persist import Persistent
from ircbot.plugin import BotPlugin
from ircbot.text import parse_time

from .helpers import full_pamela, mkurl, protect, public_api, spaceapi

minutes = 60
hours = 60 * minutes
days = 24 * hours

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
    "white_trash": {"timeout": 3.5 * days, "action": "vider la poubelle non triée"},
    "white_trash_second": {
        "timeout": 3.5 * days,
        "action": "vider la poubelle du salon",
    },
    "blue_trash": {"timeout": 7 * days, "action": "vider la poubelle PMC"},
    "clean": {
        "timeout": 3.5 * days,
        "action": "ranger les vidanges/cables et jeter les crasses",
    },
}

JANITOR_MINIMAL_PEOPLE = 4


class Reminder(BotPlugin):
    def tell_event(self, event):
        event["title"] = self.bot.text.bold(event["title"])
        event["when"] = self.bot.naturaltime(event["start"])
        event["url"] = self.bot.text.blue(mkurl("/events/{}".format(event["id"])))
        fmt = "===RAPPEL=== {title} a lieu {when} {url}"
        self.say(fmt.format(**event))
        self.bot.log.info("Reminding Ev#{id} {title}".format(**event))

    @protect
    async def remind_events(self):
        """
        Rappelle les évènements proches
        """
        events = await public_api("/events/")
        now = datetime.now()

        for event in events["results"]:
            if not event.get("start", None):
                continue
            when = parse_time(event["start"])
            from_now = when - now
            self.bot.log.debug("{title} {start}".format(**event))

            for (days, periods) in REMINDERS:
                smin, smax = periods * PERIOD, (periods + 1) * PERIOD
                if from_now.days == days and smin <= from_now.seconds <= smax:
                    self.tell_event(event)
                    break

    @protect
    async def janitor(self):
        """
        Désigne des gens pour faire les corvées de UrLab quand c'est ouvert
        """
        # Récupération de l'état actuel du HS
        data = await full_pamela()
        space = await spaceapi()
        people = set(data)
        if space["state"]["open"] and len(people) >= JANITOR_MINIMAL_PEOPLE:
            now = time()
            # Récupération du cache
            with Persistent("janitor.json") as janitor:
                # On ne prend que les personnes qui n'étaient pas choisies
                # précédemment
                already_chosen = set(map(itemgetter("who"), janitor.values()))
                eligible_people = list(people - already_chosen)

                # Pour chaque tâche, si elle n'a pas été faite depuis assez
                # longtemps, on sélectionne qqun au hasard pour la faire
                for name, task in JANITOR_TASKS.items():
                    cache = janitor.setdefault(name, {"time": 0, "who": None})
                    last = cache["time"]
                    if now - last > task["timeout"] and eligible_people:
                        who = random.choice(eligible_people)
                        eligible_people.remove(who)
                        fmt = "Salut {who} ! Tu pourrais {action} stp ?"
                        self.say(fmt.format(who=who, action=task["action"]))

                        # Envoi d'une notification sonore au hackerspace
                        # await lechbot_notif('trash')

                        # On enregitre dans le cache
                        janitor[name] = {"time": now, "who": who}
                        self.bot.log.info("%s designated for %s" % (who, name))

    @BotPlugin.on_connect
    async def reminder(self):
        if self.bot.local_only:
            return
        # Sleep 30 to be sure that we are connected to IRC.
        await asyncio.sleep(30)

        while True:
            await self.janitor()
            await asyncio.sleep(PERIOD / 2)
            await self.remind_events()
            await asyncio.sleep(PERIOD / 2)
