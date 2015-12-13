import asyncio
from time import time
from .helpers import spaceapi, private_api
from ircbot.plugin import BotPlugin

HAL_EVENTS = {
    'door_stairs': "Quelqu'un est de passage",
    'bell': "On sonne à la porte !",
    'heater_on': "Le radiateur est allumé",
    'heater_off': "Le radiateur est éteint",
    'hs_open': "Le hackerspace est ouvert ! RAINBOWZ NSA PONEYZ EVERYWHERE \\o/",
    'hs_close': "Le hackerspace est fermé ! N'oubliez pas d'éteindre les lumières et le radiateur.",
    'passage': "Il y a quelqu'un à l'intérieur",
    'kitchen_move': "Il y a du mouvement dans la cuisine",
}

EVENTS_RATELIMIT = {
    'passage': 3600,
    'kitchen_move': 60,
    'door_stairs': 60,
}


class Space(BotPlugin):
    def __init__(self):
        self.EVENTS_LAST_SEEN = {}

    @asyncio.coroutine
    def on_hal_event(self, evt):
        now = time()
        if evt in HAL_EVENTS:
            if evt in self.EVENTS_LAST_SEEN and\
               evt in EVENTS_RATELIMIT and\
               now - self.EVENTS_LAST_SEEN[evt] < EVENTS_RATELIMIT[evt]:
                    self.bot.log.info("Drop HAL event " + evt + " (rate limit)")
                    return
            self.bot.say(HAL_EVENTS[evt])
            self.EVENTS_LAST_SEEN[evt] = now
            self.bot.log.info("HAL event " + evt)

    # @BotPlugin.on_connect
    # def on_connect(self):
    #     """Subscribe to HAL events"""
    #     yield from lechbot_event_consume(on_hal_event)
    #     self.bot.log.info("Listening to HAL events !")

    # @BotPlugin.command(r'\!poke')
    # def poke(self, msg):
    #     """Dit gentiment bonjour aux personnes présentes à UrLab"""
    #     yield from lechbot_notif('poke')
    #     msg.reply("Coucou HAL !!! /o/", hilight=True)
    #     self.bot.log.info('Poke by ' + msg.user.nick)

    @BotPlugin.command(r'\!status')
    def spacestatus(self, msg):
        """Affiche le statut actuel du hackerspace"""
        space = yield from spaceapi()

        when = self.bot.naturaltime(space['state']['lastchange'])
        if space['state']['open']:
            msg.reply("Le hackerspace a ouvert " + when)
        else:
            msg.reply("Le hackerspace a fermé " + when)

    @BotPlugin.command(r'sudo \!(open|close)')
    def change_spacestatus(self, msg):
        """Change le statut du hackerspace en cas de dysfonctionnement de HAL"""
        status = msg.args[0]
        yield from private_api('/space/change_status', {
            'open': 1 if status == "open" else 0
        })
        yield from self.spacestatus(msg)
        self.bot.log.info(status + ' UrLab by ' + msg.user.nick)
