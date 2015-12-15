import asyncio
import aiohttp
from os import path
from logging import getLogger
from config import INCUBATOR, INCUBATOR_SECRET, SPACEAPI

logger = getLogger(__name__)
TIMEFMT = "%Y-%m-%d %H:%M:%S"
unsafe_conn = aiohttp.TCPConnector(verify_ssl=False)


def protect(func):
    """Catch and log exceptions that occurs in call to func"""
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
def public_api(endpoint, verify_ssl=True):
    """Call UrLab incubator public API"""
    if not endpoint.startswith('http'):
        if endpoint[-1] != '/':
            endpoint += '/'
        url = mkurl(path.join('api', endpoint.lstrip('/')))
    else:
        url = endpoint
    args = {'headers': {'User-agent': "UrLab [LechBot]"}}
    if not verify_ssl:
        args['connector'] = unsafe_conn
        logger.warning("Using unverified SSL for " + url)
    response = yield from aiohttp.get(url, **args)
    res = yield from response.json()
    yield from response.release()
    return res


@asyncio.coroutine
def spaceapi():
    return public_api(SPACEAPI)
