import asyncio
from logging import getLogger
from os import path

import aiohttp

from config import FULL_PAMELA, INCUBATOR, INCUBATOR_SECRET, SPACEAPI

logger = getLogger(__name__)
TIMEFMT = "%Y-%m-%d %H:%M:%S"
unsafe_conn = aiohttp.TCPConnector(verify_ssl=False)


class ApiError(Exception):
    def __init__(self, response, code):
        self.response = response
        self.code = code

    @property
    def error(self):
        return self.response.get("error")

    @property
    def error_type(self):
        return self.response.get("type")

    def __repr__(self):
        if self.error_type:
            return "<ApiError(%i type:%s): %s>" % (
                self.code,
                self.error_type,
                self.response,
            )
        else:
            return "<ApiError(%i): %s>" % (self.code, self.response)


def protect(func):
    """Catch and log exceptions that occurs in call to func"""

    async def wrapper(*args, **kwargs):
        try:
            r = func(*args, **kwargs)
            if asyncio.iscoroutine(r):
                r = await r
            return r
        except:
            logger.exception("Error in {}".format(func.__name__))

    return wrapper


def mkurl(endpoint, host=INCUBATOR):
    if endpoint.startswith("http"):
        return endpoint
    url = str(host)
    if url[-1] != "/":
        url += "/"
    return url + endpoint.lstrip("/")


async def private_api(endpoint, data):
    """Call UrLab incubator private API"""
    data["secret"] = INCUBATOR_SECRET
    response = await aiohttp.post(mkurl(endpoint), data=data)
    res = await response.json()
    status_code = response.status
    await response.release()
    if status_code != 200:
        raise ApiError(response=res, code=status_code)
    return res


async def public_api(endpoint, verify_ssl=True):
    """Call UrLab incubator public API"""
    if not endpoint.startswith("http"):
        if endpoint[-1] != "/":
            endpoint += "/"
        url = mkurl(path.join("api", endpoint.lstrip("/")))
    else:
        url = endpoint
    args = {"headers": {"User-agent": "UrLab [LechBot]"}}
    if not verify_ssl:
        args["connector"] = unsafe_conn
        logger.warning("Using unverified SSL for " + url)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, **args) as response:
            return await response.json()


@asyncio.coroutine
def spaceapi():
    return public_api(SPACEAPI)


@asyncio.coroutine
def full_pamela():
    return private_api(FULL_PAMELA, {})
