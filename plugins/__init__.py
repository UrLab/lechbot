import plugins.topic as topic
import plugins.twitter as twitter
import plugins.techwednesday as techwednesday
import plugins.space as space
import plugins.urls as urls
import plugins.reminder as reminder


plugins = [topic, twitter, techwednesday, space, urls, reminder]


def load_all_plugins(bot):
    for p in plugins:
        p.load(bot)
