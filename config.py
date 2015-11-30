from ircbot import MockIRCBot
import logging

BOT_CLASS = MockIRCBot
DEBUG = True
LOGLEVEL = logging.INFO

NICKNAME = "DechBot" if DEBUG else "Lechbot"
CHANS = ['#titoufaitdestests'] if DEBUG else ['#urlab']

INCUBATOR_SECRET = "Vairy sicret"
INCUBATOR = "http://localhost:8000/"
SPACEAPI = "http://localhost:8000/spaceapi.json"

try:
    from local_config import *  # pragma: no flakes
except ImportError:
    print("Cannot load local config; using gitted config")
    pass
