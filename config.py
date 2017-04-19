# Bot nickname
NICKNAME = "DechBot"

# Main chan for this bot
MAIN_CHAN = "#titoufaitdestests"

# Url to Incubator
INCUBATOR = "http://localhost:8000/"

# Secret string to perform private API calls to incubator.
# Go to [INCUBATOR]/admin/space/privateapikey/ to obtain one
INCUBATOR_SECRET = "Vairy sicret"

# SpaceAPI url
SPACEAPI = INCUBATOR + "spaceapi.json"

# Full pamela url
FULL_PAMELA = INCUBATOR + "space/private_pamela.json"

# URL of the Crossbar router (websocket endpoint)
WAMP_HOST = "ws://127.0.0.1:8080/ws"

# Crossbar realm to use
WAMP_REALM = "urlab"

# Twitter configuration. Obtain those values from
# https://dev.twitter.com/oauth/overview/application-owner-access-tokens
TWITTER_CONFIG = {
    'consumer_key': 'consumer',
    'consumer_secret': 'secret',
    'oauth_token': 'token',
    'oauth_token_secret': 'token secret'
}

GIPHY_KEY = "secret"

try:
    from local_config import *  # pragma: no flakes # NOQA
except ImportError:
    print("Cannot load local config; using gitted config")
    pass
