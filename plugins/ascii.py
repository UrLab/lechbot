from ircbot.plugin import BotPlugin


class Ascii(BotPlugin):
    @BotPlugin.command(r'\!penisbird')
    def penisbird(self, msg):
        msg.reply(" < )\n ( \\\n.X\n8====D")


    @BotPlugin.command(r'\!train')
    def train(self, msg):
        msg.reply("._||__|  |  ______   ______   ______ \n"
                  "(        | |      | |      | |      |\n"
                  "/-()---() ~ ()--() ~ ()--() ~ ()--()\n")
