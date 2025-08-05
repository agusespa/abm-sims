from .agents import (
    Robot,
    ComplexStructure,
    BioLabRobot,
    MaintenanceRobot,
    ConstructionRobot,
    EVASpecialistRobot,
    LogisticsRobot,
    Human,
    CentralCommunicationsSystem,
    PowerDistributionHub,
    BatteryPack,
    HazardousMaterialsStorage,
    HabitatWall,
    ExternalWall,
    PowerWall,
)
from .utils import ZONE_ENVIRONMENT_MAP, ZoneCode, ROBOT_OPERATIONAL_ZONES


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


def setup_mars_base(model, grid_data, equipment_positions, config_params):
    """Main function to set up the entire Mars base including zones, walls, equipment, humans, and robots"""
    build_base_from_blueprint(model, grid_data)
    _create_equipment_agents(model, equipment_positions)
    _create_human_agents(model, config_params)
    _create_robot_agents(model, config_params)


def _create_equipment_agents(model, equipment_positions):
    """Create and place equipment agents based on equipment positions"""
    equipment_classes = {
        "CentralCommunicationsSystem": CentralCommunicationsSystem,
        "PowerDistributionHub": PowerDistributionHub,
        "BatteryPack": BatteryPack,
        "HazardousMaterialsStorage": HazardousMaterialsStorage,
    }

    for equipment_data in equipment_positions:
        equipment_type = equipment_data["type"]
        equipment_class = equipment_classes.get(equipment_type)

        if equipment_class:
            initial_integrity = equipment_data["integrity"]
            if equipment_type == "BatteryPack" and model.random.random() < 0.2:
                initial_integrity = 29

            equipment = equipment_class(
                model,
                integrity=initial_integrity,
            )
            model.grid.place_agent(
                equipment, (equipment_data["x"], equipment_data["y"])
            )
            model.schedule.add(equipment)


def _create_human_agents(model, config_params):
    """Create and place human agents"""
    crew_size = config_params.get("CREW_SIZE")
    injured_count = int(crew_size * 0.7)

    health_configs = [
        (injured_count, 85),
        (crew_size - injured_count, 65),
    ]

    for count, health in health_configs:
        for _ in range(count):
            human = Human(model, health)
            position = _get_random_human_position(model)
            model.grid.place_agent(human, position)
            human.pos = position
            model.schedule.add(human)


def _create_robot_agents(model, config_params):
    """Create and place robot agents"""
    robot_classes = {
        "BioLabRobot": BioLabRobot,
        "MaintenanceRobot": MaintenanceRobot,
        "ConstructionRobot": ConstructionRobot,
        "EVASpecialistRobot": EVASpecialistRobot,
        "LogisticsRobot": LogisticsRobot,
    }
    
    robot_counts = config_params["ROBOT_COUNTS"]
    for robot_type, count in robot_counts.items():
        robot_class = robot_classes.get(robot_type)
        if not robot_class:
            raise ValueError(f"Unknown robot type: {robot_type}")
        
        for i in range(count):
            robot = robot_class(model)
            position = _get_realistic_robot_position(model, robot_type, i)
            model.grid.place_agent(robot, position)
            model.schedule.add(robot)


def _get_realistic_robot_position(model, robot_type, robot_index):
    """Get a realistic starting position for a robot based on its type"""
    available_zones = ROBOT_OPERATIONAL_ZONES[robot_type]
    if not available_zones:
        raise ValueError(f"No operational zones found for robot type '{robot_type}'")

    # Filter to only zones that actually exist in the model
    existing_zones = [zone for zone in available_zones if zone in model.zones and model.zones[zone]["positions"]]
    
    if not existing_zones:
        # Fallback to any available zone with positions
        existing_zones = [zone for zone in model.zones.keys() if model.zones[zone]["positions"]]
        if not existing_zones:
            raise ValueError(f"No valid zones available for robot placement")

    # Distribute robots evenly across available zones
    chosen_zone_code = existing_zones[robot_index % len(existing_zones)]
    
    return _find_valid_position_in_zone(model, chosen_zone_code)


def _get_random_human_position(model):
    """Get a random position for human placement in preferred zones"""
    preferred_zones = [ZoneCode.LAB.value, ZoneCode.HABITAT.value]
    available_preferred_zones = [
        zone for zone in preferred_zones if zone in model.zones
    ]
    if not available_preferred_zones:
        raise ValueError("No preferred zones available for human placement")
    chosen_zone = model.random.choice(available_preferred_zones)
    return _get_equipment_position(model, chosen_zone)


def _get_equipment_position(model, zone_code):
    """Get a valid position within a specified zone"""
    if zone_code in model.zones:
        available_positions = model.zones[zone_code]["positions"]
        if not available_positions:
            raise ValueError(f"No valid positions available in zone '{zone_code}'")
        return model.random.choice(available_positions)
    raise ValueError(f"Zone with code '{zone_code}' not found.")


def _find_valid_position_in_zone(model, zone_code):
    """Find a valid position within a specified zone"""
    if zone_code not in model.zones:
        raise ValueError(f"Zone with code '{zone_code}' not found")

    available_positions = model.zones[zone_code]["positions"]
    if not available_positions:
        raise ValueError(f"No valid positions available in zone '{zone_code}'")

    return model.random.choice(available_positions)


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
