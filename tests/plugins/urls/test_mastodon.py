import re

import pytest

from ircbot import BotPlugin
from plugins import UrlShow
from tests.pytestbot import PytestBot

URLS = [
    "https://mamot.fr/@LukaszOlejnik@mastodon.social/109581465546995503",
    "https://mamot.fr/@LaQuadrature/109602337358898925",
    "https://mastodon.social/@MarkRuffalo/109638532333776039",
    "https://mastodon.social/@MarkRuffalo@mastodon.social/109638532333776039",
]


class OnlyMastodonPlugin(BotPlugin):
    mastodon_toot = UrlShow.mastodon_toot


@pytest.mark.parametrize("url", URLS)
def test_mastodon_toot_match(url):
    assert re.match(
        OnlyMastodonPlugin().mastodon_toot._botplugin_special_tag_pattern, url
    )


@pytest.mark.parametrize(
    "url", ["https://twitter.com/jenniesrenes/status/1609913017654824962"]
)
def test_mastodon_toot_no_match(url):
    assert not re.match(
        OnlyMastodonPlugin().mastodon_toot._botplugin_special_tag_pattern, url
    )


@pytest.mark.network
@pytest.mark.asyncio
@pytest.mark.parametrize("url", URLS)
async def test_mastodon_toot_match(url):
    bot = PytestBot(OnlyMastodonPlugin())
    await bot.feed(text=url)
    assert len(bot.output) == 1
