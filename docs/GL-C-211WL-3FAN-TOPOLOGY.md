# GL-C-211WL three-fan topology

## Decision

The three P12 Pro PST fans are arranged as a **servo-routed 2+1 topology**.

- **Supply bank:** fan_1 + fan_2 in parallel airflow
- **Exhaust bank:** fan_3
- **Routing:** one logical MZ966 actuator moves a mechanically coupled double-diverter
- fan rotation direction stays fixed
- room assignment changes mechanically during pendulum dead-time

This resolves the previous mismatch between three physical fans and four logical room/direction roles.

## Airflow graph

### PHASE_A

```text
OUTSIDE IN
   |
   +--> fan_1 --+
   |            |
   +--> fan_2 --+--> SUPPLY PLENUM --> coupled diverter --> ROOM A

ROOM B --> coupled diverter --> EXHAUST PLENUM --> fan_3 --> OUTSIDE OUT
```

Logical roles:

- room A = SUPPLY
- room B = EXHAUST

### DEADTIME_TO_B

```text
fan_1 = OFF
fan_2 = OFF
fan_3 = OFF

servo moves coupled diverter from position A to position B
```

### PHASE_B

```text
OUTSIDE IN
   |
   +--> fan_1 --+
   |            |
   +--> fan_2 --+--> SUPPLY PLENUM --> coupled diverter --> ROOM B

ROOM A --> coupled diverter --> EXHAUST PLENUM --> fan_3 --> OUTSIDE OUT
```

Logical roles:

- room A = EXHAUST
- room B = SUPPLY

### DEADTIME_TO_A

All fans are OFF while the diverter returns to position A.

## Why not one three-fan common air bank?

The pendulum cycle requires **simultaneous opposite air functions** in every active phase:

- one room receives outside air,
- the other room exhausts to outside.

Putting all three fans into one common undivided air path would collapse those two functions into one pressure domain or require additional per-fan reversing valves. The 2+1 topology keeps supply and exhaust physically separated while still allowing the room assignment to be swapped by one coupled routing mechanism.

## Mechanical diverter requirement

The routing mechanism must behave like a double-pole, double-throw air switch.

Position A:

- supply plenum -> room A
- room B -> exhaust plenum

Position B:

- supply plenum -> room B
- room A -> exhaust plenum

Requirements:

- supply and exhaust passages remain sealed from one another,
- no fan operation while the mechanism is between positions,
- positive mechanical stops,
- low leakage at both end positions,
- service/manual position should be possible,
- condensate paths must not be blocked by the diverter.

A single MZ966 may move both dampers through a linkage. If the torque or geometry requires two servos, the existing 6 V / 3 A rail rule remains: move servos sequentially until measured current proves simultaneous motion is safe.

## Electrical fan principle

All P12 fans receive continuous 12 V power from the LPV-35-12.

Do **not** speed-control a 4-pin P12 by chopping its 12 V supply.

Preferred electrical structure:

```text
Mean Well LPV-35-12
12 V / 3 A
   |
   +--> P12 fan_1 +12 V
   +--> P12 fan_2 +12 V
   +--> P12 fan_3 +12 V
   |
   +--> GL-C-211WL
           |
           +--> supply-bank PWM/open-drain -> fan_1 PWM
           |                              +-> fan_2 PWM
           |
           +--> exhaust-bank PWM/open-drain -> fan_3 PWM
           |
           +--> servo signal -> MZ966
```

### PWM parallelization

fan_1 and fan_2 always belong to the same supply bank and therefore receive the same logical PWM demand. Their PWM inputs are candidates for one shared open-drain signal.

That physical parallel connection is **not frozen yet**.

Bench validation must confirm:

- combined PWM-input pull-up current is within the open-drain sink capability,
- duty/frequency remains correct with two fan inputs attached,
- both fans reach OFF correctly,
- boot/reset does not create an unintended run command.

fan_3 remains a separate PWM group so supply and exhaust airflow can be balanced independently.

## Current-capacity check

Three P12 Pro PST fans at approximately 0.33 A nominal each require about:

- 0.99 A fan current
- 11.9 W at 12 V

The full PSU budget must also include:

- GL-C-211WL consumption,
- LK1263 conversion losses,
- MZ966 movement/stall current reflected to the 12 V side,
- wiring loss,
- startup/transient margin.

## Software mapping

The control core continues to expose four logical roles:

- room_a_supply
- room_a_exhaust
- room_b_supply
- room_b_exhaust

The hardware layer maps them by **fan group + servo route**, not by assigning one physical fan to two directions.

```yaml
topology: servo_routed_2plus1

fan_groups:
  supply_bank:
    members: [fan_1, fan_2]
  exhaust_bank:
    members: [fan_3]

logical_role_mapping:
  room_a_supply: supply_bank
  room_b_supply: supply_bank
  room_a_exhaust: exhaust_bank
  room_b_exhaust: exhaust_bank

routing:
  PHASE_A: ROOM_A_SUPPLY_ROOM_B_EXHAUST
  PHASE_B: ROOM_B_SUPPLY_ROOM_A_EXHAUST
```

During dead-time the target route is changed while all fan targets remain zero.

The adapter must reject a command when active logical roles disagree with the selected route.

## Servo timing interlock

The production dead-time must be at least:

```text
measured servo travel time
+ mechanical settling margin
+ optional position-confirmation margin
```

Until end-position feedback is added, use a conservative measured timing value.

The safe transition is always:

```text
fans OFF
  -> move servo
  -> wait until route is stable
  -> enable supply/exhaust fan groups
```

## Bench work

- [ ] confirm physical 2+1 plenum/diverter layout on paper/CAD
- [ ] check that supply/exhaust passages never short-circuit
- [ ] measure MZ966 travel time under real damper load
- [ ] measure MZ966 movement/stall current at 6 V
- [ ] verify fan_1 + fan_2 shared PWM input electrically
- [ ] verify separate exhaust-bank PWM
- [ ] verify all fans OFF during servo motion
- [ ] measure supply-bank vs exhaust-bank airflow and derive calibration factors
- [ ] verify route A airflow direction
- [ ] verify route B airflow direction
- [ ] verify leakage in both diverter positions

## Gate

The logical mapping is now defined as **2+1 fan banks with servo routing**.

Final GPIO pin assignment, shared-PWM wiring, servo endpoints and production dead-time remain gated on bench measurements.
