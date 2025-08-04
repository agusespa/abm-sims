from enum import Enum

class Capability(Enum):
    FIRST_AID = "first-aid"

    HAZARD = "hazard"

    WALL_INT_DETECT = "wall-int_detect"
    WALL_INT = "wall-int"
    WALL_EXT_DETECT = "wall-ext_detect"
    WALL_EXT = "wall-ext"

    FIRE = "fire"

    POWER_INT_DETECT = "power-int_detect"
    POWER_INT = "power-int"
    POWER_EXT_DETECT = "power-ext_detect"
    POWER_EXT = "power-ext"

    CONTROL_DETECT = "control_detect"
    CONTROL = "control"

    SUPPLIES = "supplies"
    FIRE_SUPPLIES = "fire-supplies"
    MATERIALS = "materials"


class InventoryType(Enum):
    SUPPLIES = "supplies"
    MATERIALS = "materials"
    FIRE_POWDER = "fire_powder"


class OperatingEnvironment(Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    MIXED = "mixed"
    NONE = "none"


class ZoneCode(Enum):
    OUTDOORS = "outdoors"
    AIRLOCK = "airlock"
    HABITAT = "habitat"
    MEDICAL_BAY = "medical_bay"
    LAB = "lab"
    CONTROL_MODULE = "control_module"
    POWER_DISTRIBUTION_MODULE = "power_distribution"
    POWER_STATION = "power_station"
    DEPOSIT = "deposit"
    CORRIDOR = "corridor"
    HABITAT_WALL = "habitat_wall"
    POWER_WALL = "power_wall"

ZONE_ENVIRONMENT_MAP = {
    ZoneCode.OUTDOORS: OperatingEnvironment.EXTERNAL,
    ZoneCode.AIRLOCK: OperatingEnvironment.MIXED,
    ZoneCode.DEPOSIT: OperatingEnvironment.MIXED,
    ZoneCode.HABITAT: OperatingEnvironment.INTERNAL,
    ZoneCode.MEDICAL_BAY: OperatingEnvironment.INTERNAL,
    ZoneCode.LAB: OperatingEnvironment.INTERNAL,
    ZoneCode.CONTROL_MODULE: OperatingEnvironment.INTERNAL,
    ZoneCode.POWER_DISTRIBUTION_MODULE: OperatingEnvironment.INTERNAL,
    ZoneCode.POWER_STATION: OperatingEnvironment.INTERNAL,
    ZoneCode.CORRIDOR: OperatingEnvironment.INTERNAL,
    ZoneCode.HABITAT_WALL: OperatingEnvironment.NONE,
    ZoneCode.POWER_WALL: OperatingEnvironment.NONE,
}

ROBOT_OPERATIONAL_ZONES = {
    "BioLabRobot": [ZoneCode.MEDICAL_BAY.value, ZoneCode.LAB.value],
    "MaintenanceRobot": [
        ZoneCode.CONTROL_MODULE.value,
        ZoneCode.HABITAT.value,
        ZoneCode.POWER_DISTRIBUTION_MODULE.value,
    ],
    "ConstructionRobot": [ZoneCode.OUTDOORS.value, ZoneCode.DEPOSIT.value],
    "EVASpecialistRobot": [ZoneCode.AIRLOCK.value, ZoneCode.DEPOSIT.value],
    "LogisticsRobot": [ZoneCode.OUTDOORS.value, ZoneCode.DEPOSIT.value],
}
