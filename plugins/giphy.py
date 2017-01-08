from .helpers import public_api
from ircbot.plugin import BotPlugin
import random


class Giphy(BotPlugin):
    def __init__(self, giphy_key):
        self.giphy_key = giphy_key

    def search_gif(self, query):
        url = "http://api.giphy.com/v1/gifs/search?api_key={}&q={}"
        q = query.replace(' ', '+')
        r = yield from public_api(url.format(self.giphy_key, q))
        choosed = random.choice(r['data'])
        return choosed['images']['original']['url']

    @BotPlugin.command(r'\!gif (#[\w\d_-]+) (.+)')
    def gif(self, msg):
        """Cherche un gif et le poste sur un autre chan"""
        gif = yield from self.search_gif(msg.args[1])
        self.bot.say(gif, target=msg.args[0])

    @BotPlugin.command(r'\!gif (.+)')
    def gif_here(self, msg):
        """Cherche un gif et le poste ici"""
        gif = yield from self.search_gif(msg.args[0])
        msg.reply(gif)
