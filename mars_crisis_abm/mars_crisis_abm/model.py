import mesa

from . import blueprint

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
from .utils import STABILITY_THRESHOLDS, ROBOT_OPERATIONAL_ZONES, ZoneCode


class MarsModel(mesa.Model):

    def __init__(self, config_params, grid_data, equipment_positions):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)

        self.config_params = config_params
        self.grid_data = grid_data
        self.mission_status = "ONGOING"

        height = len(self.grid_data)
        width = len(self.grid_data[0])
        self.grid = mesa.space.MultiGrid(width, height, False)

        self.zones = {}
        self.equipment_positions = equipment_positions
        blueprint.build_base_from_blueprint(self, self.grid_data)

        self.communications_online = False
        self.fire_alarm_on = False
        self.atmospheric_condition = 100.0
        self.contamination_level = 0.0
        self.power_level = STABILITY_THRESHOLDS["power"] - 10

        self._create_equipment_agents()
        self._create_human_agents()
        self.robot_counts = config_params["ROBOT_COUNTS"]
        self._create_robot_agents()

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Atmospheric Condition": lambda m: m.atmospheric_condition,
                "Power Level": lambda m: m.power_level,
                "Dead Humans": lambda m: m._count_alive_humans(),
                "Critical Humans": lambda m: m._count_critical_humans(),
                "Contamination Level": lambda m: m.contamination_level,
                "Damaged Walls": lambda m: m._count_damaged_walls(),
                "Damaged Power Walls": lambda m: m._count_damaged_power_walls(),
                "Damaged Equipment": lambda m: m._count_damaged_equipment(),
                "Active Fires": lambda m: m._count_active_fires(),
                "Recharging Robots": lambda m: m._count_recharging_robots(),
                "Working Robots": lambda m: m._count_working_robots(),
                "Idle Robots": lambda m: m._count_idle_robots(),
                "Searching Robots": lambda m: m._count_searching_robots(),
            }
        )

    def step(self):
        self.schedule.step()

        self._update_system_status()

        self.datacollector.collect(self)

        self.mission_status = self._check_mission_status()
        if self.mission_status != "ONGOING":
            self.running = False

    def _create_robot_agents(self):
        robot_classes = {
            "BioLabRobot": BioLabRobot,
            "MaintenanceRobot": MaintenanceRobot,
            "ConstructionRobot": ConstructionRobot,
            "EVASpecialistRobot": EVASpecialistRobot,
            "LogisticsRobot": LogisticsRobot,
        }
        
        for robot_type, count in self.robot_counts.items():
            robot_class = robot_classes.get(robot_type)
            if not robot_class:
                raise ValueError(f"Unknown robot type: {robot_type}")
            
            for i in range(count):
                robot = robot_class(self)
                position = self._get_realistic_robot_position(robot_type, i,)
                self.grid.place_agent(robot, position)
                self.schedule.add(robot)

    def _get_realistic_robot_position(self, robot_type, robot_index):
        available_zones = ROBOT_OPERATIONAL_ZONES[robot_type]
        if not available_zones:
            raise ValueError(f"No operational zones found for robot type '{robot_type}'")

        # Distribute robots evenly across available zones
        chosen_zone_code = available_zones[robot_index % len(available_zones)]
        
        return self._find_valid_position_in_zone(chosen_zone_code)

    def _find_valid_position_in_zone(self, zone_code):
        if zone_code not in self.zones:
            raise ValueError(f"Zone with code '{zone_code}' not found")

        available_positions = self.zones[zone_code]["positions"]
        if not available_positions:
            raise ValueError(f"No valid positions available in zone '{zone_code}'")

        return self.random.choice(available_positions)

    def _create_human_agents(self):
        crew_size = self.config_params.get("CREW_SIZE")
        injured_count = int(crew_size * 0.7)

        health_configs = [
            (injured_count, 85),
            (crew_size - injured_count, 65),
        ]

        for count, health in health_configs:
            for _ in range(count):
                human = Human(self, health)
                position = self._get_random_human_position()
                self.grid.place_agent(human, position)
                human.pos = position
                self.schedule.add(human)

    def _get_random_human_position(self):
        preferred_zones = [ZoneCode.LAB.value, ZoneCode.HABITAT.value]
        available_preferred_zones = [
            zone for zone in preferred_zones if zone in self.zones
        ]
        if not available_preferred_zones:
            raise ValueError("No preferred zones available for human placement")
        chosen_zone = self.random.choice(available_preferred_zones)
        return self._get_equipment_position(chosen_zone)

    def _create_equipment_agents(self):
        equipment_classes = {
            "CentralCommunicationsSystem": CentralCommunicationsSystem,
            "PowerDistributionHub": PowerDistributionHub,
            "BatteryPack": BatteryPack,
            "HazardousMaterialsStorage": HazardousMaterialsStorage,
        }

        for equipment_data in self.equipment_positions:
            equipment_type = equipment_data["type"]
            equipment_class = equipment_classes.get(equipment_type)

            if equipment_class:
                initial_integrity = equipment_data["integrity"]
                if equipment_type == "BatteryPack" and self.random.random() < 0.2:
                    initial_integrity = 29

                equipment = equipment_class(
                    self,
                    integrity=initial_integrity,
                )
                self.grid.place_agent(
                    equipment, (equipment_data["x"], equipment_data["y"])
                )
                self.schedule.add(equipment)

    def _get_equipment_position(self, zone_code):
        if zone_code in self.zones:
            available_positions = self.zones[zone_code]["positions"]
            if not available_positions:
                raise ValueError(f"No valid positions available in zone '{zone_code}'")
            return self.random.choice(available_positions)
        raise ValueError(f"Zone with code '{zone_code}' not found.")

    def _update_system_status(self):
        # Update communications status
        comm_system = [
            agent
            for agent in self.agents
            if isinstance(agent, CentralCommunicationsSystem)
        ]

        self.communications_online = (
            comm_system[0].integrity > STABILITY_THRESHOLDS["communications"]
        )

        # Update fire alarm status
        if self.power_level <= 0:
            self.fire_alarm_on = False
        else:
            has_fire = False
            for agent in self.agents:
                if (
                    isinstance(agent, ComplexStructure)
                    and hasattr(agent, "fire_intensity")
                    and agent.fire_intensity > 0
                ):
                    has_fire = True
                    break
            self.fire_alarm_on = has_fire

        # Calculate power level based on power walls and batteries
        batteries = [agent for agent in self.agents if isinstance(agent, BatteryPack)]

        power_walls = [agent for agent in self.agents if isinstance(agent, PowerWall)]

        total_power_integrity = 0
        total_power_components = 0

        for wall in power_walls:
            total_power_integrity += wall.integrity
            total_power_components += 1

        for battery in batteries:
            total_power_integrity += battery.integrity
            total_power_components += 1

        if total_power_components > 0:
            self.power_level = total_power_integrity / total_power_components
        else:
            self.power_level = 0

        atmospheric_decrease = 0
        wall_damage_total = 0
        damaged_walls_total = 0

        for agent in self.agents:
            if isinstance(agent, HabitatWall):
                if agent.integrity < 100:
                    damaged_walls_total += 1
                    wall_damage_total += 100 - agent.integrity

        if damaged_walls_total > 0:
            atmospheric_decrease = wall_damage_total / (100 * damaged_walls_total * 8)

        # Add fire impact on atmosphere
        fire_strength_total = sum(
            agent.fire_intensity
            for agent in self.agents
            if isinstance(agent, ComplexStructure) and hasattr(agent, "fire_intensity")
        )

        if fire_strength_total > 0:
            atmospheric_decrease += fire_strength_total / 800

        # Calculate contamination level and add impact on atmosphere
        hazmat_storage = [
            agent
            for agent in self.agents
            if isinstance(agent, HazardousMaterialsStorage)
        ]

        contamination_decrease = 0
        contamination_total = 0
        damaged_hazmat_storage_total = 0
        for storage in hazmat_storage:
            damaged_hazmat_storage_total += 1
            contamination_total += 100 - storage.integrity

        if contamination_total > 0:
            contamination_decrease = contamination_total / (
                100 * 6
            )

        self.contamination_level = contamination_decrease * 100

        atmospheric_decrease += contamination_decrease

        self.atmospheric_condition -= atmospheric_decrease

    def _check_mission_status(self):
        """
        Check mission status based on termination criteria:
        - SUCCESS: Systems stabilized (power > 70, atmosphere > 70, contamination < 10) and communications_online == True
        - FAILURE: Critical metrics unrecoverable
        - ONGOING
        """

        # Check for mission success - systems stabilized and communications restored
        systems_stabilized = (
            self.power_level > STABILITY_THRESHOLDS["power"]
            and self.atmospheric_condition > STABILITY_THRESHOLDS["atmosphere"]
            and self.contamination_level < STABILITY_THRESHOLDS["contamination"]
            and self.communications_online
        )
        if systems_stabilized:
            return "SUCCESS"

        # Check for mission failure - any critical metric below 10
        systems_failed = self.power_level < 10 or self.atmospheric_condition < 10
        if systems_failed:
            return "FAILURE"

        # Check for mission failure - all humans are dead
        living_humans = [
            agent
            for agent in self.agents
            if isinstance(agent, Human) and agent.health > 0
        ]
        if len(living_humans) == 0:
            return "FAILURE"

        return "ONGOING"

    def _count_damaged_walls(self):
        return len(
            [
                agent
                for agent in self.agents
                if isinstance(agent, (HabitatWall, ExternalWall))
                and agent.integrity < 80
            ]
        )

    def _count_damaged_power_walls(self):
        return len(
            [
                agent
                for agent in self.agents
                if isinstance(agent, PowerWall) and agent.integrity < 80
            ]
        )

    def _count_damaged_equipment(self):
        damaged_count = 0
        for agent in self.agents:
            if isinstance(
                agent,
                (
                    CentralCommunicationsSystem,
                    PowerDistributionHub,
                    BatteryPack,
                    HazardousMaterialsStorage,
                ),
            ):
                if agent.integrity < 80:
                    damaged_count += 1
        return damaged_count

    def _count_active_fires(self):
        return len(
            [
                agent
                for agent in self.agents
                if isinstance(agent, ComplexStructure)
                and hasattr(agent, "fire_intensity")
                and agent.fire_intensity > 0
            ]
        )

    def _count_critical_humans(self):
        critical_count = 0
        for agent in self.agents:
            if isinstance(agent, Human) and agent.health < 30 and agent.health > 0:
                critical_count += 1
        return critical_count

    def _count_alive_humans(self):
        return len(
            [
                agent
                for agent in self.agents
                if isinstance(agent, Human) and agent.health > 0
            ]
        )

    def _count_recharging_robots(self):
        return len(
            [
                agent
                for agent in self.agents
                if isinstance(agent, Robot)
                and hasattr(agent, "is_recharging")
                and agent.is_recharging
            ]
        )

    def _count_working_robots(self):
        return len(
            [
                agent
                for agent in self.agents
                if isinstance(agent, Robot)
                and hasattr(agent, "current_task")
                and agent.current_task
                and not (hasattr(agent, "is_recharging") and agent.is_recharging)
            ]
        )

    def _count_idle_robots(self):
        return len(
            [
                agent
                for agent in self.agents
                if isinstance(agent, Robot)
                and not (hasattr(agent, "current_task") and agent.current_task)
                and not (hasattr(agent, "is_recharging") and agent.is_recharging)
                and (
                    not hasattr(agent, "_is_connected_to_network")
                    or agent._is_connected_to_network()
                )
            ]
        )

    def _count_searching_robots(self):
        count = 0
        for agent in self.agents:
            if isinstance(agent, Robot):
                try:
                    if (
                        not (hasattr(agent, "current_task") and agent.current_task)
                        and not (
                            hasattr(agent, "is_recharging") and agent.is_recharging
                        )
                        and hasattr(agent, "_is_connected_to_network")
                        and not agent._is_connected_to_network()
                    ):
                        count += 1
                except:
                    pass
        return count
