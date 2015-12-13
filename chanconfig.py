from plugins import UrlShow, Twitter, Topic, Space, Reminder, TechWednesday
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
