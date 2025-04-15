from functools import partial, wraps
from .command import Command, ECommandType


class BotPlugin:
    comment_tag_id = 0

    def load(self, bot, chan):
        self.bot = bot
        self.chan = chan
        callbacks = {
            ECommandType.COMMAND: [],
            ECommandType.SUDO_COMMAND: [],
            ECommandType.JOIN: [],
            ECommandType.CONNECT: []
        }

        # form all attrs of self, get the ones that are commands
        for member in map(partial(getattr, self), dir(self)):
            if hasattr(member, "_command"):
                c = member._command

                clbk = BotPlugin.partial_wrap(c.callback, self)
                callbacks[member._command_type].append(Command(
                                            clbk,
                                            c.id,
                                            c.regex,
                                            c.need_sudo,
                                            c.public)
                )

        callbacks[ECommandType.COMMAND].sort(key=lambda c: c.id)
        return callbacks

    @staticmethod
    def partial_wrap(func, *partial_args, **partial_kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*partial_args, *args, **partial_kwargs, **kwargs)

        return wrapper


    def say(self, text, strip_text=False):
        self.bot.say(text, target=self.chan, strip_text=strip_text)

    def set_topic(self, text):
        self.bot.set_topic(text, target=self.chan)

    @classmethod
    def command(cls, pattern, need_sudo=False, help=True):
        """
            @param pattern : regex to apply to messages
            @param need_sudo : is the command only usable with sudo
            @param no_help : do not display the command in !help
        """
        cls.comment_tag_id += 1
        # Here's the trick. We keep a static id, which is incremented any time
        # we declare a new command, so that we know in which order they have
        # been declared. This information is used to build the list of commands
        # in the right order, only inside a single plugin class.

        def decorator(func):
            command_type =  ECommandType.SUDO_COMMAND if need_sudo else ECommandType.COMMAND

            func._command_type = command_type
            func._command = Command(func, cls.comment_tag_id, pattern, need_sudo, help)

            return func # no real change is made, we only use wrapper for the '@' syntax

        return decorator

    @classmethod
    def on_join(cls, func):
        func._command_type = ECommandType.JOIN
        func._command = Command(func, cls.comment_tag_id)

        return func

    @classmethod
    def on_connect(cls, func):
        func._command_type = ECommandType.CONNECT
        func._command = Command(func, cls.comment_tag_id)

        return func


class HelpPlugin(BotPlugin):
    @BotPlugin.command(r"\!help +(#[^ ]+)")
    def tell_help_for_chan(self, msg):
        """Affiche la liste des commandes pour un chan"""
        chan = msg.args[0].lower()
        if chan not in self.bot.channels:
            msg.reply("Pas de commande sur le chan %s" % chan, hilight=True)
        else:
            commands = self.bot.channels.get(chan, {}).get(ECommandType.COMMAND, [])
            msg.reply(self.bot.text.red("Aide pour " + chan), private=True)
            for command in commands:
                if not command.public: # dont show not public commands, usefull to hide some internal commands
                    continue
                cmd = self.bot.text.bold(command.regex.pattern.replace("\\", ""))
                reply = cmd
                if command.callback.__doc__:
                    doc = command.callback.__doc__.strip()
                    if doc:
                        reply += ": " + doc
                msg.reply(reply, private=True)

    @BotPlugin.command(r"\!help")
    def tell_help(self, msg):
        """Affiche la liste des commandes du chan où c'est demandé"""
        msg.args = [self.chan]
        self.tell_help_for_chan(msg)
