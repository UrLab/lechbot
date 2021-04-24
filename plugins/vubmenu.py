from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup

from ircbot.plugin import BotPlugin
from ircbot.text import parse_time


def parse_section(node):
    date = parse_time(node.select(".date-display-single")[0].text.strip())
    menu = dict(x.text.strip().split("\n") for x in node.select("tr"))
    return date, menu


class VUBMenu(BotPlugin):
    @BotPlugin.command(r"\!menu")
    def menu_of_the_day(self, msg):
        """Affiche le menu du jour de la cafétaria de la VUB"""
        url = "https://my.vub.ac.be/en/restaurant/etterbeek"
        response = yield from aiohttp.get(url)
        content = yield from response.read()
        response.close()

        page = BeautifulSoup(content, "html.parser")
        sections = page.select("#content .view-content .views-row")
        menu = dict(map(parse_section, sections))
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        if today not in menu:
            msg.reply(
                self.bot.text.red("Aucun menu trouvé au restaurant de la VUB (Plaine)")
            )
        else:
            msg.reply(
                self.bot.text.purple(
                    "Menu d'aujourd'hui au restaurant de la VUB (Plaine):"
                )
            )
            for stand, meal in menu[today].items():
                msg.reply(self.bot.text.bold(stand + ": ") + meal)
