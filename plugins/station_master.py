import asyncio
from ircbot.plugin import BotPlugin
from datetime import datetime, timedelta
from datetime import time as dtime
import itertools
import functools
import aiohttp

CENTRAL = "Brussels-Central"
CHAPELLE = "Brussels-Chapelle/Brussels-Kapellekerk"

TRAIN_TIMES = [
    (dtime( 7, 15), dtime( 8, 15), CENTRAL, "S11778"),  # 07:51
    (dtime( 8, 15), dtime( 9, 15), CENTRAL, "S11779"),  # 08:51
    (dtime( 9, 15), dtime(10, 15), CENTRAL, "S11780"),  # 09:52
    (dtime(10, 15), dtime(11, 15), CENTRAL, "S11781"),  # 10:52
    (dtime(11, 15), dtime(12, 15), CENTRAL, "S11782"),  # 11:52

    (dtime(15, 15), dtime(16, 15), CHAPELLE, "S11765"),  # 16:06
    (dtime(16, 15), dtime(17, 15), CHAPELLE, "S11766"),  # 17:06
    (dtime(17, 15), dtime(18, 15), CHAPELLE, "S11767"),  # 18:05
    (dtime(18, 15), dtime(19, 20), CHAPELLE, "S11768"),  # 19:05
]

RULES = {
    'train_morning': [
        {"hour": [9], "minute": [40, 50], "weekday": [0, 1, 2, 3, 4]},
    ],
    'train_evening': [
        {"hour": [17], "minute": [49, 59], "weekday": [0, 1, 2, 3, 4]},
    ],
    # 'metro': [
    #     {"hour": [9], "minute": [15], "weekday": [1, 2, 3, 4, 5]},
    # ],
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

    def event(self, event_type):
        self.set_next_call(event_type)
        fun = getattr(self, "run_%s" % event_type)
        assert asyncio.iscoroutinefunction(fun)
        asyncio.ensure_future(fun())

    @asyncio.coroutine
    def run_train_morning(self):
        station = "Brussels-Central"
        train = "S11780"
        data = yield from self.get_delay(train, station)
        self.say(self.format_train(train, data))

    @asyncio.coroutine
    def run_train_evening(self):
        station = "Brussels-Chapelle/Brussels-Kapellekerk"
        train = "S11767"
        data = yield from self.get_delay(train, station)
        if data['delay'] < 5 or (data['scheduled_departure'] - datetime.now()) < timedelta(minutes=10):
            # Skip noise if no or little delay and depature is in the "far" future
            self.say(self.format_train(train, data))

    def get_delay(self, train_id, station):
        url = "https://api.irail.be/vehicle/?id=BE.NMBS.%s&format=json" % train_id

        response = yield from aiohttp.get(url)
        data = yield from response.json()
        stops = [s for s in data["stops"]["stop"] if s["station"] == station]
        if len(stops) != 1:
            raise Exception("More than one %s stop" % station)
        stop = stops[0]
        departure = datetime.fromtimestamp(int(stop['scheduledDepartureTime']))
        return {
            "canceled": stop["departureCanceled"] != "0",
            "delay": round(int(stop["departureDelay"]) / 60),
            "platform": stop['platform'],
            "is_normal_platform": stop['platforminfo']['normal'] == "1",
            "scheduled_departure": departure,
        }

    def set_next_call(self, event_type):
        at = self.get_next_instant(event_type)
        dt = (at - datetime.now()).total_seconds()
        self.loop.call_at(
            self.loop.time() + dt,
            functools.partial(self.event, event_type)
        )

    @BotPlugin.on_connect
    def boot(self):
        for event_type in RULES.keys():
            self.set_next_call(event_type)

    def format_train(self, train, data):
        if data['canceled']:
            status_txt = "est " + self.bot.text.bold(self.bot.text.red("annulé ❌"))
        elif data['delay'] > 0:
            status_txt = 'a un ' + self.bot.text.yellow('retard de %s min' % data['delay'])
        else:
            status_txt = 'est ' + self.bot.text.green('à temps')

        if data["is_normal_platform"]:
            platform_txt = ""
        else:
            platform_txt = self.bot.text.red("🚉 Changement de quai : quai %s." % data['platform'])

        return "Le %s de %s %s. %s" % (
            train[:2],
            data['scheduled_departure'].strftime("%H:%M"),
            status_txt,
            platform_txt
        )

    @BotPlugin.command(r'\!teleport')
    def teleport(self, msg):
        has_ran = False
        for start, stop, station, train in TRAIN_TIMES:
            if start < datetime.now().time() < stop:
                has_ran = True
                data = yield from self.get_delay(train, station)
                msg.reply(self.format_train(train, data))

        if not has_ran:
            msg.reply("Aucun téléporteur n'est disponible pour l'instant...")
