from collections import Counter

from .helpers import public_api

# See https://static.komoot.de/doc/external-api/v007/index.html#
API_ROOT = "https://external-api.komoot.de/v007"


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


def komoot_api(api_path):
    return public_api(f"{API_ROOT}{api_path}")
