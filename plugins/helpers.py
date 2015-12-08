import asyncio
import aiohttp
import aioamqp
import json
from os import path
from datetime import datetime
from logging import getLogger
from aioauth_client import TwitterClient
from config import (INCUBATOR, INCUBATOR_SECRET, SPACEAPI,
                    RMQ_HOST, RMQ_USER, RMQ_PASSWORD,
                    LECHBOT_EVENTS_QUEUE, LECHBOT_NOTIFS_QUEUE,
                    TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
                    TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_SECRET)

logger = getLogger(__name__)
TIMEFMT = "%Y-%m-%d %H:%M:%S"


def protect(func):
    def wrapper(*args, **kwargs):
        try:
            r = func(*args, **kwargs)
            if asyncio.iscoroutine(r):
                r = yield from r
            return r
        except:
            logger.exception("Error in {}".format(func.__name__))
    return wrapper


def mkurl(endpoint, host=INCUBATOR):
    url = str(host)
    if url[-1] != '/':
        url += '/'
    return url + endpoint.lstrip('/')


@asyncio.coroutine
def private_api(endpoint, data):
    """Call UrLab incubator private API"""
    data['secret'] = INCUBATOR_SECRET
    response = yield from aiohttp.post(mkurl(endpoint), data=data)
    status_code = response.status
    yield from response.release()
    assert status_code == 200


@asyncio.coroutine
def public_api(endpoint):
    """Call UrLab incubator public API"""
    if not endpoint.startswith('http'):
        if endpoint[-1] != '/':
            endpoint += '/'
        url = mkurl(path.join('api', endpoint.lstrip('/')))
    else:
        url = endpoint
    headers = {'User-agent': "UrLab [LechBot]"}
    response = yield from aiohttp.get(url, headers=headers)
    res = yield from response.json()
    yield from response.release()
    return res


@asyncio.coroutine
def spaceapi():
    return public_api(SPACEAPI)


@asyncio.coroutine
def rmq_error_callback(exc):
    logger.error("Error when connecting to RabbitMQ: " + str(exc))


@asyncio.coroutine
@protect
def lechbot_event_consume(coroutine):
    transport, protocol = yield from aioamqp.connect(
        host=RMQ_HOST, login=RMQ_USER, password=RMQ_PASSWORD,
        on_error=rmq_error_callback)
    channel = yield from protocol.channel()
    queue = yield from channel.queue_declare(LECHBOT_EVENTS_QUEUE)

    @asyncio.coroutine
    @protect
    def consume(body, envelope, properties):
        yield from channel.basic_client_ack(envelope.delivery_tag)
        msg = json.loads(body.decode())
        now = datetime.now()
        msgtime = datetime
        msgtime = parse_date(msg['time'])
        if (now - msgtime).total_seconds() < 120:
            yield from coroutine(msg['name'])

    yield from channel.basic_consume(LECHBOT_EVENTS_QUEUE, callback=consume)


@asyncio.coroutine
@protect
def lechbot_notif(notif_name):
    transport, protocol = yield from aioamqp.connect(
        host=RMQ_HOST, login=RMQ_USER, password=RMQ_PASSWORD,
        on_error=rmq_error_callback)
    channel = yield from protocol.channel()
    yield from channel.queue_declare(LECHBOT_NOTIFS_QUEUE)
    msg = {'time': datetime.now().strftime(TIMEFMT), 'name': notif_name}
    yield from channel.publish(json.dumps(msg), '', LECHBOT_NOTIFS_QUEUE)
    yield from protocol.close()
    transport.close()


class AsyncTwitter:
    def __init__(self):
        self.client = TwitterClient(
            consumer_key=TWITTER_CONSUMER_KEY,
            consumer_secret=TWITTER_CONSUMER_SECRET,
            oauth_token=TWITTER_OAUTH_TOKEN,
            oauth_token_secret=TWITTER_OAUTH_SECRET)

    def request(self, *args, **kwargs):
        response = yield from self.client.request(*args, **kwargs)
        res = yield from response.json()
        yield from response.release()
        return res

twitter = AsyncTwitter()
