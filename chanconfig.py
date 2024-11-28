from config import GIPHY_KEY, TWITTER_CONFIG
from ircbot.plugin import HelpPlugin
from plugins import (
    Ascii,
    Giphy,
    Komoot,
    LesRepublicains,
    Poll,
    React,
    Reminder,
    Space,
    TechWednesday,
    Topic,
    Trump,
    Twitter,
    UrlShow,
)

CHANS = {
    "#urlab": [
        Ascii(),
        Topic(),
        Space(),
        React(),
        TechWednesday(),
        Reminder(),
        Twitter(TWITTER_CONFIG),
        UrlShow(TWITTER_CONFIG),
        Giphy(GIPHY_KEY),
        Komoot(),
        HelpPlugin(),
        Poll(),
        LesRepublicains(),
        Trump(),
    ],
    "#titoufaitdestests": [
        Ascii(),
        Topic(),
        Space(),
        React(),
        TechWednesday(),
        Reminder(),
        Twitter(TWITTER_CONFIG),
        UrlShow(TWITTER_CONFIG),
        Giphy(GIPHY_KEY),
        Komoot(),
        HelpPlugin(),
        Poll(),
        LesRepublicains(),
        Trump(),
    ],
    "QUERY": [
        TechWednesday(),
        HelpPlugin(),
        Trump(),
    ],
}

# Rate limit for incoming UrLab notifications in seconds
RATELIMIT = {
    # Hal events
    "bell": 120,
    "passage": 3600,
    "kitchen_move": 3600,
    "doors_stairs": 900,
    # Incubator activity stream
    "Event.a créé": 900,
    "Event.a édité": 900,
    "Project.a créé": 900,
    "Project.a édité": 900,
    "Project.participe à": 900,
    "Task.a ajouté la tâche": 3600,
    "Task.a fini la tâche": 3600,
    "Task.a ré-ajouté la tâche": 3600,
    "wiki.revision": 300,
}

try:
    from local_chanconfig import CHANS, RATELIMIT
except ImportError:
    print("Cannot load local chan config; using gitted config")
    pass
