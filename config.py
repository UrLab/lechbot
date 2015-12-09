DEBUG = True

NICKNAME = "DechBot"
CHANS = ['#titoufaitdestests']

INCUBATOR_SECRET = "Vairy sicret"
INCUBATOR = "http://localhost:8000/"
SPACEAPI = INCUBATOR + "spaceapi.json"

WAMP_HOST = "ws://127.0.0.1:8080/ws"
WAMP_REALM = "urlab"

TWITTER_CONSUMER_KEY = "consumer"
TWITTER_CONSUMER_SECRET = "secret"
TWITTER_OAUTH_TOKEN = "token"
TWITTER_OAUTH_SECRET = "token-secret"

try:
    from local_config import *  # pragma: no flakes
except ImportError:
    print("Cannot load local config; using gitted config")
    pass
