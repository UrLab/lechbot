from ircbot.plugin import BotPlugin

class React(BotPlugin):
    @BotPlugin.command(r'\!react')
    def react(self, msg):
        msg.reply("Oh mon dieu! C'est réactif!")