import pytest
from unittest.mock import MagicMock, patch
import mesa
from mars_crisis_abm.blueprint import (
    build_base_from_blueprint,
    setup_mars_base,
    _create_wall_agents,
    _create_equipment_agents,
    _create_human_agents,
    _create_robot_agents,
    _get_realistic_robot_position,
    _get_random_human_position,
    _get_equipment_position,
    _find_valid_position_in_zone,
    _get_wall_integrity,
)
from mars_crisis_abm.agents import (
    HabitatWall,
    ExternalWall,
    PowerWall,
    Human,
    CentralCommunicationsSystem,
    PowerDistributionHub,
    BatteryPack,
    HazardousMaterialsStorage,
    BioLabRobot,
    MaintenanceRobot,
    ConstructionRobot,
    EVASpecialistRobot,
    LogisticsRobot,
)
from mars_crisis_abm.utils import OperatingEnvironment


@pytest.fixture
def mocked_model():
    model = MagicMock()
    model.zones = {}
    model.schedule = mesa.time.RandomActivation(model)
    model.grid = mesa.space.MultiGrid(10, 10, False)
    model.random = mesa.Model().random  # Use real random for realistic testing
    return model


@pytest.mark.parametrize(
    "random_value, expected_integrity",
    [
        (0.7, 100.0),  # 80% chance of perfect walls
        (0.85, 85.0),  # 10% chance of slightly damaged
        (0.92, 70.0),  # 5% chance of moderately damaged
        (0.97, 55.0),  # 5% chance of badly damaged
    ],
)
def test_get_wall_integrity(random_value, expected_integrity):
    model = MagicMock()
    model.random.random.return_value = random_value
    assert _get_wall_integrity(model) == expected_integrity


@pytest.mark.parametrize(
    "zone_code, expected_agents",
    [
        ("habitat_wall", [HabitatWall, ExternalWall]),
        ("power_wall", [PowerWall]),
        ("some_other_zone", []),
    ],
)
def test_create_wall_agents(zone_code, expected_agents):
    model = MagicMock()
    with patch("mars_crisis_abm.blueprint._get_wall_integrity", return_value=100.0):
        agents = _create_wall_agents(zone_code, model)
        assert len(agents) == len(expected_agents)
        for agent, expected_agent_type in zip(agents, expected_agents):
            assert isinstance(agent, expected_agent_type)
            assert agent.integrity == 100.0


def test_build_base_from_blueprint(mocked_model):
    grid_data = [
        ["habitat_wall", "habitat_wall", "habitat_wall"],
        ["habitat_wall", "habitat", "habitat_wall"],
        ["habitat_wall", "power_wall", "habitat_wall"],
    ]

    with patch("mars_crisis_abm.blueprint._get_wall_integrity", return_value=100.0):
        build_base_from_blueprint(mocked_model, grid_data)

    # Verify zones were created correctly
    assert "habitat_wall" in mocked_model.zones
    assert "habitat" in mocked_model.zones
    assert "power_wall" in mocked_model.zones

    # Verify zone bounds and properties
    assert mocked_model.zones["habitat"]["bounds"] == [1, 1, 2, 2]
    assert mocked_model.zones["habitat"]["type"] == OperatingEnvironment.INTERNAL.value
    assert mocked_model.zones["habitat"]["positions"] == [(1, 1)]

    # Verify walls were actually placed on the grid
    habitat_wall_positions = [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]
    power_wall_position = (1, 2)

    for pos in habitat_wall_positions:
        agents_at_pos = mocked_model.grid.get_cell_list_contents(pos)
        assert len(agents_at_pos) == 2  # HabitatWall + ExternalWall
        assert any(isinstance(agent, HabitatWall) for agent in agents_at_pos)
        assert any(isinstance(agent, ExternalWall) for agent in agents_at_pos)

    agents_at_power_wall = mocked_model.grid.get_cell_list_contents(power_wall_position)
    assert len(agents_at_power_wall) == 1
    assert isinstance(agents_at_power_wall[0], PowerWall)


def test_build_base_from_blueprint_multiple_zones(mocked_model):
    grid_data = [
        ["habitat", "corridor", "lab"],
        ["habitat", "corridor", "lab"],
    ]
    build_base_from_blueprint(mocked_model, grid_data)

    # Verify zone bounds are calculated correctly
    assert mocked_model.zones["habitat"]["bounds"] == [0, 0, 1, 2]
    assert mocked_model.zones["corridor"]["bounds"] == [1, 0, 2, 2]
    assert mocked_model.zones["lab"]["bounds"] == [2, 0, 3, 2]

    # Verify positions are tracked correctly for agent placement
    assert len(mocked_model.zones["habitat"]["positions"]) == 2
    assert len(mocked_model.zones["corridor"]["positions"]) == 2
    assert len(mocked_model.zones["lab"]["positions"]) == 2

    # Verify specific positions
    assert (0, 0) in mocked_model.zones["habitat"]["positions"]
    assert (0, 1) in mocked_model.zones["habitat"]["positions"]
    assert (1, 0) in mocked_model.zones["corridor"]["positions"]
    assert (1, 1) in mocked_model.zones["corridor"]["positions"]


def test_build_base_from_blueprint_no_walls(mocked_model):
    grid_data = [
        ["habitat", "habitat"],
        ["habitat", "habitat"],
    ]
    build_base_from_blueprint(mocked_model, grid_data)

    # Verify no agents were placed (no walls)
    for x in range(2):
        for y in range(2):
            agents_at_pos = mocked_model.grid.get_cell_list_contents((x, y))
            assert len(agents_at_pos) == 0


def test_setup_mars_base_integration(mocked_model):
    grid_data = [
        ["habitat_wall", "habitat", "lab"],
        ["corridor", "corridor", "corridor"],
        ["medical_bay", "control_module", "power_distribution"],
    ]
    equipment_positions = [
        {"type": "CentralCommunicationsSystem", "x": 1, "y": 1, "integrity": 25},
        {"type": "PowerDistributionHub", "x": 2, "y": 2, "integrity": 100},
        {"type": "BatteryPack", "x": 1, "y": 2, "integrity": 80},
    ]
    config_params = {
        "CREW_SIZE": 3,
        "ROBOT_COUNTS": {"MaintenanceRobot": 2, "BioLabRobot": 1},
    }

    with patch("mars_crisis_abm.blueprint._get_wall_integrity", return_value=100.0):
        setup_mars_base(mocked_model, grid_data, equipment_positions, config_params)

    # Verify zones were created
    expected_zones = [
        "habitat_wall",
        "habitat",
        "lab",
        "corridor",
        "medical_bay",
        "control_module",
        "power_distribution",
    ]
    for zone in expected_zones:
        assert zone in mocked_model.zones

    # Count agents by type (walls are on grid, others are scheduled)
    scheduled_agents = list(mocked_model.schedule.agents)
    humans = [agent for agent in scheduled_agents if isinstance(agent, Human)]
    robots = [
        agent
        for agent in scheduled_agents
        if isinstance(agent, (BioLabRobot, MaintenanceRobot))
    ]
    equipment = [
        agent
        for agent in scheduled_agents
        if isinstance(
            agent, (CentralCommunicationsSystem, PowerDistributionHub, BatteryPack)
        )
    ]

    # Count walls from grid (they're placed but not scheduled)
    wall_count = 0
    for x in range(mocked_model.grid.width):
        for y in range(mocked_model.grid.height):
            cell_agents = mocked_model.grid.get_cell_list_contents((x, y))
            wall_count += len(
                [
                    agent
                    for agent in cell_agents
                    if isinstance(agent, (HabitatWall, ExternalWall, PowerWall))
                ]
            )

    # Verify correct number of each agent type
    assert len(humans) == 3
    assert len(robots) == 3  # 2 maintenance + 1 biolab
    assert len(equipment) == 3
    assert wall_count == 2  # 1 habitat_wall position creates 2 wall agents

    # Verify agents are placed in appropriate zones
    for human in humans:
        human_pos = human.pos
        # Humans should be in habitat or lab zones
        assert (
            human_pos in mocked_model.zones["habitat"]["positions"]
            or human_pos in mocked_model.zones["lab"]["positions"]
        )

    # Verify equipment is placed at specified positions
    comm_system = [
        agent for agent in equipment if isinstance(agent, CentralCommunicationsSystem)
    ][0]
    power_hub = [
        agent for agent in equipment if isinstance(agent, PowerDistributionHub)
    ][0]
    battery = [agent for agent in equipment if isinstance(agent, BatteryPack)][0]

    assert comm_system.pos == (1, 1)
    assert power_hub.pos == (2, 2)
    assert battery.pos == (1, 2)


def test_create_equipment_agents_real_placement(mocked_model):
    equipment_positions = [
        {"type": "CentralCommunicationsSystem", "x": 0, "y": 0, "integrity": 25},
        {"type": "PowerDistributionHub", "x": 1, "y": 1, "integrity": 100},
        {"type": "BatteryPack", "x": 2, "y": 2, "integrity": 100},
        {"type": "HazardousMaterialsStorage", "x": 3, "y": 3, "integrity": 90},
    ]

    # Test battery damage logic - set random to trigger damage
    mocked_model.random.random = lambda: 0.1  # < 0.2, should trigger damage

    _create_equipment_agents(mocked_model, equipment_positions)

    # Verify all equipment was created and placed
    all_agents = list(mocked_model.schedule.agents)
    equipment_agents = [
        agent
        for agent in all_agents
        if isinstance(
            agent,
            (
                CentralCommunicationsSystem,
                PowerDistributionHub,
                BatteryPack,
                HazardousMaterialsStorage,
            ),
        )
    ]

    assert len(equipment_agents) == 4

    # Verify specific equipment types and positions
    comm_system = [
        agent
        for agent in equipment_agents
        if isinstance(agent, CentralCommunicationsSystem)
    ][0]
    power_hub = [
        agent for agent in equipment_agents if isinstance(agent, PowerDistributionHub)
    ][0]
    battery = [agent for agent in equipment_agents if isinstance(agent, BatteryPack)][0]
    hazmat = [
        agent
        for agent in equipment_agents
        if isinstance(agent, HazardousMaterialsStorage)
    ][0]

    assert comm_system.pos == (0, 0)
    assert comm_system.integrity == 25
    assert power_hub.pos == (1, 1)
    assert power_hub.integrity == 100
    assert battery.pos == (2, 2)
    assert battery.integrity == 29  # Should be damaged due to random < 0.2
    assert hazmat.pos == (3, 3)
    assert hazmat.integrity == 90


def test_create_human_agents_zone_placement(mocked_model):
    mocked_model.zones = {
        "habitat": {"positions": [(0, 0), (1, 1), (2, 2)]},
        "lab": {"positions": [(3, 3), (4, 4)]},
        "corridor": {"positions": [(5, 5)]},  # Should not be used for humans
    }
    config_params = {"CREW_SIZE": 4}

    _create_human_agents(mocked_model, config_params)

    # Verify correct number of humans created
    all_agents = list(mocked_model.schedule.agents)
    humans = [agent for agent in all_agents if isinstance(agent, Human)]
    assert len(humans) == 4

    # Verify humans are placed only in habitat or lab zones
    valid_positions = (
        mocked_model.zones["habitat"]["positions"] + mocked_model.zones["lab"]["positions"]
    )
    for human in humans:
        assert human.pos in valid_positions

    # Verify health distribution (70% injured at 85 health, 30% at 65 health)
    health_85_count = len([h for h in humans if h.health == 85])
    health_65_count = len([h for h in humans if h.health == 65])

    # With crew size 4: 70% of 4 = 2.8 -> int(2.8) = 2 injured, 2 healthy
    assert health_85_count == 2  # injured
    assert health_65_count == 2  # healthy


def test_create_robot_agents_zone_distribution(mocked_model):
    mocked_model.zones = {
        "lab": {"positions": [(0, 0), (1, 1)]},
        "medical_bay": {"positions": [(2, 2)]},
        "habitat": {"positions": [(3, 3), (4, 4)]},
        "control_module": {"positions": [(5, 5)]},
        "power_distribution": {"positions": [(6, 6)]},
        "outdoors": {"positions": [(7, 7)]},
        "deposit": {"positions": [(8, 8)]},
        "airlock": {"positions": [(9, 9)]},
    }
    config_params = {
        "ROBOT_COUNTS": {
            "BioLabRobot": 2,
            "MaintenanceRobot": 3,
            "ConstructionRobot": 1,
            "EVASpecialistRobot": 1,
            "LogisticsRobot": 1,
        }
    }

    _create_robot_agents(mocked_model, config_params)

    # Verify correct number of robots created
    all_agents = list(mocked_model.schedule.agents)
    robots = [
        agent
        for agent in all_agents
        if isinstance(
            agent,
            (
                BioLabRobot,
                MaintenanceRobot,
                ConstructionRobot,
                EVASpecialistRobot,
                LogisticsRobot,
            ),
        )
    ]
    assert len(robots) == 8

    # Verify robot types
    biolab_robots = [r for r in robots if isinstance(r, BioLabRobot)]
    maintenance_robots = [r for r in robots if isinstance(r, MaintenanceRobot)]
    construction_robots = [r for r in robots if isinstance(r, ConstructionRobot)]
    eva_robots = [r for r in robots if isinstance(r, EVASpecialistRobot)]
    logistics_robots = [r for r in robots if isinstance(r, LogisticsRobot)]

    assert len(biolab_robots) == 2
    assert len(maintenance_robots) == 3
    assert len(construction_robots) == 1
    assert len(eva_robots) == 1
    assert len(logistics_robots) == 1

    # Verify robots are placed in their operational zones
    # BioLabRobot should be in medical_bay or lab
    biolab_valid_positions = (
        mocked_model.zones["medical_bay"]["positions"]
        + mocked_model.zones["lab"]["positions"]
    )
    for robot in biolab_robots:
        assert robot.pos in biolab_valid_positions

    # MaintenanceRobot should be in control_module, habitat, or power_distribution
    maintenance_valid_positions = (
        mocked_model.zones["control_module"]["positions"]
        + mocked_model.zones["habitat"]["positions"]
        + mocked_model.zones["power_distribution"]["positions"]
    )
    for robot in maintenance_robots:
        assert robot.pos in maintenance_valid_positions


def test_get_realistic_robot_position_fallback(mocked_model):
    mocked_model.zones = {
        "corridor": {"positions": [(0, 0), (1, 1)]},
        "habitat": {"positions": [(2, 2)]},
    }

    # BioLabRobot prefers medical_bay and lab, but they don't exist
    # Should fallback to available zones
    position = _get_realistic_robot_position(mocked_model, "BioLabRobot", 0)
    valid_positions = [(0, 0), (1, 1), (2, 2)]
    assert position in valid_positions


def test_get_realistic_robot_position_distribution(mocked_model):
    mocked_model.zones = {
        "lab": {"positions": [(0, 0)]},
        "medical_bay": {"positions": [(1, 1)]},
    }

    # Create multiple BioLabRobots and verify they're distributed across zones
    positions = []
    for i in range(4):
        position = _get_realistic_robot_position(mocked_model, "BioLabRobot", i)
        positions.append(position)

    # Should alternate between lab and medical_bay
    assert (0, 0) in positions  # lab
    assert (1, 1) in positions  # medical_bay


def test_robot_position_no_valid_zones():
    model = MagicMock()
    model.zones = {"habitat_wall": {"positions": []}, "power_wall": {"positions": []}}

    with pytest.raises(
        ValueError, match="No valid zones available for robot placement"
    ):
        _get_realistic_robot_position(model, "BioLabRobot", 0)


def test_find_valid_position_in_zone_real(mocked_model):
    mocked_model.zones = {"test_zone": {"positions": [(0, 0), (1, 1), (2, 2)]}}

    position = _find_valid_position_in_zone(mocked_model, "test_zone")
    assert position in [(0, 0), (1, 1), (2, 2)]


def test_find_valid_position_in_zone_invalid_zone(mocked_model):
    with pytest.raises(ValueError, match="Zone with code 'invalid' not found"):
        _find_valid_position_in_zone(mocked_model, "invalid")


def test_find_valid_position_in_zone_no_positions(mocked_model):
    mocked_model.zones = {"empty_zone": {"positions": []}}

    with pytest.raises(
        ValueError, match="No valid positions available in zone 'empty_zone'"
    ):
        _find_valid_position_in_zone(mocked_model, "empty_zone")


def test_get_equipment_position_real(mocked_model):
    mocked_model.zones = {"corridor": {"positions": [(0, 0), (1, 1), (2, 2)]}}

    position = _get_equipment_position(mocked_model, "corridor")
    assert position in [(0, 0), (1, 1), (2, 2)]


def test_get_equipment_position_invalid_zone(mocked_model):
    """Test error handling for invalid zone in equipment placement"""
    with pytest.raises(ValueError, match="Zone with code 'nonexistent' not found"):
        _get_equipment_position(mocked_model, "nonexistent")


def test_human_placement_no_preferred_zones():
    model = MagicMock()
    model.zones = {
        "corridor": {"positions": [(0, 0)]},
        "outdoors": {"positions": [(1, 1)]},
    }

    with pytest.raises(
        ValueError, match="No preferred zones available for human placement"
    ):
        _get_random_human_position(model)


def test_equipment_agents_unknown_type(mocked_model):
    equipment_positions = [
        {"type": "UnknownEquipment", "x": 0, "y": 0, "integrity": 100},
        {"type": "CentralCommunicationsSystem", "x": 1, "y": 1, "integrity": 25},
    ]

    _create_equipment_agents(mocked_model, equipment_positions)

    # Only the known equipment should be created
    all_agents = list(mocked_model.schedule.agents)
    equipment_agents = [
        agent
        for agent in all_agents
        if isinstance(
            agent,
            (
                CentralCommunicationsSystem,
                PowerDistributionHub,
                BatteryPack,
                HazardousMaterialsStorage,
            ),
        )
    ]

    assert len(equipment_agents) == 1
    assert isinstance(equipment_agents[0], CentralCommunicationsSystem)
