# GL-C-211WL three-fan topology

## Decision

The three P12 Pro PST fans are arranged as a **servo-routed 2+1 topology**.

- **Supply bank:** fan_1 + fan_2 in parallel airflow
- **Exhaust bank:** fan_3
- **Routing:** one logical MZ966 actuator mechanically couples two physically separate full-area T-diverters (supply + exhaust)
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
   +--> fan_2 --+--> SUPPLY PLENUM --> SUPPLY T-DIVERTER --> ROOM A

ROOM B --> EXHAUST T-DIVERTER --> EXHAUST PLENUM --> fan_3 --> OUTSIDE OUT
```

Logical roles:

- room A = SUPPLY
- room B = EXHAUST

### DEADTIME_TO_B

```text
fan_1 = OFF
fan_2 = OFF
fan_3 = OFF

servo/linkage moves both isolated T-diverters from position A to position B
```

### PHASE_B

```text
OUTSIDE IN
   |
   +--> fan_1 --+
   |            |
   +--> fan_2 --+--> SUPPLY PLENUM --> SUPPLY T-DIVERTER --> ROOM B

ROOM A --> EXHAUST T-DIVERTER --> EXHAUST PLENUM --> fan_3 --> OUTSIDE OUT
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

Putting all three fans into one common undivided air path would collapse those two functions into one pressure domain or require additional per-fan reversing valves. The 2+1 topology keeps supply and exhaust physically separated. ROUTING-V0.3 implements that separation with two independent full-area T-diverter bodies whose shafts may be coupled to one MZ966.

## Mechanical diverter requirement

The preferred ROUTING-V0.3 mechanism uses **two physically separate full-area T-diverters**:

- supply_t_diverter: supply bank -> core A or core B,
- exhaust_t_diverter: core A or core B -> exhaust bank.

The two air bodies remain isolated. Their shafts may be mechanically coupled to one MZ966 by a single_servo_linkage.

Position A:

- supply T-diverter -> room/core A,
- room/core B -> exhaust T-diverter.

Position B:

- supply T-diverter -> room/core B,
- room/core A -> exhaust T-diverter.

Requirements:

- supply and exhaust bodies remain sealed from one another,
- no fan operation while either diverter is between stable positions,
- positive mechanical stops,
- low closed-branch and shaft leakage,
- service/manual position should be possible,
- condensate paths must not be blocked,
- both diverters must reach the complementary route without binding or one hard stop arriving prematurely.

### Why ROUTING-V0.2 was superseded

The monolithic side-by-side V0.2 double-diverter fit the Mega S but its branch opening was only 65 x 50 mm = **3250 mm²**.

For comparison:

- P12 112 mm aperture: about **9852 mm²**,
- current core open area: **10000 mm²**,
- V0.2 branch: only about **33 %** of fan/core area.

ROUTING-V0.3 uses **112 x 112 mm = 12544 mm²** ports, about 127 % of the P12 aperture and 125 % of the current core open area. V0.2 remains tracked as engineering evidence but is not the preferred full-size airflow prototype.

A single MZ966 may move both V0.3 shafts through linkage. If real torque/current shows that one servo is insufficient, the actuator architecture must be revisited from measured data rather than guessed.

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
  mechanism: coupled_dual_t_diverter
  coupling: single_servo_linkage
  mechanical_units:
    supply: supply_t_diverter
    exhaust: exhaust_t_diverter
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

- [x] define and CAD the preferred V0.3 dual full-area T-diverter layout
- [ ] bench-verify that the two isolated T-diverter bodies never cross-leak
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
