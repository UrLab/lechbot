import random
import re

from ircbot.plugin import BotPlugin

from .helpers import public_api


class Giphy(BotPlugin):
    def __init__(self, giphy_key):
        self.giphy_key = giphy_key

    def clean_url(self, url):
        m = re.match(r"^(https://.+/giphy\.gif).*", url)
        if m:
            return m.group(1)
        return url

    async def search_gif(self, query):
        url = "http://api.giphy.com/v1/gifs/search?api_key={}&q={}"
        q = query.replace(" ", "+")
        r = await public_api(url.format(self.giphy_key, q))
        chosen = random.choice(r["data"])
        return self.clean_url(chosen["images"]["original"]["url"])

    @BotPlugin.command(r"\!gif (#[\w\d_-]+) (.+)")
    async def gif(self, msg):
        """Cherche un gif et le poste sur un autre chan"""
        gif = await self.search_gif(msg.args[1])
        reply = "{}: {}".format(msg.user, gif)
        self.bot.say(reply, target=msg.args[0])

    @BotPlugin.command(r"\!gif (.+)")
    async def gif_here(self, msg):
        """Cherche un gif et le poste ici"""
        gif = await self.search_gif(msg.args[0])
        msg.reply(gif)
