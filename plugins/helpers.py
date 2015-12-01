import asyncio
import aiohttp
from config import INCUBATOR, INCUBATOR_SECRET, SPACEAPI
from os import path


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
    response = yield from aiohttp.get(url)
    res = yield from response.json()
    yield from response.release()
    return res


@asyncio.coroutine
def spaceapi():
    res = yield from public_api(SPACEAPI)
    return res
