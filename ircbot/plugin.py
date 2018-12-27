import re
from functools import partial


class BotPlugin:
    comment_tag_id = 0

    def load(self, bot, chan):
        self.bot = bot
        self.chan = chan
        callbacks = {
            'commands': [],
            'on_join': [],
            'on_connect': [],
        }
        for member in map(partial(getattr, self), dir(self)):
            if hasattr(member, '_botplugin_special_tag_pattern'):
                pattern = member._botplugin_special_tag_pattern
                callbacks['commands'].append((re.compile(pattern), member))
            elif hasattr(member, '_botplugin_special_tag_onjoin'):
                callbacks['on_join'].append(member)
            elif hasattr(member, '_botplugin_special_tag_onconnect'):
                callbacks['on_connect'].append(member)
        callbacks['commands'].sort(key=lambda P: P[1]._special_tag_id)
        return callbacks

    def say(self, text, strip_text=False):
        self.bot.say(text, target=self.chan, strip_text=strip_text)

    def set_topic(self, text):
        self.bot.set_topic(text, target=self.chan)

    @classmethod
    def command(cls, pattern):
        cls.comment_tag_id += 1
        # Here's the trick. We keep a static id, which is incremented any time
        # we declare a new command, so that we know in which order they have
        # been declared. This information is used to build the list of commands
        # in the right order, only inside a single plugin class.

        def wrapper(func):
            func._botplugin_special_tag_pattern = pattern
            func._special_tag_id = cls.comment_tag_id
            return func
        return wrapper

    @staticmethod
    def on_join(func):
        func._botplugin_special_tag_onjoin = True
        return func

    @staticmethod
    def on_connect(func):
        func._botplugin_special_tag_onconnect = True
        return func


class HelpPlugin(BotPlugin):
    @BotPlugin.command(r'\!help +(#[^ ]+)')
    def tell_help_for_chan(self, msg):
        """Affiche la liste des commandes pour un chan"""
        chan = msg.args[0].lower()
        if chan not in self.bot.channels:
            msg.reply("Pas de commande sur le chan %s" % chan, hilight=True)
        else:
            msg.reply("Je te réponds en privé ;)", hilight=True)
            commands = self.bot.channels.get(chan, {}).get('commands', [])
            msg.reply(self.bot.text.red("Aide pour " + chan), private=True)
            for (pattern, func) in commands:
                if func.__doc__:
                    doc = func.__doc__.strip()
                    cmd = self.bot.text.bold(pattern.pattern.replace('\\', ''))
                    if doc:
                        msg.reply(cmd + ': ' + doc, private=True)

    @BotPlugin.command(r'\!help')
    def tell_help(self, msg):
        """Affiche la liste des commandes du chan où c'est demandé"""
        msg.args = [self.chan]
        self.tell_help_for_chan(msg)
