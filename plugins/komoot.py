from collections import Counter

import aiohttp

from config import KOMOOT_CREDENTIALS
from ircbot.plugin import BotPlugin

# See https://static.komoot.de/doc/external-api/v007/index.html#
API_ROOT = "https://www.komoot.com/api/v007"
KOMOOT_URL = r"https?://www.komoot\.(?:fr|de|com)"

# See https://static.komoot.de/doc/external-api/v007/surfaces.html
surface_types = {
    "alpin": "vtt",
    "asphalt": "route",
    "cobbles": "gravel",
    "cobblestone": "gravel",
    "compacted": "gravel",
    "concrete": "route",
    "grass_paver": "gravel",
    "gravel": "gravel",
    "ground": "vtt",
    "nature": "vtt",
    "paved": "route",
    "paving_stones": "gravel",
    "sand": "vtt",
    "stone": "vtt",
    "unpaved": "vtt",
    "wood": "vtt",
}

# See https://static.komoot.de/doc/external-api/v007/waytypes.html
way_types = {
    "alpine_bike_d8": "sentier",
    "alpine_bike_d9": "sentier",
    "alpine_hiking_path": "chemin de montagne",
    "cycle_route": "piste cyclable",
    "cycleway": "piste cyclable",
    "ferry": "ferry",
    "footway": "chemin piéton",
    "hike_d2": "chemin de rando",
    "hike_d3": "chemin de rando",
    "hike_d4": "chemin de rando",
    "hike_d5": "chemin de rando",
    "hike_d6": "chemin de rando",
    "hike_d7": "chemin de rando",
    "hike_d8": "chemin de rando",
    "hike_d9": "chemin de rando",
    "hiking_path": "chemin de rando",
    "long_hiking_path": "chemin de rando",
    "minor_road": "rue",
    "movable_bridge": "pont ouvrant",
    "primary": "route",
    "service": "route",
    "street": "route",
    "track": "piste",
    "trail_d1": "sentier",
    "trail_d2": "sentier",
    "trail_d3": "sentier",
    "trail_d4": "sentier",
    "trail_d5": "sentier",
    "trail_d6": "sentier",
    "trail_d7": "sentier",
    "way": "chemin",
}


def describe_tour_summary(summary):
    """
    Return a text description of the summary of a tour (surfaces, way types)
    """
    texts = []

    for field, mapping in [("surfaces", surface_types), ("way_types", way_types)]:
        aggregated_count = Counter()
        for item in summary[field]:
            key = item["type"].split("#", 1)[1]
            name = mapping.get(key, "???")
            aggregated_count.update({name: item["amount"]})

        texts.append(
            "* "
            + ", ".join(
                f"{name}: {round(100*amount)}%"
                for name, amount in sorted(
                    aggregated_count.items(), key=lambda x: x[1], reverse=True
                )
                if amount >= 0.01
            )
        )

    return "\n".join(texts)


async def komoot_auth(session):
    # 1. Login as Lechbot
    async with session.post(
        "https://account.komoot.com/v1/signin", data=KOMOOT_CREDENTIALS
    ) as response:
        await response.json()
    # 2. Transfer the cookies to the main domain
    await session.get("https://account.komoot.com/actions/transfer?type=signin")


async def komoot_api(path, auth=True):
    async with aiohttp.ClientSession() as session:
        if auth:
            await komoot_auth(session)
        # 3. Actual call
        async with session.get(f"{API_ROOT}{path}") as response:
            return await response.json()


class Komoot(BotPlugin):
    @BotPlugin.command(rf"\!komoot follow {KOMOOT_URL}/user/(\d+)")
    async def follow(self, msg):
        """Ordonne à Lechbot de suivre un utilisateur sur Komoot, lui donnant ainsi accès aux tours visible par les amis de cet utilisateur une fois que l'utilisateur a accepté la demande de suivi à son tour."""
        target_user = msg.args[0]
        async with aiohttp.ClientSession() as session:
            await komoot_auth(session)
            path = f"/users/{KOMOOT_CREDENTIALS['user_id']}/relations/{target_user}"
            async with session.patch(
                f"{API_ROOT}{path}", json={"relation_to_follow": "follow"}
            ) as response:
                await response.json()
        msg.reply("Lechbot suit maintenant cet utilisateur o/")
