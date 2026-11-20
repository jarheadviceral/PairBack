"""Campus locations supplied by the project team.

Intermediate floors suggest rooms 01–15; final floors stop at the supplied
endpoint. These are suggestions, not a verified inventory of existing rooms.
"""

ROOM_LIMITS = {
    "MVP": 415, "SOM": 402, "CTC": 410, "SEC A": 215,
    "SEC B": 215, "SEC C": 215, "G": 312, "B": 310,
    "Bel": 313, "F": 327, "FA Annex": 211,
}


def room_choices(last_room):
    final_floor, final_number = divmod(last_room, 100)
    return [
        str(floor * 100 + number)
        for floor in range(1, final_floor + 1)
        for number in range(1, (final_number if floor == final_floor else 15) + 1)
    ]


LOCATIONS = {building: room_choices(limit) for building, limit in ROOM_LIMITS.items()}
LOCATIONS["MVP"].append("Roofdeck")
LOCATIONS["SEC A"].append("Escaler Hall")
LOCATIONS["Gonzaga Cafeteria"] = ["GONZ 1", "GONZ 2"]
LOCATIONS["New Rizal Library"] = [f"Floor {floor}" for floor in range(1, 6)]
LOCATIONS["Old Rizal Library"] = ["Floor 1", "Floor 2"]
for name in [
    "Leong Hall Auditorium", "Red Brick Road", "SEC Walk",
    "Eliazo Dormitory", "Cervini Dormitory", "IRH",
    "College Covered Courts", "JSEC", "Arete", "North Carpark",
    "Central Carpark", "Upper East Carpark", "Lower East Carpark",
]:
    LOCATIONS[name] = []


def compose_location(building, room=""):
    building, room = str(building).strip(), str(room).strip()
    if building not in LOCATIONS:
        raise ValueError("Choose a listed building or campus location.")
    if len(room) > 80:
        raise ValueError("Room or area must be at most 80 characters.")
    return f"{building} · {room}" if room else building


def location_key(location):
    """Compare known buildings; preserve exact matching for legacy locations."""
    value = str(location).strip().casefold()
    # Require separators and known rooms when parsing legacy locations.
    for building in LOCATIONS:
        key = building.casefold()
        if value == key or value.startswith(key + " · "):
            return key
        if value.startswith(key + " "):
            suffix = value[len(key) + 1:]
            if suffix in [room.casefold() for room in LOCATIONS[building]]:
                return key
    return value
