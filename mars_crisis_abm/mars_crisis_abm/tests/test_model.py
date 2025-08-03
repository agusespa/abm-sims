import pytest
from mars_crisis_abm.model import MarsModel
from mars_crisis_abm.agents import (
    Human,
    CentralCommunicationsSystem,
    BatteryPack,
    HabitatWall,
    ExternalWall,
    PowerWall,
)
from mars_crisis_abm.utils.enums import OperatingEnvironment, ZoneCode
from mars_crisis_abm.utils.agent_utils import get_zones_by_type


@pytest.fixture
def model():
    grid_data = [
        ["outdoors", "outdoors", "outdoors"],
        ["outdoors", "habitat", "outdoors"],
        ["outdoors", "outdoors", "outdoors"],
    ]
    equipment_positions = []

    model = MarsModel(
        config_params={
            "ROBOT_COUNTS": {},
            "CREW_SIZE": 1,
        },
        grid_data=grid_data,
        equipment_positions=equipment_positions,
    )

    for agent in list(model.agents):
        agent.remove()

    CentralCommunicationsSystem(model, 100)
    Human(model, 100)
    BatteryPack(model, 10)

    yield model


@pytest.fixture
def model_with_walls():
    grid_data = [
        ["habitat_wall", "habitat_wall", "outdoors"],
        ["habitat_wall", "habitat", "power_wall"],
        ["outdoors", "outdoors", "outdoors"],
    ]
    equipment_positions = []

    model = MarsModel(
        config_params={
            "ROBOT_COUNTS": {},
            "CREW_SIZE": 1,
        },
        grid_data=grid_data,
        equipment_positions=equipment_positions,
    )
    # Clear agents created by default to control test environment
    for agent in list(model.schedule.agents):
        model.schedule.remove(agent)
    for x in range(model.grid.width):
        for y in range(model.grid.height):
            cell_contents = model.grid.get_cell_list_contents((x, y))
            for agent in list(cell_contents):
                model.grid.remove_agent(agent)

    # Manually place agents for testing is_wall
    model.grid.place_agent(HabitatWall(model, 100), (0, 0))
    model.grid.place_agent(ExternalWall(model, 100), (1, 0))
    model.grid.place_agent(PowerWall(model, 100), (2, 1))

    yield model


@pytest.fixture
def model_with_zones():
    grid_data = [
        ["lab", "corridor", "outdoors"],
        ["lab", "habitat", "outdoors"],
        ["power_station", "corridor", "outdoors"],
    ]
    equipment_positions = []

    model = MarsModel(
        config_params={
            "ROBOT_COUNTS": {},
            "CREW_SIZE": 1,
        },
        grid_data=grid_data,
        equipment_positions=equipment_positions,
    )
    yield model


def test_check_mission_status_success(model):
    model.power_level = 80
    model.atmospheric_condition = 80
    model.contamination_level = 0
    model.communications_online = True

    assert model._check_mission_status() == "SUCCESS"


def test_check_mission_status_failure_power_level(model):
    model.power_level = 5
    model.atmospheric_condition = 80
    model.contamination_level = 5
    model.communications_online = False

    assert model._check_mission_status() == "FAILURE"


def test_check_mission_status_failure_atmospheric_condition(model):
    model.power_level = 80
    model.atmospheric_condition = 5
    model.contamination_level = 5
    model.communications_online = False

    assert model._check_mission_status() == "FAILURE"


def test_check_mission_status_failure_no_living_humans(model):
    model.power_level = 80
    model.atmospheric_condition = 80
    model.contamination_level = 5
    model.communications_online = False

    human = [agent for agent in model.agents if isinstance(agent, Human)]
    human[0].health = 0

    assert model._check_mission_status() == "FAILURE"


def test_check_mission_status_ongoing(model):
    model.power_level = 50
    model.atmospheric_condition = 50
    model.contamination_level = 20
    model.communications_online = False

    assert model._check_mission_status() == "ONGOING"


def test_update_system_status_communications(model):
    model._update_system_status()
    assert model.communications_online is True

    comm_system = [
        agent
        for agent in model.agents
        if isinstance(agent, CentralCommunicationsSystem)
    ]
    comm_system[0].integrity = 20
    model._update_system_status()

    assert model.communications_online is False


def test_update_system_status_fire_alarm(model):
    # Test with power on and no fires
    model.power_level = 50
    model._update_system_status()
    assert model.fire_alarm_on is False

    # Test with power on and a fire
    comm_system = [agent for agent in model.agents if isinstance(agent, BatteryPack)]
    comm_system[0].fire_intensity = 50
    model._update_system_status()
    assert model.fire_alarm_on is True

    # Test with power off
    model.power_level = 0
    model._update_system_status()
    assert model.fire_alarm_on is False





def test_get_zones_by_type_mixed(model_with_zones):
    mixed_zones = get_zones_by_type(model_with_zones.zones, OperatingEnvironment.MIXED)
    expected_zones = [
        ZoneCode.LAB.value,
        ZoneCode.CORRIDOR.value,
        ZoneCode.OUTDOORS.value,
        ZoneCode.HABITAT.value,
        ZoneCode.POWER_STATION.value,
    ]
    assert sorted(mixed_zones) == sorted(expected_zones)


def test_get_zones_by_type_internal(model_with_zones):
    internal_zones = get_zones_by_type(model_with_zones.zones, OperatingEnvironment.INTERNAL)
    expected_zones = [
        ZoneCode.LAB.value,
        ZoneCode.HABITAT.value,
        ZoneCode.CORRIDOR.value,
        ZoneCode.POWER_STATION.value,
    ]
    assert sorted(internal_zones) == sorted(expected_zones)


def test_get_zones_by_type_external(model_with_zones):
    external_zones = get_zones_by_type(model_with_zones.zones, OperatingEnvironment.EXTERNAL)
    expected_zones = [ZoneCode.OUTDOORS.value]
    assert sorted(external_zones) == sorted(expected_zones)
