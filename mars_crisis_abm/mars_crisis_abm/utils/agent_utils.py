from .constants import STABILITY_THRESHOLDS, BASE_DETERIORATION_RATE
from .enums import OperatingEnvironment


def spread_fire(agent):
    neighbors = agent.model.grid.get_neighbors(agent.pos, moore=True, radius=3)
    for neighbor in neighbors:
        if hasattr(neighbor, "fire_intensity") and neighbor.fire_intensity == 0:
            neighbor.integrity = min(
                neighbor.integrity, STABILITY_THRESHOLDS["structure"] - 1
            )
            neighbor.fire_intensity = 10


def spread_damage(agent, radius=1):
    neighbors = agent.model.grid.get_neighbors(agent.pos, moore=True, radius=radius)

    for neighbor in neighbors:
        if hasattr(neighbor, "integrity"):
            neighbor.integrity -= BASE_DETERIORATION_RATE


def get_zones_by_type(zones, operating_environment):
    accessible_zones = set()
    for zone_data in zones.values():
        zone_type = zone_data["type"]
        zone_code = zone_data["code"]

        if operating_environment == OperatingEnvironment.MIXED:
            accessible_zones.add(zone_code)
        elif operating_environment == OperatingEnvironment.INTERNAL:
            if (
                zone_type == OperatingEnvironment.INTERNAL.value
                or zone_type == OperatingEnvironment.MIXED.value
            ):
                accessible_zones.add(zone_code)
        elif operating_environment == OperatingEnvironment.EXTERNAL:
            if (
                zone_type == OperatingEnvironment.EXTERNAL.value
                or zone_type == OperatingEnvironment.MIXED.value
            ):
                accessible_zones.add(zone_code)
    return list(accessible_zones)
