import asyncio
import logging
from sys import stdout

import humanize
import sentry_sdk

from chanconfig import CHANS
from config import MAIN_CHAN, NICKNAME, PORT, SENTRY_DSN, SERVER, BRIDGE_BOTS
from ircbot import CLIBot, IRCBot


def main(loglevel, klass, options):
    humanize.i18n.activate("fr_FR")
    fmt = "%(levelname)7s %(asctime)s | %(module)s:%(funcName)s | %(message)s"
    logging.basicConfig(stream=stdout, level=loglevel, format=fmt)

    if SENTRY_DSN:
        sentry_sdk.init(SENTRY_DSN, traces_sample_rate=1.0)

    bot = klass(NICKNAME, CHANS, bridge_bots=BRIDGE_BOTS, main_chan=MAIN_CHAN, local_only=options.local)

    @bot.command(r"tg %s$" % NICKNAME)
    def shut_up(msg):
        """Je meurs"""
        bot.log.info("Shutting down; asked by " + msg.user.nick)
        exit()

    bot.connect(host=SERVER, port=PORT)
    bot.log.info("Starting")

    if bot.local_only:
        bot.log.info(
            "You are in local mode, we will not try to poll from"
            " twitter, the incubator or any other distant api."
        )
        asyncio.get_event_loop().run_forever()
    else:
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    import argparse

    optparser = argparse.ArgumentParser(description=u"LechBot, le bot de #urlab")
    optparser.add_argument(
        "--irc",
        "-i",
        action="store_true",
        dest="online",
        default=False,
        help="Connect to IRC",
    )
    optparser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        dest="debug",
        default=False,
        help="Also output debug informations",
    )
    optparser.add_argument(
        "--local",
        "-l",
        action="store_true",
        dest="local",
        default=False,
        help="Don't try to connect to Twitter",
    )

    options = optparser.parse_args()

    lvl = logging.DEBUG if options.debug else logging.INFO
    klass = IRCBot if options.online else CLIBot
    main(lvl, klass, options)
