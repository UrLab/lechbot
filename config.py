from ircbot import MockIRCBot
import logging

BOT_CLASS = MockIRCBot
DEBUG = True
LOGLEVEL = logging.INFO

NICKNAME = "DechBot"
CHANS = ['#titoufaitdestests']

INCUBATOR_SECRET = "Vairy sicret"
INCUBATOR = "http://localhost:8000/"
SPACEAPI = INCUBATOR + "spaceapi.json"

RMQ_HOST = "localhost"
RMQ_USER = "guest"
RMQ_PASSWORD = "guest"
LECHBOT_EVENTS_QUEUE = "test.hal.events"
LECHBOT_NOTIFS_QUEUE = "test.hal.notifs"

TWITTER_CONSUMER_KEY = "consumer"
TWITTER_CONSUMER_SECRET = "secret"

try:
    from local_config import *  # pragma: no flakes
except ImportError:
    print("Cannot load local config; using gitted config")
    pass
