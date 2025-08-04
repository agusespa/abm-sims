import pytest
import json
import tempfile
import os
from mars_crisis_abm.model import MarsModel
from mars_crisis_abm.utils import load_grid_layout_csv


@pytest.fixture
def config_params():
    with open("config/params.json") as f:
        return json.load(f)


@pytest.fixture
def grid_data_and_equipment(test_csv_data):
    return load_grid_layout_csv(test_csv_data)


@pytest.fixture
def test_csv_data():
    """Create a temporary CSV file for testing with all required zones"""
    csv_content = """;;;;;T;T;T
;A;H;H;M;M;T;T
;A;H;H;M;C;T;T
;C;C;1;C;C;C;C
;L;L;C;R;D;D;
;L;L;2;R;D;C;
;;;;;3;D;"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    yield temp_path

    os.unlink(temp_path)


def test_model_creation_simple(config_params, grid_data_and_equipment):
    grid_data, equipment_positions = grid_data_and_equipment

    model = MarsModel(config_params, grid_data, equipment_positions)

    # Assertions to check model initialization
    assert model.config_params == config_params
    assert model.grid_data == grid_data
    assert model.grid is not None
    assert model.mission_status == "ONGOING"
    assert model.communications_online == False
    assert model.fire_alarm_on == False
    assert model.atmospheric_condition == 100.0
    assert model.contamination_level == 0.0

    # Check grid dimensions
    expected_height = len(grid_data)
    expected_width = len(grid_data[0])
    assert model.grid.width == expected_width
    assert model.grid.height == expected_height


def test_csv_loading(grid_data_and_equipment):
    grid_data, equipment_positions = grid_data_and_equipment

    # Test grid data structure
    assert len(grid_data) == 7  # 7 rows
    assert len(grid_data[0]) == 8  # 8 columns
    assert grid_data[0][0] == "outdoors"  # Empty becomes outdoors
    assert grid_data[1][1] == "airlock"  # A becomes airlock
    assert grid_data[1][2] == "habitat"  # H becomes habitat
    assert grid_data[1][4] == "medical_bay"  # M becomes medical_bay
    assert grid_data[4][4] == "control_module"  # R becomes control_module
    assert grid_data[4][5] == "power_distribution"  # D becomes power_distribution

    # Test equipment positions - equipment sits on corridor zones
    assert len(equipment_positions) == 3  # 1, 2, and 3 symbols

    # Equipment positions should be on corridor zones
    assert grid_data[3][3] == "corridor"  # Equipment 1 sits on corridor
    assert grid_data[5][3] == "corridor"  # Equipment 2 sits on corridor
    assert grid_data[6][5] == "corridor"  # Equipment 3 sits on corridor

    # Find equipment by type
    comm_equipment = [
        eq for eq in equipment_positions if eq["type"] == "CentralCommunicationsSystem"
    ]
    power_equipment = [
        eq for eq in equipment_positions if eq["type"] == "PowerDistributionHub"
    ]
    battery_equipment = [
        eq for eq in equipment_positions if eq["type"] == "BatteryPack"
    ]

    assert len(comm_equipment) == 1
    assert len(power_equipment) == 1
    assert len(battery_equipment) == 1
    assert comm_equipment[0]["integrity"] == 25  # Communications always starts at 25
