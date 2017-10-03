import asyncio
import random
from ircbot.persist import Persistent
from ircbot.text import parse_time
from ircbot.plugin import BotPlugin
from .helpers import public_api, mkurl, protect, full_pamela, spaceapi
from datetime import datetime, timedelta
from datetime import time as dtime
from operator import itemgetter
from time import mktime
import itertools
import functools
import aiohttp

TRAIN_TIMES = [
    (dtime(7, 0), dtime(9, 15), "Brussels-Central", "S11779"),
    (dtime(9, 15), dtime(10, 15), "Brussels-Central", "S11780"),
    (dtime(16, 0), dtime(17, 15), "Brussels-Chapelle/Brussels-Kapellekerk", "S11766"),
    (dtime(17, 15), dtime(18, 15), "Brussels-Chapelle/Brussels-Kapellekerk", "S11767"),
]

RULES = {
    # 'train_morning': [
    #     {"hour": [9], "minute": [40], "weekday": [1, 2, 3, 4, 5]},
    # ],
    # 'train_evening': [
    #     {"hour": [17], "minute": [40], "weekday": [1, 2, 3, 4, 5]},
    # ],
    # 'metro': [
    #     {"hour": [9], "minute": [15], "weekday": [1, 2, 3, 4, 5]},
    # ],
    # "pair": [
    #     {"hour": range(24), "minute": range(0, 60, 2), "weekday": range(7)}
    # ],
    # "impair": [
    #     {"hour": range(24), "minute": range(1, 60, 2), "weekday": range(7)}
    # ],
    # "im_a_test": [
    #     {"hour": range(24), "minute": range(60), "weekday": range(7)}
    # ],
    # "other_test": [
    #     {"hour": range(24), "minute": range(60), "weekday": range(7)}
    # ]
}


def next_day(weekday, hour=0, minute=0, second=0):
    now = datetime.now()
    d_days = (weekday - now.weekday()) % 7
    day = now + timedelta(days=d_days)
    if d_days == 0 and dtime(hour, minute, second) < now.time():
        day += timedelta(days=7)
    return day.replace(hour=hour, minute=minute, second=second, microsecond=0)


class StationMaster(BotPlugin):
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def get_next_instant(self, event_type):
        rules = RULES[event_type]
        expanded_rules = itertools.chain(*(
            itertools.product(rule["weekday"], rule["hour"], rule['minute'])
            for rule in rules
        ))
        expanded_rules = list(expanded_rules)
        days = [next_day(*rule) for rule in expanded_rules]
        return min(days)

    # @asyncio.coroutine
    def event(self, event_type):
        print("Calling %s" % event_type)
        self.set_next_call(event_type)
        fun = getattr(self, "run_%s" % event_type)
        # yield from fun()
        print("%s called" % event_type)

    def run_pair(self):
        print("Ceci est une minute paire")

    def run_impair(self):
        print("Ceci est une minute impaire")

    def run_train_morning(self):
        station = "Brussels-Central"
        train = "S11780"

    def run_im_a_test(self):
        print("Inside i'm a test")
        station = "Brussels-Central"
        train = "S11780"
        a = yield from self.get_delay(train, station)
        print(a)

    def run_other_test(self):
        print("Inside other test")

    def get_delay(self, train_id, station):
        url = "https://api.irail.be/vehicle/?id=BE.NMBS.%s&format=json" % train_id

        response = yield from aiohttp.get(url)
        data = yield from response.json()
        stops = [s for s in data["stops"]["stop"] if s["station"] == station]
        if len(stops) != 1:
            raise Exception("More than one %s stop" % station)
        stop = stops[0]
        print(stop)
        departure = datetime.fromtimestamp(int(stop['scheduledDepartureTime']))
        return {
            "canceled": stop["departureCanceled"] != "0",
            "delay": int(stop["departureDelay"]),
            "platform": stop['platform'],
            "scheduled_departure": departure,
        }

    def set_next_call(self, event_type):
        at = self.get_next_instant(event_type)
        dt = (at - datetime.now()).total_seconds()
        dt /= 20
        dt = max(dt, 2)
        self.loop.call_at(
            self.loop.time() + dt,
            functools.partial(self.event, event_type)
        )
        print("timer set in %s for %s" % (dt, event_type))

    @BotPlugin.on_connect
    def boot(self):
        print("booting")
        for event_type in RULES.keys():
            self.set_next_call(event_type)

    @BotPlugin.command(r'\!teleport')
    def teleport(self, msg):
        has_ran = False
        for start, stop, station, train in TRAIN_TIMES:
            if start < datetime.now().time() < stop:
                has_ran = True
                data = yield from self.get_delay(train, station)

                if data['canceled']:
                    txt = "is canceled"
                elif data['delay'] > 0:
                    txt = 'has a delay of %s min' % data['delay']
                else:
                    txt = 'is on time'

                msg.reply("Train %s (%s) %s, platform %s" % (
                    train,
                    data['scheduled_departure'].strftime("%H:%M"),
                    txt,
                    data['platform']
                ))

        if not has_ran:
            msg.reply("No teleporter available for now...")
