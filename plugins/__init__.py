import plugins.topic as topic
import plugins.twitter as twitter
import plugins.techwednesday as techwednesday
import plugins.space as space


plugins = [topic, twitter, techwednesday, space]


def load_all_plugins(bot):
    for p in plugins:
        p.load(bot)
