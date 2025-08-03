import pytest
from unittest.mock import MagicMock, patch
from mars_crisis_abm.blueprint import build_base_from_blueprint, _create_wall_agents, _get_wall_integrity
from mars_crisis_abm.agents import HabitatWall, ExternalWall, PowerWall
from mars_crisis_abm.utils.enums import OperatingEnvironment

@pytest.fixture
def model():
    model = MagicMock()
    model.zones = {}
    model.schedule = MagicMock()
    model.schedule.add = MagicMock()
    model.grid = MagicMock()
    model.grid.place_agent = MagicMock()
    model.random = MagicMock()
    return model

@pytest.mark.parametrize("random_value, expected_integrity", [
    (0.7, 100.0),  # 80% chance of perfect walls
    (0.85, 85.0), # 10% chance of slightly damaged
    (0.92, 70.0), # 5% chance of moderately damaged
    (0.97, 55.0)  # 5% chance of badly damaged
])
def test_get_wall_integrity(model, random_value, expected_integrity):
    model.random.random.return_value = random_value
    assert _get_wall_integrity(model) == expected_integrity

@pytest.mark.parametrize("zone_code, expected_agents", [
    ("habitat_wall", [HabitatWall, ExternalWall]),
    ("power_wall", [PowerWall]),
    ("some_other_zone", [])
])
def test_create_wall_agents(model, zone_code, expected_agents):
    with patch('mars_crisis_abm.blueprint._get_wall_integrity', return_value=100.0):
        agents = _create_wall_agents(zone_code, model)
        assert len(agents) == len(expected_agents)
        for agent, expected_agent_type in zip(agents, expected_agents):
            assert isinstance(agent, expected_agent_type)

def test_build_base_from_blueprint(model):
    grid_data = [
        ["habitat_wall", "habitat_wall", "habitat_wall"],
        ["habitat_wall", "habitat", "habitat_wall"],
        ["habitat_wall", "power_wall", "habitat_wall"],
    ]

    with patch('mars_crisis_abm.blueprint._get_wall_integrity', return_value=100.0):
        build_base_from_blueprint(model, grid_data)

    assert "habitat_wall" in model.zones
    assert "habitat" in model.zones
    assert "power_wall" in model.zones

    assert model.zones["habitat"]["bounds"] == [1, 1, 2, 2]
    assert model.zones["habitat"]["type"] == OperatingEnvironment.INTERNAL.value
    assert model.zones["habitat"]["positions"] == [(1, 1)]

    # 7 habitat_wall cells * 2 agents/cell + 1 power_wall cell * 1 agent/cell = 15
    assert model.grid.place_agent.call_count == 15

def test_build_base_from_blueprint_multiple_zones(model):
    grid_data = [
        ["habitat", "corridor", "lab"],
        ["habitat", "corridor", "lab"],
    ]
    build_base_from_blueprint(model, grid_data)

    assert model.zones["habitat"]["bounds"] == [0, 0, 1, 2]
    assert model.zones["corridor"]["bounds"] == [1, 0, 2, 2]
    assert model.zones["lab"]["bounds"] == [2, 0, 3, 2]

    assert len(model.zones["habitat"]["positions"]) == 2
    assert len(model.zones["corridor"]["positions"]) == 2
    assert len(model.zones["lab"]["positions"]) == 2

def test_build_base_from_blueprint_no_walls(model):
    grid_data = [
        ["habitat", "habitat"],
        ["habitat", "habitat"],
    ]
    build_base_from_blueprint(model, grid_data)
    assert model.grid.place_agent.call_count == 0
