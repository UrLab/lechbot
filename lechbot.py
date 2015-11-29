import logging
from sys import stdout
from datetime import datetime

from config import (
    NICKNAME, CHANS,
    INCUBATOR_SECRET, SPACEAPI, STATUS_CHANGE_URL)
from ircbot import IRCBot, MockIRCBot
import aiohttp
import humanize
humanize.i18n.activate('fr_FR')

logging.basicConfig(
    stream=stdout, level=logging.INFO,
    format="%(asctime)s %(levelname)7s: %(message)s")
logger = logging.getLogger(__name__)


bot = MockIRCBot(NICKNAME, CHANS)

bot.command(r'\!help')(bot.help)


@bot.command(r'tg %s$' % NICKNAME)
def shut_up(msg):
    """Je meurs"""
    logger.info('Shutting down; asked by ' + msg.user.nick)
    exit()


@bot.command(r'\!motd +(https?://[^ ]+)')
def music_of_the_day(msg):
    """Change la musique du jour"""
    msg.reply("Not implemented")
    logger.info("Music of the day changed by " + msg.user.nick)


@bot.command(r'\!topic +([^ ].+)')
def topic(msg):
    """Change l'annonce du chat"""
    msg.reply("Not implemented")
    logger.info("Topic changed by " + msg.user.nick)


@bot.command(r'\!twitter +([^ ].+)')
def tweet_message(msg):
    """Tweete avec le compte de UrLab (@urlabbxl)"""
    text = msg.args[0]
    msg.reply("Not implemented")
    logger.info('Tweet "' + text + '" by ' + msg.user.nick)


@bot.command(r'\!retweet https?://.*twitter.com/([^/]+)/status/(\d+)')
def retweet_message(msg):
    """Retweete un message avec le compte de UrLab (@urlabbxl)"""
    user, status = msg.args
    msg.reply("Not implemented")
    logger.info('Retweet @' + user + ' by ' + msg.user.nick)


@bot.command(r'\!tw +([^ ].+)')
def add_to_next_tw(msg):
    """Ajoute un point à l'ordre du jour de la prochaine réunion"""
    point = msg.args[0]
    msg.reply("Not implemented")
    logger.info('Add "' + point + '" to next tw by ' + msg.user.nick)


@bot.command(r'\!tw')
def next_tw(msg):
    """Affiche l'ordre du jour de la prochaine réunion"""
    msg.reply("Not implemented")


@bot.command(r'\!poke')
def poke(msg):
    """Dit gentiment bonjour aux personnes présentes à UrLab"""
    msg.reply("Not implemented")
    logger.info('Poke by ' + msg.user.nick)


@bot.command(r'\!status')
def spacestatus(msg):
    """Affiche le statut actuel du hackerspace"""
    response = yield from aiohttp.get(SPACEAPI)
    space = yield from response.json()

    when = humanize.naturaltime(
        datetime.fromtimestamp(space['state']['lastchange']))
    if space['state']['open']:
        msg.reply("Le hackerspace a ouvert " + when)
    else:
        msg.reply("Le hackerspace a fermé " + when)

    yield from response.release()


@bot.command(r'sudo \!(open|close)')
def change_spacestatus(msg):
    """Change le statut du hackerspace en cas de dysfonctionnement de HAL"""
    status = msg.args[0]
    response = yield from aiohttp.post(STATUS_CHANGE_URL, data={
        "secret": INCUBATOR_SECRET,
        "open": 1 if status == 'open' else 0
    })

    yield from spacestatus(msg)
    yield from response.release()
    logger.info(status + ' UrLab by ' + msg.user.nick)

if __name__ == "__main__":
    bot.run()
