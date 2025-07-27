# Mars Laboratory Emergency Response ABM

An Agent-Based Model (ABM) simulating robot coordination and recruitment behaviors in emergency response worst case scenarios on Mars.

## Overview

This simulation explores how individual decision-making under uncertainty, combined with local communication and environmental cues, can lead to efficient collective behaviors in resource acquisition and problem-solving. The scenario demonstrates emergent coordination in distributed systems where autonomous agents must solve complex, multi-faceted problems without central control - a critical capability for future Mars missions where Earth-based support is impossible.

---
## Simulation Scenario

**The Crisis**: A catastrophic breach occurs in a Mars research laboratory, causing cascading failures that take down both the life support systems and the robots' central coordination system. With no external help available, the robots must act autonomously using only their individual capabilities and local communication to prevent total mission failure.

**The Challenge**: The worst case scenario being simulated involves multiple simultaneous emergencies: habitat breaches threatening atmosphere integrity, power system failures, laboratory contamination, and injured researchers. Each emergency requires different combinations of specialized skills, but no single robot has all the capabilities needed. The robots must discover each other's abilities, form teams dynamically, and coordinate responses without any central command structure.

**The Stakes**: In the harsh Martian environment, every decision matters. Atmosphere loss means death in minutes. Power failure cascades into life support collapse. The robots have limited energy and communication capabilities, imperfect information, and must make life-or-death decisions under extreme time pressure while coordinating purely through local interactions.

### Crisis Timeline
1. T+0:00 (Initial Event): A defective battery cell in the habitat's backup power array short-circuits.
2. T+0:02 (Runaway & Explosion): The faulty cell initiates a violent thermal runaway, leading to an energetic, localized explosion within the internal power hub. This blast generates a significant concussive force, stunning or incapacitating any human crew in direct proximity.
3. T+0:05 (System Collapse & Widespread Incapacitation): The explosion immediately triggers a critical arc fault within the internal power hub, causing a complete power system blackout across the habitat and severing connection to external power. The Central Control System (CCS) suffers catastrophic failure from the arc fault's electromagnetic pulse (EMP) and physical shock. All central control ceases instantly and without warning, forcing robots into autonomous, local-only operations. Due to the concussive force and rapid onset of atmospheric degradation (from failed life support and potential toxic fumes from ruptured containers), all human crew members are rendered unconscious or severely incapacitated.
4. T+0:07 (Life Support Compromise & Contamination Escalation): Internal power disruption fully impacts atmospheric processing, leading to the collapse of oxygen generation, CO2 scrubbing, and air recirculation. Debris from the explosion breaches a critical habitat seal, initiating atmosphere loss. Nearby experimental containment vessels rupture due to shockwave, releasing and spreading hazardous contaminants throughout the lab.
5. T+0:10 onwards (Critical Phase): Atmosphere loss escalates, and the habitat becomes untenable within minutes. Robots must coordinate urgent repairs, medical aid for the incapacitated crew, and contaminant containment using only local information and dynamic team formations to prevent total mission failure, all while their limited energy reserves deplete.

---
## Environment Setup

- The Habitat Module(s): Pressurized, sealed environment protecting crew from Mars' harsh conditions. Includes multiple interconnected sections (living, lab, medical).
- Human Crew/Researchers: Small team of specialized scientists and engineers. Vulnerable to habitat failures, contamination, and injury.
- Life Support System (LSS): Critical for human survival, managing atmosphere (O2, CO2, circulation), temperature, and water. Highly dependent on stable power.
- Power System: External Primary Solar Power feeds power into the base. Internal Distribution Hub & Backup Batteries regulate power within the habitat, providing critical UPS to internal systems.
- Central Control System (CCS): Primary server and software for habitat system monitoring and management. Vulnerable to power fluctuations, EMP, and physical damage.
- Laboratory Facilities & Equipment: Specialized modules for scientific research. Contains sensitive instruments, hazardous chemicals, and potentially biological samples.
- Communication Systems: Local wireless/wired network for habitat systems. External Communication Link with Earth and orbiting assets, subject to light-speed delay.

---
## Robot Agents
The simulation features 9 specialized robot types, each with unique capabilities and associated energy costs. 

All robots possess fundamental capabilities such as basic navigation, local communication, knowledge base cache (layouts, inventory management), environmental scanning and self-diagnosis, which are dependent on the type of environment the robot is designed for.
Each robot type also has a defined **Operating Environment**:
- **Internal**: Designed exclusively for operation within the pressurized, controlled habitat. Cannot operate externally.
- **External**: Designed exclusively for operation in the harsh Martian exterior environment. Cannot operate internally.
- **Mixed**: Designed to operate in both internal and external environments, capable of transitioning via airlocks.

### General capabilities
Habilities that all robots have but differ in how good or bad they can perform them, and how much battery they consume.
- **Heavy Lifting**: The ability to lift and move large or heavy objects.
- **Precision Assembly**: The ability to assemble components with high precision and delicate handling, and perform small-scale mechanical fixes.
- **Emergency First Aid**: The ability to administer basic emergency medical treatment to humans.
- **Cargo Transport**: The ability to efficiently move and transport cargo.
- **Debris Removal**: The ability to push lighter debris, break down larger, non-liftable obstructions.

### Special skills
Capabilities that require specialized equipement, and a robot either have or doesn't have.
- **Contamination Analysis**: The ability to detect and identify hazardous contaminants.
- **Vitals Monitoring**: The ability to monitor the vital signs of living beings and diagnose medical conditions in humans.
- **Life Support System Maintenance**: The ability to diagnose issues within life support systems and maintain them.
- **Environmental Decontamination**: The ability to clean and neutralize environmental contaminants.
- **Power System Repair**: Specific skills for diagnosing and repairing electrical power grids and manage battery systems.
- **Atmospheric Sealing**: The ability to seal breaches in the habitat's atmosphere.
- **Additive Manufacturing**: The ability to create new components using 3D printing.
- **Radiation Source Containment**: The ability to safely manage sources of radiation.
- **Structural Assembly**: The ability to construct and perform robust repairs on large habitat components.
- **Fire Suppression**: The ability to detect, assess, and neutralize fire hazards through chemical agents, inert gas dispersal, or isolation tactics. 

#### Bio-Lab Robots
Specializing in experimental assistance, human well-being, life support diagnostics, and detailed environmental/biological monitoring.
**Operating Environment:** Internal
Main Capabilities:
- Emergency First Aid
- Precission Assembly
Special skills:
- Contamination Analysis
- Vitals Monitoring

#### Hazmat Robots
Specialized in handling hazardous materials and environments.
**Operating Environment:** Internal
Main capabilities:
- Debris Removal
Special skills:
- Contamination Analysis
- Environmental Decontamination
- Radiation Source Containment

#### Maintenance Robots
Focused on general upkeep and life support systems upkeep.
**Operating Environment:** Internal
Main Capabilities:
- Precision Assembly
- Debris Removal
Special skills:
- Life Support System Maintenance
- Fire Suppression

#### Construction Robots
Designed for heavy structural work and debris management, primarily for **external habitat components and environments**.
**Operating Environment:** External
Main Capabilities:
- Heavy Lifting
- Debris Removal
Special skills:
- Structural Assembly

#### Power Systems Robots
Dedicated to electrical infrastructure and energy management.
**Operating Environment:** Internal
Main Capabilities:
- Precision Assembly
- Heavy Lifting
Special skills:
- Power System Repair

#### EVA Specialist Robots
Equipped for extra-vehicular activities and external habitat integrity, acting as general-purpose external operators.
**Operating Environment:** Mixed
Main Capabilities:
- Precision Assembly
- Cargo Transport
- Debris Removal
Special skills:
- Atmospheric Sealing

#### External Repair Robots
Specialized in diagnosing and repairing external systems, especially those damaged by environmental hazards or explosions.
**Operating Environment:** External
Main Capabilities:
- Precision Assembly
- Cargo Transport
- Heavy Lifting
Special skills:
- Atmospheric Sealing
- Power System Repair

#### Logistics Robots
Optimized for efficient movement and management of resources.
**Operating Environment:** Internal
Main Capabilities:
- Cargo Transport
- Heavy Lifting

#### Fabrication Robots
Capable of on-demand manufacturing and assembly.
**Operating Environment:** Internal
Main Capabilities:
- Precision Assembly
Special skills:
- Additive Manufacturing

### Intelligent Behaviors

**Autonomous Decision-Making:**
- **Task Leadership Evaluation**: Robots assess leadership potential based on capability match (40%), urgency (30%), proximity (20%), and energy level (10%)
- **Team Formation**: Leaders recruit team members through capability gap analysis and invitation-acceptance protocols
- **Dynamic Recruitment**: Robots send recruitment messages with task details, energy estimates, and team requirements
- **Invitation Processing**: Candidates evaluate invitations using benefit/cost analysis and urgency thresholds 

**Coordination Mechanisms:**
- **Local Information Sharing**: Robots discover nearby entities within communication range and update knowledge bases
- **Capability Matching**: Multi-factor scoring system considering skill level, reliability, and energy costs
- **Team Optimization**: Prioritizes candidates who fill capability gaps, then adds support members
- **Graceful Degradation**: System continues operating even if individual robots fail or become unavailable

**Adaptive Behaviors:**
- **Energy Management**: Robots monitor energy levels and factor consumption into decision-making
- **Urgency Response**: Higher urgency tasks trigger expanded search ranges and lower recruitment thresholds
- **Progress Tracking**: Teams monitor task completion using bottleneck analysis (weakest capability determines progress)
- **Resource Allocation**: Energy consumption scales with capability usage and task complexity

#### Recruitment Dynamics

The simulation implements a sophisticated multi-stage recruitment system:

**1. Leadership Assessment**
- Robots evaluate tasks using weighted scoring: capability match (40%), urgency (30%), distance (20%), energy (10%)
- Leadership threshold of 0.5 required to initiate team formation
- Available robots compete for leadership based on their assessment scores

**2. Candidate Discovery**
- Search within communication range
- Identify robots with complementary capabilities
- Lower recruitment thresholds (0.6 → 0.3) for unique capabilities or urgent tasks

**3. Invitation Protocol**
- Leaders send structured recruitment messages including task details, energy estimates, and team requirements
- Messages contain urgency level, estimated duration, and required capability levels
- Candidates receive invitations in their pending queue for processing

**4. Decision Framework**
- Candidates evaluate invitations using benefit/cost analysis
- Benefit factors: capability utilization (50%), urgency (30%), team collaboration (20%)
- Cost factors: energy expenditure (40%), travel distance (30%), time commitment (30%)
- Acceptance probability based on benefit/cost ratio and urgency threshold

**5. Team Assembly**
- Priority given to robots that fill capability gaps in required skills
- Secondary recruitment for support roles once core capabilities are covered
- Team size limited by task requirements (typically 2-4 robots)
- Failed recruitments trigger alternative candidate selection

---
## Simulation Constraints

### Physical Environment
- **Facility Layout**: grid with distinct zones
- **Communication Range**: Wireless conection limited to 10 grid units
- **Energy Management**: Robots start with 100 energy units, drain 0.5 per step, consume energy for actions
- **Spatial Positioning**: Manhattan distance calculations for movement and task assignment
- **Obstruction Zones**: Explosions or structural failures generate debris in nearby tiles, blocking movement or access. Robots must remove debris before performing any other actions in affected areas.

### Mission-Critical Systems
- **Crew Vital Status**: Each human crew member has a health score (0–100). Unconscious researchers degrade at 1% per step if untreated; critical threshold is 30%. Death occurs at 0%. Robots can stabilize vitals using Emergency First Aid and Vitals Monitoring.
- **Atmosphere Integrity**: Starts at 100%, degrades with unresolved habitat breaches (0.3% per step)
- **Power Level**: Starts at 100%, degrades with power failures (0.5% per step)
- **Contamination Level**: Starts at 0%, increases with unresolved contamination events
- **System Failure Threshold**: Mission fails if atmosphere or power drops to 0%

### Uncertainty Elements
**Information Constraints:**
- **Limited Awareness**: Robots only know about entities within communication range
- **Incomplete Knowledge**: Robots maintain knowledge bases of nearby robots, supplies and tasks but lack global situational awareness
- **Capability Discovery**: Robot capabilities are learned through interaction rather than centrally broadcast
- **Dynamic Information**: Knowledge becomes stale as robots move and situations change

**Environmental Unpredictability:**
- **Stochastic Emergencies**: New emergencies appear with 5% probability per simulation step
- **Variable Task Complexity**: Emergency difficulty ranges from 0.5-0.8, affecting completion time and resource requirements
- **Random Positioning**: Initial robot placement and emergency locations are randomized
- **Cascading Failures**: Unresolved emergencies cause progressive system degradation

**Resource and Performance Variability:**
- **Energy Uncertainty**: Robots don't know others' exact energy levels, affecting recruitment decisions
- **Capability Reliability**: Each capability has a reliability factor (0.8-0.95) introducing performance variance
- **Team Coordination**: Actual team effectiveness depends on capability coverage and coordination efficiency
- **Communication Failures**: Graceful degradation when robots fail to update or communicate properly

### Emergency Scenarios
On top of the main catastrophic event described in the Simulation Scenario, the simulation will include different emergency sub-types that can occur throughout the mission:
- **Habitat Breach**: Atmosphere leaks requiring environmental scanning, structural repair, and life support assessment
- **Power Failure**: Critical system failures needing electrical repair, battery management, and facility knowledge
- **Radiation Leak**: Contamination requiring radiation shielding, protective protocols, and contamination detection
- **Electrical Fire**: Fires needing chemical neutralization, electrical repair, and filter replacement
- **Lab Contamination**: Chemical/biological hazards requiring contamination detection, assessment, and debris clearing
- **Critical Researcher's conditions**: Medical emergencies needing diagnosis, treatment, and vital monitoring
- **External Damage**: Hull breaches requiring external repair, airlock operations, and structural repair
- **Equipment Malfunction**: System failures needing 3D printing, component assembly, and minor repairs
- **Supply Shortage**: Resource depletion requiring cargo transport, inventory management, and route optimization

---
## Simulation Outcomes

### Mission Failure Conditions
The simulation ends in failure if **any** of the following critical thresholds are reached:
- **Atmosphere Integrity** reaches 0%: The habitat becomes uninhabitable and all human life support is lost.
- **Power Level** reaches 0%: Life support, communications, and robotic operations permanently shut down.
- **All Human Crew Members Die**: If every researcher’s health reaches 0%, the mission is considered a total loss.

### Successful Mission Criteria
A mission is considered successful if all the following conditions are met by the end of the simulation:
- At least three **human crew member survive**
- **Atmosphere Integrity** and **Power Level** remain above 0%
- All **triggered emergencies** are resolved within their time limits
- **Contamination level** remains below critical threshold

### Partial Success
The simulation may be considered a **partial success** if:
- Less thatn three human **crew members survive**
- **Atmosphere Integrity** or **Power Level** drop below 25%, but never reach 0%
- Some **triggered emergencies** are resolved late, but cascading failure is avoided

---
## Usage

### Dependencies
```bash
pip install -r requirements.txt
```

### Running the simulation
```bash
python -m mars_abm
```

#### Optimization Modes

##### A. Budget-Constrained Mode
- Set a robot configuration, find the outcome
- Maximizes mission survival probability within budget constraints

##### B. Requirement-Based Mode
- Set mission requirements, find the minimum fleet needed
- Finds the most cost-effective fleet to meet survival requirements

#### Parameters Configuration

The tool will interactively prompt you for:

**Budget-Constrained Mode:**
- **Robot Configuration**: Total number of robots (for each type) available for the mission
- **Analysis Mode**: Quick analysis (fewer emergency scenarios) or comprehensive analysis

**Requirement-Based Mode:**
- **Maximum Budget**: Upper limit for robot budget consideration
- **Emergency Frequency**: Probability of emergencies per simulation step

#### Output Files

All reports and charts are automatically saved to the `reports/` directory:
- **Detailed Reports**: Complete simulation logs and analysis results
- **Visualization Charts**: Comprehensive performance charts
