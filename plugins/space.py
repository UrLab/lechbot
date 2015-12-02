import asyncio
from time import time
from .helpers import spaceapi, private_api, lechbot_notif, lechbot_event_consume

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


def load(bot):
    EVENTS_LAST_SEEN = {}

    @asyncio.coroutine
    def on_hal_event(evt):
        now = time()
        if evt in HAL_EVENTS:
            if evt in EVENTS_LAST_SEEN and\
               evt in EVENTS_RATELIMIT and\
               now - EVENTS_LAST_SEEN[evt] < EVENTS_RATELIMIT[evt]:
                    bot.log.info("Drop HAL event " + evt + " (rate limit)")
                    return
            bot.say(HAL_EVENTS[evt])
            EVENTS_LAST_SEEN[evt] = now
            bot.log.info("HAL event " + evt)

    @bot.on_connect
    def on_connect():
        """Subscribe to HAL events"""
        yield from lechbot_event_consume(on_hal_event)
        bot.log.info("Listening to HAL events !")

    @bot.command(r'\!poke')
    def poke(msg):
        """Dit gentiment bonjour aux personnes présentes à UrLab"""
        yield from lechbot_notif('poke')
        msg.reply("Coucou HAL !!! /o/", hilight=True)
        bot.log.info('Poke by ' + msg.user.nick)

    @bot.command(r'\!status')
    def spacestatus(msg):
        """Affiche le statut actuel du hackerspace"""
        space = yield from spaceapi()

        when = bot.naturaltime(space['state']['lastchange'])
        if space['state']['open']:
            msg.reply("Le hackerspace a ouvert " + when)
        else:
            msg.reply("Le hackerspace a fermé " + when)

    @bot.command(r'sudo \!(open|close)')
    def change_spacestatus(msg):
        """Change le statut du hackerspace en cas de dysfonctionnement de HAL"""
        status = msg.args[0]
        yield from private_api('/space/change_status', {
            'open': 1 if status == "open" else 0
        })
        yield from spacestatus(msg)
        bot.log.info(status + ' UrLab by ' + msg.user.nick)
