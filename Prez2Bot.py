import logging
from sys import stdout
from plugins.urls import load as load_urls
from ircbot import CLIBot, IRCBot
import humanize

NICKNAME, CHANS = 'Prez2Bot', ['#ci']


def main(loglevel, bot_class):
    humanize.i18n.activate('fr_FR')
    logging.basicConfig(
        stream=stdout, level=loglevel,
        format="%(asctime)s %(levelname)7s: %(message)s")

    bot = bot_class('Prez2Bot', ['#ci'])

    @bot.command(r'tg %s$' % NICKNAME)
    def shut_up(msg):
        """Je meurs"""
        bot.log.info('Shutting down; asked by ' + msg.user.nick)
        exit()

    load_urls(bot)
    bot.command(r'\!help')(bot.help)
    bot.run()


if __name__ == "__main__":
    lvl = logging.INFO
    klass = CLIBot

    import argparse

    optparser = argparse.ArgumentParser(
        description=u"Prez2Bot, le bot de #ci")
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
    main(lvl, klass)
