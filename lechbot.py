import logging
from sys import stdout
from config import BOT_CLASS, NICKNAME, CHANS, LOGLEVEL
from plugins import load_all_plugins
import humanize

humanize.i18n.activate('fr_FR')
logging.basicConfig(
    stream=stdout, level=LOGLEVEL,
    format="%(asctime)s %(levelname)7s: %(message)s")


bot = BOT_CLASS(NICKNAME, CHANS)


@bot.command(r'tg %s$' % NICKNAME)
def shut_up(msg):
    """Je meurs"""
    bot.log.info('Shutting down; asked by ' + msg.user.nick)
    exit()

load_all_plugins(bot)
bot.command(r'\!help')(bot.help)

if __name__ == "__main__":
    bot.run()
