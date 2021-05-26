.. toctree::

Quickstart
==========

This is the most simple bot: it connects to libera, join ``#my_chan``, and
register a command ``!hello``, which always replies ``world``.

::

    from ircbot import IRCBot

    bot = IRCBot("AnnaBot", {'#my_chan': []})

    @bot.command(r'\!hello')
    def hello(msg):
        msg.reply("World")

    bot.connect(host="irc.libera.chat", port=6697).run()


Captures
--------

Regexp captures in a command definition are available in ``msg.args``. Named
captures are also available in ``msg.kwargs``.

::

    @bot.command(r'\!hello +([^ ]+)')
    def hello_someone(msg):
        msg.reply("Hello " + msg.args[0])


Reply options
-------------

Hilight made easy.

::
    
    @bot.command(r'\!hello +([^ ]+)')
    def hello_someone(msg):
        msg.reply("Hello " + msg.args[0])
        msg.reply("I just Hello'ed " + msg.args[0], hilight=True)


Reply in private conversation is also this simple:

::
    
    @bot.command(r'\!hello +([^ ]+)')
    def hello_someone(msg):
        msg.reply("Hello " + msg.args[0])
        msg.reply("I just Hello'ed " + msg.args[0], private=True)


Backends
--------

For testing purposes, you may bypass IRC and have a simple command line REPL
for interacting with your bot

::

    from ircbot import CLIBot

    bot = CLIBot("AnnaBot", {'#my_chan': []})
    bot.connect().run()


Plugins
-------

Use plugins to split functionalities in modular units. The bot of our first
example becomes

::

    from ircbot import IRCBot, BotPlugin

    class Hello(BotPlugin):
        @BotPlugin.command(r'\!hello')
        def hello(self, msg):
            msg.reply("world")

    bot = IRCBot("AnnaBot", {'#my_chan': [Hello()]})
    bot.connect(host="irc.libera.chat", port=6697).run()


API Reference
=============

Abstract base bot
-----------------

LechBot is built on a modular design. An abstract bot class define a minimal
interface and logic to load and dispatch plugins for different channels.
Backends implement this interface and provide the communication with a server
or a mock.

.. automodule:: ircbot.abstractbot
    :members:


Backends
--------

The implemented backends are currently:

IRCBot
......

This backend connects to an IRC server

.. automodule:: ircbot.ircbot
    :members:

CLIBot
......

This backend provide a simple command line REPL

.. automodule:: ircbot.clibot
    :members:

TestBot
.......

This backend allows to write functional tests for plugins

.. automodule:: ircbot.testbot
    :members:


Plugins
-------

Plugins are a modular way to define commands.

.. automodule:: plugins
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

