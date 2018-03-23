from .helpers import public_api
from ircbot.plugin import BotPlugin
import random
import re


class Giphy(BotPlugin):
    def __init__(self, giphy_key):
        self.giphy_key = giphy_key

    def clean_url(self, url):
        m = re.match(r'^(https://.+/giphy\.gif).*', url)
        if m:
            return m.group(1)
        return url

    def search_gif(self, query):
        url = "http://api.giphy.com/v1/gifs/search?api_key={}&q={}"
        q = query.replace(' ', '+')
        r = yield from public_api(url.format(self.giphy_key, q))
        choochoosed = random.choice(r['data'])
        return self.clean_url(choosed['images']['original']['url'])

    @BotPlugin.command(r'\!gif (#[\w\d_-]+) (.+)')
    def gif(self, msg):
        """Cherche un gif et le poste sur un autre chan"""
        gif = yield from self.search_gif(msg.args[1])
        reply = "{}: {}".format(msg.user, gif)
        self.bot.say(reply, target=msg.args[0])

    @BotPlugin.command(r'\!gif (.+)')
    def gif_here(self, msg):
        """Cherche un gif et le poste ici"""
        gif = yield from self.search_gif(msg.args[0])
        msg.reply(gif)
