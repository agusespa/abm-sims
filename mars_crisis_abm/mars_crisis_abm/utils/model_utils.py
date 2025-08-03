import json
import csv
from .grid_mapping import ZONE_MAPPING, EQUIPMENT_MAPPING


def _get_default_equipment_integrity(equipment_type):
    """Get default integrity values for equipment types with some variation"""
    import random

    if equipment_type == "CentralCommunicationsSystem":
        return 25

    base_values = {
        "PowerDistributionHub": (75, 90),  # Less damaged
        "BatteryPack": (60, 85),  # Less damaged, less variable
        "HazardousMaterialsStorage": (65, 80),  # Less damaged
    }

    if equipment_type in base_values:
        min_val, max_val = base_values[equipment_type]
        return random.randint(min_val, max_val)
    else:
        raise ValueError("Equipement not supported")


def load_config(file_path):
    """
    Loads configuration parameters from a JSON file.

    Args:
        file_path (str): The path to the JSON configuration file.

    Returns:
        dict: The loaded configuration parameters.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.
        Exception: For any other unexpected errors.
    """
    config_params = {}
    try:
        with open(file_path, "r") as f:
            config_params = json.load(f)
    except FileNotFoundError:
        raise ValueError(
            f"Error: The configuration file was not found at '{file_path}'"
        )
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Error: The configuration file '{file_path}' is not valid JSON. Details: {e}"
        )
    except Exception as e:
        raise ValueError(f"An unexpected error occurred while loading the file: {e}")

    return config_params


def load_grid_layout_csv(file_path):
    """
    Loads grid layout from a CSV file where each cell contains a symbol
    representing either a zone type or equipment.

    Args:
        file_path (str): The path to the CSV grid file.

    Returns:
        tuple: (grid_data, equipment_positions)
    """
    grid_data = []
    equipment_positions = []

    try:
        with open(file_path, "r") as f:
            reader = csv.reader(f, delimiter=";")
            for y, row in enumerate(reader):
                grid_row = []
                for x, cell in enumerate(row):
                    cell = cell.strip()

                    if not cell:
                        grid_row.append("outdoors")

                    elif cell in EQUIPMENT_MAPPING:
                        equipment_positions.append(
                            {
                                "x": x,
                                "y": y,
                                "type": EQUIPMENT_MAPPING[cell],
                                "integrity": _get_default_equipment_integrity(
                                    EQUIPMENT_MAPPING[cell]
                                ),
                            }
                        )
                        grid_row.append("corridor")

                    elif cell in ZONE_MAPPING:
                        grid_row.append(ZONE_MAPPING[cell])

                    else:
                        raise ValueError(f"Unsupported zone: ", cell)

                grid_data.append(grid_row)

    except FileNotFoundError:
        raise ValueError(f"Error: The grid layout file was not found at '{file_path}'")
    except Exception as e:
        raise ValueError(
            f"An unexpected error occurred while loading the grid layout: {e}"
        )

    return grid_data, equipment_positions
