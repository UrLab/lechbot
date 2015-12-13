from ircbot.persist import Persistent
from time import time
from datetime import datetime
from .helpers import private_api
from ircbot.plugin import BotPlugin


class Topic(BotPlugin):
    def make_topic(self, msg, new_topic=None, new_music=None):
        template = {'last_changed': None, 'text': "", 'changed_by': None}
        with Persistent('topic.json') as current_topic:
            for key, newval in [('motd', new_music), ('topic', new_topic)]:
                oldval = current_topic.setdefault(key, dict(template))
                if newval is not None:
                    oldval['last_changed'] = time()
                    oldval['changed_by'] = msg.user.nick
                    oldval['text'] = newval
            topic_string = ' :: '.join(
                current_topic[x]['text'] for x in ('motd', 'topic'))
            self.bot.set_topic(topic_string, msg.chan)

    @BotPlugin.command(r'\!motd +(https?://[^ ]+)')
    def music_of_the_day(self, msg):
        """Change la musique du jour"""
        now = datetime.now()
        with Persistent('topic.json') as current_topic:
            last = datetime.fromtimestamp(current_topic.get('motd', {})\
                                                       .get('last_changed', 0))
        if last.date() == now.date():
            msg.reply("La musique du jour a déjà été changée aujourd'hui",
                      hilight=True)
            return
        try:
            yield from private_api('/space/change_motd', {
                'nick': msg.user.nick,
                'url': msg.args[0]
            })
            self.bot.log.info("Music of the day changed by " + msg.user.nick)
            self.make_topic(msg, new_music=msg.args[0])
            msg.reply("tu viens de changer la musique du jour >>> d*-*b <<<",
                      hilight=True)
        except:
            msg.reply("Impossible de changer la musique du jour !")

    @BotPlugin.command(r'\!topic prepend +([^ ].+)')
    def prepend_topic(self, msg):
        """Insère une nouvelle annonce à l'avant du topic"""
        with Persistent('topic.json') as current_topic:
            topic = current_topic.get('topic', {}).get('text', '')
        self.make_topic(msg, new_topic=msg.args[0] + ' :: ' + topic)
        self.bot.log.info("Topic changed by " + msg.user.nick)

    @BotPlugin.command(r'\!topic +([^ ].+)')
    def topic(self, msg):
        """Change l'annonce du chat"""
        self.make_topic(msg, new_topic=msg.args[0])
        self.bot.log.info("Topic changed by " + msg.user.nick)

    @BotPlugin.command(r'\!(topic|motd)')
    def tell_topic(self, msg):
        """Qui a changé le topic/MotD, et quand ?"""
        key = msg.args[0]
        with Persistent('topic.json') as topic:
            if key not in topic or topic[key]['last_changed'] is None:
                msg.reply(key + " n'a pas encore été changé")
            else:
                when = self.bot.naturaltime(topic[key]['last_changed'])
                msg.reply("Changé " + when + " par " + topic[key]['changed_by'])
