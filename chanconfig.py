from plugins import UrlShow, Twitter, Topic, Space, Reminder, TechWednesday, TwitterStream
from ircbot.plugin import HelpPlugin
from config import TWITTER_CONFIG


CHANS = {
    '#titoufaitdestests': [
        Topic(),
        Space(),
        TechWednesday(),
        Reminder(),
        Twitter(TWITTER_CONFIG),
        UrlShow(TWITTER_CONFIG),
        TwitterStream(TWITTER_CONFIG, 'TitouOnRails'),
        HelpPlugin(),
    ],
    'QUERY': [
        TechWednesday(),
        HelpPlugin(),
    ],
}

try:
    from local_chanconfig import CHANS
except ImportError:
    pass
