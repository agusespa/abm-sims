# Mars Crisis Emergency Response ABM

An Agent-Based Model (ABM) simulating robot coordination and recruitment behaviors in emergency response worst case scenarios on Mars.

## Overview

This simulation explores how robots' individual decision-making under uncertainty, localized communication and limited environmental cues, can lead to efficient collective behaviors in resource acquisition and problem-solving. 
The scenario provides the grounds for emergent behabiors where autonomous agents must solve complex, multi-faceted problems without central control.

### Strategies
**The Goal** is to determine the best system for robot fleet self management (without a central coordination system).
It will implement two heuristics-based strategies that will serve as base cases for comparison purposes:
- individual task management with circumstantial collaboration,
- coordinated group management (to be implemented later).
Finally, it will implement an RL system to discover more optimal systems.

---
## Simulation Scenario

**The Crisis**: A catastrophic sysmic event occurs in a Mars research complex, causing cascading failures that take down both the life support systems and the robots' central coordination system. With no external help available, the robots must act autonomously using only their individual capabilities and local communication to prevent total mission failure.

**The Challenge**: The worst case scenario being simulated involves multiple simultaneous emergencies: habitat breaches threatening atmosphere integrity, power system failures, laboratory contamination, and injured crew members. Each emergency requires different combinations of specialized capabilities, but no single robot has all the capabilities needed. The robots must discover each other's abilities, form teams dynamically, and coordinate responses without any central command structure.

**The Objective**: Robots must guarantee systems' stability and get communications back online.

### Crisis Timeline:
T+0:00 (Initial Event): Major marsquake strikes. Solar array damaged. Internal power grid destabilizes. Central Control System suffers catastrophic hardware failure.
T+0:01 (System Collapse): Multiple habitat breaches cause rapid depressurization. Critical power blackout and surges spread. Labs rupture, releasing contaminants.
T+0:02 (Crew Incapacitation): Atmosphere loss, toxins, falling debris, and lack of life support incapacitate or trap all human crew members across the base.
T+0:03 onwards (Critical Phase): Fire starts in the power hub and quickly expands.

### Termination Crireria
The simulation is consider completed when systems are stabilized and communications are re-established.
The simulation ends prematurely if any of the critical metrics falls to an unrecoverable level.

---
## Environment Setup
### Planetary Environment

### Base Infrastructure
- Habitat Module(s): various rooms and connecting corridors.
- Laboratory Facilities: area for research and hazardous materials storage.
- Control module: life support systems, central control system, communication system. Internal robots chargers.
- Power Distribution and Battery Backup Module
- Power Station
- Storage & Supplies: Deposit for spare parts, tools, and construction materials. External robots chargers.

### Equipement
- Central comminications system (1)
- Power distribution hub (>=1)
- Battery pack (>=4)
- Hazardous materials storage (>=2)

### Agents
- Human Crew: Small team of specialized scientists and engineers. Vulnerable to habitat failures, contamination, and injury.
- Robot Agents

---
## Robot Agents

The simulation features specialized robot types, each with unique capabilities. All robots possess fundamental capabilities such as basic navigation, local communication, knowledge base (layouts, inventory management), environmental scanning, and self-diagnosis.
Each special (non-fundamental) capability has a reliability factor (0.8-0.95).

Each robot type also has a defined **Operating Environment**:
- **Internal**: Designed exclusively for operation within the pressurized, controlled habitat. Cannot operate externally.
- **External**: Designed exclusively for operation in the harsh Martian exterior environment. Cannot operate internally.
- **Mixed**: Designed to operate in both internal and external environments, capable of transitioning via airlocks.

### Internal Systems
#### Energy Management
Robots start with 60 energy units, which drain at a rate of 0.5 per step.
Robots recharge their batteries by staying idle in the Deposit (for external or mixed robots) and the Power Module (for internal robots).

#### Knowledge Base
Robots keep data about themselves:
- Position: grid coordinates
- Battery level
- Status: idle | charging | working
- Capabilities
Robots keep data about threats:
- Type: capability used (e.g. "wall-ext_detect")
- Position: grid coordinates
- Severity

### Local Communication Network
Robots form a wireless conection mesh, with a **Range** limited to 30 grid units.
Robots maintain a local cache of messages.
Robots rebroadcast newly received messages within range only once (simple flooding with limited spam).
#### Message Types
Robots can broadcast small, structured messages containing:
- Sender ID
- Sender Position
- Battery Level
- Current Task / Status
- Capability List
- Detected Threat (type, position, severity)
- Help Request (task type, urgency, position)

### Robot Archetypes and Emergency Response

#### Bio-Lab Robot
Specializing in experimental assistance, human well-being, life support diagnostics, and detailed environmental/biological monitoring.
**Operating Environment**: Internal
**Capabilities**: "first-aid", "hazard", "wall-int_detect"

#### Maintenance Robot
Focused on general upkeep and life support systems upkeep.
**Operating Environment**: Internal
**Capabilities**: "wall-int_detect", "wall-int", "fire", "power-int_detect", "power-int", "power-ext_detect", "control"

#### Construction Robot
Designed for heavy structural work and debris management, primarily for **external habitat components and environments**.
**Operating Environment**: External
**Capabilities**: "wall-ext", "power-ext"
**Reacts** to message types: "wall-ext_detect" and "power-ext_detect"

#### EVA Specialist Robot
Equipped for extra-vehicular activities and external habitat integrity, acting as general-purpose external operators.
**Operating Environment**: Mixed
**Capabilities**: "supplies", "fire-supplies"
**Reacts** to message types: "supplies" and "fire-supplies" requests

#### Logistics Robot
Equipped for extra-vehicular activities and external habitat integrity, acting as heavy-duty transporters.
**Operating Environment**: External
**Capabilities**: "materials"
**Reacts** to message types: "materials" requests

### Robot Strategies
#### Individual
Each robot, upon detecting a problem within its operating environment and based on its capabilities, will attempt to address it independently.
Robots will prioritize tasks for which they possess the direct "repair" or "cure" capability.
If a robot encounters a problem it cannot solve alone (lack of sufficient resources, or the problem's complexity requiring multiple robots), it will emit a call for help.
Robots receiving these help broadcasts will evaluate them against their own capabilities and current tasks, and then decide how to act.

#### Coordinated
(To be implemented later)

---
## Emergencies and Threat Management

### System Monitoring
The simulation tracks these mission critical variables and threats:
- **Crew Health** is calculated by the average of all the members, including the deceased ones.
- **Power Level** is calculated by the average of the integrities from the power walls, battery packs and power distribution hubs.
- **Atmospheric Condition** starts at 100 and decreases according to the different damages listed below.
- **Threat Tracking**: real-time monitoring of the amount of damaged walls, equipment failures, active fires, and critical human conditions.

### Damage and Repair
There are three stages:
- **Detection**: the existence of a threat somwhere is detected
- **Assesment**: the location and status is diagnosed
- **Repair**: the threat is mitigated

#### Crew Member's Health
Health deterioration rate is 1, and 1/5 if the human is conscious. A human remains conscious if their health is >= 60.
If their condition falls below 30 they need to be treated in the medical bay. Two first-aid capable robots are needed for transportation.
If the condition falls below 15, it can't be cured, only prevented from getting worse by continuous aid. Death occurs at 0.
**Capabilities** required:
- **Assessment**: visual confirmation by robot with "first-aid" capability
- **Repair**: "first-aid" capability

#### General Structural Damage
If the integrity of a structural agent (walls or equipement) falls below 15, it can't be recovered, only prevented from getting worse by continuous repair.
The general rate of deterioration follows this equation: 2.5 / integrity.
The general rate of repair = 25 / integrity.

#### Walls
To repair the interior of a wall, a robot needs spare parts. To repair the exterior of a wall, a robot needs materials. Materials and spare parts need to be fetched from the deposit, and 1 trip will give enough supplies for 25 integrity points.
If a wall has internal or external integrity below 20, the adjacent walls will get 69 integrity and start to deteriorate.
If the internal or external integrity falls bellow 50, its counterpart will get 69 integrity and start to deteriorate.
**Capabilities** required: 
- **Detection**: "wall-int_detect" or "wall-ext_detect" capabilities
- **Assessment**: visual confirmation by robot with "wall-int" or "wall-ext" capabilities
- **Repair**: "wall-int" with support from "supplies" and "wall-ext" with support from "materials"
**Consequences**: **atmospheric condition** decreases by the sum of all wall integrity values (taking the one, internal or external, that is highest) difference from 100 and then divided by 100.

#### Fire
If there is a fire in an equipement or a wall, it will spread to adjacent equipement or walls when the fire intensity is >= 70.
When the equipement or wall catch fire, their integrity gets at 69 and start deteriorating at the default rate * 2.
When there is a fire, the fire alarm is immediately triggered unless there is no power.
The maintenance robots carry enough extinguisher powder to reduce fire intensity by 200. When depleated, the robot's tank will need to be replentished from the deposit, which takes 1 trip.
**Capabilities** required: 
- **Detection**: all internal and mixed environment robots can sense the alarm
- **Assessment**: visual confirmation by robot with "fire" capability
- **Repair**: "fire" capability, with support from "fire-supplies"
**Consequences**: **atmospheric condition** decreases by the sum of all the fires strength values divided by 100.

#### Power walls
To repair a power-wall, a robot needs materials. Materials need to be fetched from the deposit, and 1 trip will give enough supplies for 25 integrity points.
If a power_wall integrity falls below 20, adjacent walls will start deteriorating too.  
**Capabilities** required: 
- **Detection**: "power-ext_detect"
- **Assessment**: "power-ext" 
- **Repair**: "power-ext" with support from "materials"
**Consequences**: see **power level** calculation in Emercency Metrics.

#### Batteries
If the integrity of a battery falls below 30, it turns on fire.
**Capabilities** required: 
- **Detection**: "power-int_detect" capability
- **Assessment**: visual confirmation by robot with "power-int" capability
- **Repair**: "power-int" capability
**Consequences**: see **power level** calculation in Emercency Metrics.

#### Power Distributon Hub
**Capabilities** required:
- **Detection**: "power-int_detect" capability
- **Assessment**: visual confirmation by robot with "power-int" capability
- **Repair**: "power-int" capability
**Consequences**: see **power level** calculation in Emercency Metrics.

#### Central comminications system
To get back on-line, the com system integrity needs to be over 70.
**Capabilities** required:
- **Detection**: "control" capability
- **Assessment**: visual confirmation by robot with "control" capability
- **Repair**: "control" capability

#### Hazardous materials storage
**Capabilities** required:
- **Detection**: "hazard" capability
- **Assessment**: visual confirmation by robot with "hazard" capability
- **Repair**: "hazard" capability
**Consequences**: **atmospheric condition** and **crew member's health** decreases by the sum of all integrity values divided by 100.

---
## Usage

### Requirements

```bash
pip install -r requirements.txt
```

#### Running the CLI
```bash
python -m mars_crisis_abm
```

### Running the Visualization
```bash
solara run app.py
```

Then open your browser to: http://localhost:8765

### Visualization Features

- **Interactive Grid**: Shows robots moving and responding to emergencies
- **Real-time Charts**: 
  - System status (Atmosphere, Power, Contamination)
  - Emergency response progress
  - Robot fleet status
- **Robot Visualization**:
  - Different colors for each robot type
  - Size indicates status (team leaders are larger, low energy robots are smaller)
  - Red color override for low-energy robots

### Robot Types and Colors

- **BioLabRobot**: Red (Medical)
- **MaintenanceRobot**: Blue (Maintenance)
- **ConstructionRobot**: Yellow (Construction)
- **PowerSystemsRobot**: Cyan (Power)
- **EVASpecialistRobot**: Magenta (EVA)
- **ExternalRepairRobot**: Silver (External Repair)
- **LogisticsRobot**: Gray (Logistics)
- **FabricationRobot**: Maroon (Fabrication)

### Controls

- **Play/Pause**: Control simulation execution
- **Step**: Advance one simulation step
- **Reset**: Restart the simulation
- **Speed**: Adjust simulation speed (500ms default interval)

### Optimization Modes

#### A. Budget-Constrained Mode
- Set a robot configuration, find the outcome
- Maximizes mission survival probability within budget constraints

#### B. Requirement-Based Mode
- Set mission requirements, find the minimum fleet needed
- Finds the most cost-effective fleet to meet survival requirements
