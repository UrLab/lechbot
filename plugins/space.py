from .helpers import spaceapi, private_api


def load(bot):
    @bot.command(r'\!poke')
    def poke(msg):
        """Dit gentiment bonjour aux personnes présentes à UrLab"""
        msg.reply("Not implemented")
        bot.log.info('Poke by ' + msg.user.nick)


    @bot.command(r'\!status')
    def spacestatus(msg):
        """Affiche le statut actuel du hackerspace"""
        space = yield from spaceapi()

        when = bot.naturaltime(space['state']['lastchange'])
        if space['state']['open']:
            msg.reply("Le hackerspace a ouvert " + when)
        else:
            msg.reply("Le hackerspace a fermé " + when)


    @bot.command(r'sudo \!(open|close)')
    def change_spacestatus(msg):
        """Change le statut du hackerspace en cas de dysfonctionnement de HAL"""
        status = msg.args[0]
        yield from private_api('/space/change_status', {
            'open': 1 if status == "open" else 0
        })
        yield from spacestatus(msg)
        bot.log.info(status + ' UrLab by ' + msg.user.nick)
