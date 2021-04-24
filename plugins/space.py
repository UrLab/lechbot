import asyncio
from time import time

from ircbot.plugin import BotPlugin

from .helpers import private_api, spaceapi


class Space(BotPlugin):
    # @BotPlugin.command(r'\!poke')
    # def poke(self, msg):
    #     """Dit gentiment bonjour aux personnes présentes à UrLab"""
    #     await lechbot_notif('poke')
    #     msg.reply("Coucou HAL !!! /o/", hilight=True)
    #     self.bot.log.info('Poke by ' + msg.user)

    @BotPlugin.command(r"\!status")
    async def spacestatus(self, msg):
        """Affiche le statut actuel du hackerspace"""
        space = await spaceapi()

        when = self.bot.naturaltime(space["state"]["lastchange"])
        if space["state"]["open"]:
            msg.reply("Le hackerspace a ouvert " + when)
        else:
            msg.reply("Le hackerspace a fermé " + when)

    @BotPlugin.command(r"sudo \!(open|close)")
    async def change_spacestatus(self, msg):
        """Change le statut du hackerspace en cas de dysfonctionnement de HAL"""
        status = msg.args[0]
        await private_api(
            "/space/change_status", {"open": 1 if status == "open" else 0}
        )
        msg.reply("sudo request sent !")
        self.bot.log.info(status + " UrLab by " + msg.user)
