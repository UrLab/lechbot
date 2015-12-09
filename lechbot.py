import logging
from sys import stdout
from config import NICKNAME, CHANS, WAMP_HOST, WAMP_REALM
from plugins import load_all_plugins
from ircbot import CLIBot, IRCBot
from ircbot.text import parse_time
from datetime import datetime
import humanize
import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner


def main(loglevel, bot):
    """
    Run LechBot in an Autobahn application
    """
    humanize.i18n.activate('fr_FR')
    logging.basicConfig(
        stream=stdout, level=loglevel,
        format="%(asctime)s %(levelname)7s: %(message)s")

    class Component(ApplicationSession):
        @asyncio.coroutine
        def onJoin(self, details):
            def on_event(key, time, text):
                time = parse_time(time)
                # Ignore recent messages
                if (datetime.now() - time).total_seconds() < 120:
                    bot.say(text)
                    bot.log.debug("Got " + repr({
                        'key': key, 'time': time, 'text': text
                    }))
            yield from self.subscribe(on_event, u'incubator.actstream')
            yield from self.subscribe(on_event, u'hal.eventstream')

    runner = ApplicationRunner(WAMP_HOST, WAMP_REALM,
                               debug_wamp=False, debug=False)
    runner.run(Component)


if __name__ == "__main__":
    lvl = logging.INFO
    klass = CLIBot

    import argparse

    optparser = argparse.ArgumentParser(
        description=u"LechBot, le bot de #urlab")
    optparser.add_argument(
        "--irc", "-i", action='store_true',
        dest='online', default=False,
        help="Connect to IRC")
    optparser.add_argument(
        "--debug", "-d", action='store_true',
        dest='debug', default=False,
        help="Also output debug informations")
    options = optparser.parse_args()

    if options.debug:
        lvl = logging.DEBUG
    if options.online:
        klass = IRCBot

    bot = klass(NICKNAME, CHANS)
    load_all_plugins(bot)
    bot.command(r'\!help')(bot.help)

    @bot.command(r'tg %s$' % NICKNAME)
    def shut_up(msg):
        """Je meurs"""
        bot.log.info('Shutting down; asked by ' + msg.user.nick)
        exit()
    bot.connect()

    main(lvl, bot=bot)
