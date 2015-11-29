DEBUG = True

NICKNAME = "DechBot" if DEBUG else "Lechbot"
CHANS = ['#titoufaitdestests'] if DEBUG else ['#urlab']

INCUBATOR_SECRET = "Vairy sicret"
STATUS_CHANGE_URL = "http://localhost:8000/space/change_status"
SPACEAPI = "http://localhost:8000/spaceapi.json"

try:
    from local_config import *  # pragma: no flakes
except ImportError:
    print("Cannot load local config; using gitted config")
    pass
