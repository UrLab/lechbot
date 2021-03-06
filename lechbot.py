import logging
from sys import stdout
from config import NICKNAME, WAMP_HOST, WAMP_REALM, MAIN_CHAN
from ircbot import CLIBot, IRCBot
from ircbot.text import parse_time
from datetime import datetime
import humanize
import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

from chanconfig import CHANS, RATELIMIT


def run_wamp(bot):
    """
    Run LechBot in an Autobahn application
    """
    class Component(ApplicationSession):
        @asyncio.coroutine
        def onJoin(self, details): # NOQA
            bot.log.info("Joined WAMP realm !")

            last_seen_keys = {}

            def on_event(key, time, text):
                now = datetime.now()
                time = parse_time(time)

                # Outdated message
                if (now - time).total_seconds() > 120:
                    bot.log.info("Got outdated event " + repr({
                        'key': key, 'time': time, 'text': text
                    }))
                    return

                # Rate limit
                last_seen = last_seen_keys.get(key, datetime.fromtimestamp(0))
                if (now - last_seen).total_seconds() < RATELIMIT.get(key, 0):
                    bot.log.info("Got rate-limited event " + repr({
                        'key': key, 'time': time, 'text': text
                    }) + " / Last seen: " + repr(last_seen))
                    return

                bot.say(text, target=MAIN_CHAN)
                bot.log.debug("Got " + repr({
                    'key': key, 'time': time, 'text': text
                }))

                last_seen_keys[key] = now
            yield from self.subscribe(on_event, u'incubator.actstream')
            yield from self.subscribe(on_event, u'hal.eventstream')

    runner = ApplicationRunner(WAMP_HOST, WAMP_REALM)
    runner.run(Component)


def main(loglevel, klass, options):
    humanize.i18n.activate('fr_FR')
    fmt = "%(levelname)7s %(asctime)s | %(module)s:%(funcName)s | %(message)s"
    logging.basicConfig(
        stream=stdout, level=loglevel,
        format=fmt)

    bot = klass(NICKNAME, CHANS, main_chan=MAIN_CHAN, local_only=options.local)

    @bot.command(r'tg %s$' % NICKNAME)
    def shut_up(msg):
        """Je meurs"""
        bot.log.info('Shutting down; asked by ' + msg.user.nick)
        exit()
    bot.connect(host="chat.freenode.net", port=6697)
    bot.log.info("Starting")

    if bot.local_only:
        bot.log.info(
            "You are in local mode, we will not try to poll from"
            " crossbar, twitter, the incubator or any other distant api."
        )
        asyncio.get_event_loop().run_forever()
    else:
        try:
            run_wamp(bot)
        except:
            bot.log.exception("WAMP not available !")
            asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
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
    optparser.add_argument(
        "--local", "-l", action='store_true',
        dest='local', default=False,
        help="Don't try to connect to crossbar or Twitter")

    options = optparser.parse_args()

    lvl = logging.DEBUG if options.debug else logging.INFO
    klass = IRCBot if options.online else CLIBot
    main(lvl, klass, options)
