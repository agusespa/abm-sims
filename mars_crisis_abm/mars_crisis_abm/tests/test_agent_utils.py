import pytest
from mars_crisis_abm.utils.enums import OperatingEnvironment, ZoneCode
from mars_crisis_abm.utils.agent_utils import get_zones_by_type

@pytest.fixture
def mock_zones():
    zones = {
        ZoneCode.LAB.value: {"code": ZoneCode.LAB.value, "type": OperatingEnvironment.INTERNAL.value},
        ZoneCode.CORRIDOR.value: {"code": ZoneCode.CORRIDOR.value, "type": OperatingEnvironment.INTERNAL.value},
        ZoneCode.OUTDOORS.value: {"code": ZoneCode.OUTDOORS.value, "type": OperatingEnvironment.EXTERNAL.value},
        ZoneCode.HABITAT.value: {"code": ZoneCode.HABITAT.value, "type": OperatingEnvironment.INTERNAL.value},
        ZoneCode.POWER_STATION.value: {"code": ZoneCode.POWER_STATION.value, "type": OperatingEnvironment.INTERNAL.value},
        ZoneCode.AIRLOCK.value: {"code": ZoneCode.AIRLOCK.value, "type": OperatingEnvironment.MIXED.value},
    }
    return zones

def test_get_zones_by_type_mixed(mock_zones):
    mixed_zones = get_zones_by_type(mock_zones, OperatingEnvironment.MIXED)
    expected_zones = [ZoneCode.LAB.value, ZoneCode.CORRIDOR.value, ZoneCode.OUTDOORS.value, ZoneCode.HABITAT.value, ZoneCode.POWER_STATION.value, ZoneCode.AIRLOCK.value]
    assert sorted(mixed_zones) == sorted(expected_zones)

def test_get_zones_by_type_internal(mock_zones):
    internal_zones = get_zones_by_type(mock_zones, OperatingEnvironment.INTERNAL)
    expected_zones = [ZoneCode.LAB.value, ZoneCode.HABITAT.value, ZoneCode.CORRIDOR.value, ZoneCode.POWER_STATION.value, ZoneCode.AIRLOCK.value]
    assert sorted(internal_zones) == sorted(expected_zones)

def test_get_zones_by_type_external(mock_zones):
    external_zones = get_zones_by_type(mock_zones, OperatingEnvironment.EXTERNAL)
    expected_zones = [ZoneCode.OUTDOORS.value, ZoneCode.AIRLOCK.value]
    assert sorted(external_zones) == sorted(expected_zones)
