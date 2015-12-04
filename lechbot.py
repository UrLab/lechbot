import logging
from sys import stdout
from config import BOT_CLASS, NICKNAME, CHANS, LOGLEVEL
from plugins import load_all_plugins
from sys import argv
import humanize


def main(loglevel):
    humanize.i18n.activate('fr_FR')
    logging.basicConfig(
        stream=stdout, level=loglevel,
        format="%(asctime)s %(levelname)7s: %(message)s")

    bot = BOT_CLASS(NICKNAME, CHANS)

    @bot.command(r'tg %s$' % NICKNAME)
    def shut_up(msg):
        """Je meurs"""
        bot.log.info('Shutting down; asked by ' + msg.user.nick)
        exit()

    load_all_plugins(bot)
    bot.command(r'\!help')(bot.help)
    bot.run()


if __name__ == "__main__":
    lvl = LOGLEVEL
    if len(argv) > 1 and argv[1] in ["--debug", "-d"]:
        lvl = logging.DEBUG
    main(lvl)
