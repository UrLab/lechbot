from ircbot.plugin import BotPlugin
from random import choice

class Ascii(BotPlugin):
    @BotPlugin.command(r'\!penisbird')
    def penisbird(self, msg):
        msg.reply(" < )\n ( \\\n.X\n8====D")


    @BotPlugin.command(r'\!train')
    def train(self, msg):
        msg.reply("._||__|  |  ______   ______   ______ \n"
                  "(        | |      | |      | |      |\n"
                  "/-()---() ~ ()--() ~ ()--() ~ ()--()\n")

    @BotPlugin.command(r'\!whoIsGod')
    def whoIsGod(self, msg):
        msg.reply("  _ _____ _ _            \n"
                  " (_)_   _(_) |_ ___ _  _ \n"
                  " | | | | | |  _/ _ \ || |\n"
                  " |_| |_| |_|\__\___/\_,_|\n")

    @BotPlugin.command(r'\!shutup')
    def shutup(self, msg):
        msg.reply("┌∩┐(◣_◢)┌∩┐\n")

    @BotPlugin.command(r'\!rose')
    def rose(self, msg):
        msg.reply("--------{---(@\n")

    @BotPlugin.command(r'\!happybithday')
    def happybirthday(self, msg):
        msg.reply("¸¸♬·¯·♩¸¸♪·¯·♫¸¸Happy Birthday To You¸¸♬·¯·♩¸¸♪·¯·♫¸¸\n")

    @BotPlugin.command(r'\!idonotcare')
    def idonotcare(self, msg):
        msg.reply("╭∩╮（︶︿︶）╭∩╮\n")

    @BotPlugin.command(r'\!dice')
    def dice(self, msg):
        msg.reply("[::]\n")

    @BotPlugin.command(r'\!spider')
    def spider(self, msg):
        msg.reply("/X\('-')/X\\n")

    @BotPlugin.command(r'\!huhu')
    def huhu(self, msg):
        msg.reply("█▬█ █▄█ █▬█ █▄█\n")

    @BotPlugin.command(r'\!hugme')
    def hugme(self, msg):
        msg.reply("(っ◕‿◕)っ\n")

    @BotPlugin.command(r'\!bunny')
    def bunny(self, msg):
        msg.reply("(\__/)\n"
                  "(O.o )\n"
                  "(> < )\n")

    @BotPlugin.command(r'\!dragons')
    def dragons(self, msg):
        msg.reply(" /\_./o__        __o\._/\\n"
                  "(/^/(_^^'        '^^_)\^\)\n"
                  "_.(_.)_            _(._)._.\n")

    @BotPlugin.command(r'\!thisslowos')
    def thisslowos(self, msg):
        msg.reply("             _.-;;-._\n"
                  "      '-..-'|   ||   |\n"
                  "      '-..-'|_.-;;-._|\n"
                  "      '-..-'|   ||   |\n"
                  "jgs   '-..-'|_.-''-._|\n")

    @BotPlugin.command(r'\!beer')
    def beer(self, msg):
        msg.reply("   oOOOOOo\n"
                  "  ,|    oO\n"
                  " //|     |\n"
                  " \\|     |\n"
                  "   `-----`\n")

    @BotPlugin.command(r'\!drink')
    def drink(self, msg):
        msg.reply("     _*\n"
                  ".---/ `\\n"
                  "|~~~~|`'\n"
                  " \  /\n"
                  "  )(\n"
                  " /__\\n")

    @BotPlugin.command(r'\!key')
    def key(self, msg):
        msg.reply("    .--.\n"
                  "   /.-. '----------.\n"
                  "   \'-' .--"--""-"-'\n"
                  "jgs '--'\n")

    @BotPlugin.command(r'\!letsplaychess')
    def letsplaychess(self, msg):
        msg.reply("♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜\n"
                  "♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟\n"
                  "… … … … … … … …\n"
                  "♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙\n"
                  "♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖\n")

    @BotPlugin.command(r'\!throwdice')
    def throwdice(self, msg):
        dices = "⚀⚁⚂⚃⚄⚅"
        msg.reply("%s\n" % choice(dices))
