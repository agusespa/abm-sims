from .agents import HabitatWall, ExternalWall, PowerWall
from .utils import ZONE_ENVIRONMENT_MAP, ZoneCode


def build_base_from_blueprint(model, grid_data):
    height = len(grid_data)
    width = len(grid_data[0])

    # First pass: create zones - grid_data already contains mapped zone names
    for y in range(height):
        for x in range(width):
            zone_code_str = grid_data[y][x]

            if zone_code_str not in model.zones:
                zone_code_enum = ZoneCode(zone_code_str)
                model.zones[zone_code_str] = {
                    "code": zone_code_enum.value,
                    "bounds": [x, y, x, y],
                    "type": ZONE_ENVIRONMENT_MAP.get(zone_code_enum).value,
                    "positions": [],  # Track valid positions for agent placement
                }
            else:
                current_bounds = model.zones[zone_code_str]["bounds"]
                model.zones[zone_code_str]["bounds"][0] = min(current_bounds[0], x)
                model.zones[zone_code_str]["bounds"][1] = min(current_bounds[1], y)
                model.zones[zone_code_str]["bounds"][2] = max(current_bounds[2], x)
                model.zones[zone_code_str]["bounds"][3] = max(current_bounds[3], y)

            # Only add positions to non-wall zones for agent placement
            if zone_code_str not in ["habitat_wall", "power_wall"]:
                model.zones[zone_code_str]["positions"].append((x, y))

    # After populating all zones, adjust max_x and max_y to be inclusive
    for zone_data in model.zones.values():
        zone_data["bounds"][2] += 1  # max_x becomes exclusive upper bound
        zone_data["bounds"][3] += 1  # max_y becomes exclusive upper bound

    # Second pass: create wall agents
    for y in range(height):
        for x in range(width):
            zone_code = grid_data[y][x]
            wall_agents = _create_wall_agents(zone_code, model)
            for wall_agent in wall_agents:
                model.grid.place_agent(wall_agent, (x, y))


def _create_wall_agents(zone_code, model):
    if zone_code == "habitat_wall":
        return [
            HabitatWall(model, _get_wall_integrity(model)),
            ExternalWall(model, _get_wall_integrity(model)),
        ]
    elif zone_code == "power_wall":
        integrity = _get_wall_integrity(model)
        return [PowerWall(model, integrity)]
    return []


def _get_wall_integrity(model):
    rand = model.random.random()
    if rand < 0.8:  # 80% chance of perfect walls
        return 100.0
    elif rand < 0.9:  # 10% chance of slightly damaged
        return 85.0
    elif rand < 0.95:  # 5% chance of moderately damaged
        return 70.0
    else:  # 5% chance of badly damaged
        return 55.0
