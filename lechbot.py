import logging
from sys import stdout
from datetime import datetime
from time import time

from config import (BOT_CLASS, NICKNAME, CHANS, LOGLEVEL,
                    INCUBATOR, INCUBATOR_SECRET, SPACEAPI)
from ircbot.persist import Persistent
import aiohttp
import asyncio
import humanize
humanize.i18n.activate('fr_FR')

logging.basicConfig(
    stream=stdout, level=LOGLEVEL,
    format="%(asctime)s %(levelname)7s: %(message)s")
logger = logging.getLogger(__name__)


bot = BOT_CLASS(NICKNAME, CHANS)

bot.command(r'\!help')(bot.help)


def make_topic(msg, new_topic=None, new_music=None):
    template = {'last_changed': None, 'text': "", 'changed_by': None}
    with Persistent('topic.json') as current_topic:
        for key, newval in [('motd', new_music), ('topic', new_topic)]:
            oldval = current_topic.setdefault(key, dict(template))
            if newval is not None:
                oldval['last_changed'] = time()
                oldval['changed_by'] = msg.user.nick
                oldval['text'] = newval
        topic_string = ' :: '.join(
            current_topic[x]['text'] for x in ('motd', 'topic'))
        bot.set_topic(topic_string, msg.chan)


@asyncio.coroutine
def private_api(endpoint, data):
    """Call UrLab incubator private API"""
    url = INCUBATOR
    if url[-1] != '/':
        url += '/'
    url += endpoint.lstrip('/')
    data['secret'] = INCUBATOR_SECRET

    response = yield from aiohttp.post(url, data=data)
    assert response.status == 200
    yield from response.release()


@bot.command(r'tg %s$' % NICKNAME)
def shut_up(msg):
    """Je meurs"""
    logger.info('Shutting down; asked by ' + msg.user.nick)
    exit()


@bot.command(r'\!motd +(https?://[^ ]+)')
def music_of_the_day(msg):
    """Change la musique du jour"""
    try:
        yield from private_api('/space/change_motd', {
            'nick': msg.user.nick,
            'url': msg.args[0]
        })
        logger.info("Music of the day changed by " + msg.user.nick)
        make_topic(msg, new_music=msg.args[0])
        msg.reply("tu viens de changer la musique du jour >>> d*-*b <<<",
                  hilight=True)
    except:
        msg.reply("Impossible de changer la musique du jour !")


@bot.command(r'\!topic +([^ ].+)')
def topic(msg):
    """Change l'annonce du chat"""
    make_topic(msg, new_topic=msg.args[0])
    logger.info("Topic changed by " + msg.user.nick)


@bot.command(r'\!(topic|motd)')
def tell_topic(msg):
    """Qui a changé le topic/MotD, et quand ?"""
    key = msg.args[0]
    with Persistent('topic.json') as topic:
        if key not in topic or topic[key]['last_changed'] is None:
            msg.reply(key + " n'a pas encore été changé")
        else:
            when = humanize.naturaltime(
                datetime.fromtimestamp(topic[key]['last_changed']))
            msg.reply("Changé " + when + " par " + topic[key]['changed_by'])


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
    yield from private_api('/space/change_status', {
        'open': 1 if status == "open" else 0
    })
    yield from spacestatus(msg)
    logger.info(status + ' UrLab by ' + msg.user.nick)

if __name__ == "__main__":
    bot.run()
