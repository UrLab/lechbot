import re
from datetime import datetime
from time import time

from yt_dlp import YoutubeDL

from ircbot.persist import Persistent
from ircbot.plugin import BotPlugin

from .helpers import ApiError, private_api

# Thank you http://stackoverflow.com/users/1622925/bruno-de-lima for the Regex
# http://stackoverflow.com/a/31711517 and https://regex101.com/r/pO4dS6/5#python
youtube_matcher = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([-_\w]+)",
    re.IGNORECASE,
)


class Topic(BotPlugin):
    def make_topic(self, msg, new_topic=None, new_music=None):
        template = {"last_changed": None, "text": "", "changed_by": None}
        with Persistent("topic.json") as current_topic:
            for key, newval in [("motd", new_music), ("topic", new_topic)]:
                oldval = current_topic.setdefault(key, dict(template))
                if newval is not None:
                    oldval["last_changed"] = time()
                    oldval["changed_by"] = msg.user
                    oldval["text"] = newval
            topic_string = " :: ".join(
                current_topic[x]["text"] for x in ("motd", "topic")
            )
            self.bot.set_topic(topic_string, msg.chan)

    def find_title(self, url):
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
        return video_title

    @BotPlugin.command(r"\!motd +(https?://[^ ]+)")
    async def music_of_the_day(self, msg):
        """Change la musique du jour"""
        now = datetime.now()
        with Persistent("topic.json") as current_topic:
            last = datetime.fromtimestamp(
                current_topic.get("motd", {}).get("last_changed", 0)
            )
        if last.date() == now.date():
            msg.reply("La musique du jour a déjà été changée aujourd'hui", hilight=True)
            return

        music_url = msg.args[0]
        match = re.match(youtube_matcher, music_url)
        if match:
            video_id = match.group(1)
            music_url = "http://youtu.be/%s" % video_id

        try:
            await private_api(
                "/space/change_motd", {"nick": msg.user, "url": music_url}
            )
        except ApiError as e:
            if e.error_type == "TRY_AGAIN_TOMORROW":
                msg.reply("La musique du jour a déjà été changée aujourd'hui !")

        self.bot.log.info("Music of the day changed by " + msg.user)
        self.make_topic(msg, new_music=music_url)
        try:
            title = self.find_title(music_url)
        except:
            self.bot.log.exception("Fetch MotD title")
            title = ""
        fmt = "tu viens de changer la musique du jour >>> d*-*b <<< {}"
        msg.reply(fmt.format(self.bot.text.bold(title)), hilight=True)

    @BotPlugin.command(r"\!topic prepend +([^ ].+)")
    async def prepend_topic(self, msg):
        """Insère une nouvelle annonce à l'avant du topic"""
        with Persistent("topic.json") as current_topic:
            topic = current_topic.get("topic", {}).get("text", "")
        self.make_topic(msg, new_topic=msg.args[0] + " :: " + topic)
        self.bot.log.info("Topic changed by " + msg.user)

    @BotPlugin.command(r"\!topic +([^ ].+)")
    def topic(self, msg):
        """Change l'annonce du chat"""
        self.make_topic(msg, new_topic=msg.args[0])
        self.bot.log.info("Topic changed by " + msg.user)

    @BotPlugin.command(r"\!(topic|motd)")
    def tell_topic(self, msg):
        """Qui a changé le topic/MotD, et quand ?"""
        key = msg.args[0]
        with Persistent("topic.json") as topic:
            if key not in topic or topic[key]["last_changed"] is None:
                msg.reply(key + " n'a pas encore été changé")
            else:
                when = self.bot.naturaltime(topic[key]["last_changed"])
                msg.reply("Changé " + when + " par " + topic[key]["changed_by"])
